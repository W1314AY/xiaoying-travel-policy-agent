import json
import os
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "develope/src"))
import deepseek
import travel_qa as qa


def response(name, **params):
    call = {"type": "function", "id": "call_" + name, "function": {
        "name": name, "arguments": json.dumps(dict(reason="测试动作", **params))}}
    return {"choices": [{"message": {"tool_calls": [call], "reasoning_content": "PRIVATE_TEST"}}]}


class DeepSeekAdapter(unittest.TestCase):
    def test_one_lodging_question_requires_clarification(self):
        source = qa.read_document(self.docs, "D02")
        for fields in ({}, {"partial_items": {"answered": "住宿费", "unsupported": "目的地"}}):
            with self.subTest(fields=fields):
                replies = [response("read_document", doc_id="D02"),
                           response("finish", status="部分已回答", answer="需补充目的地。",
                                    gaps=["未提供目的地"], citations=[source], **fields),
                           response("ask_user", status="待确认", answer="请问本次目的地？",
                                    gaps=["目的地"], citations=[source])]
                with patch.object(deepseek, "completion", side_effect=replies):
                    t = self.ask("这趟出差住宿费上限是多少？")
                self.assertEqual(t["status"], "待确认")
                self.assertEqual(t["steps"][-1]["action"], "ask_user")
                self.assertIn("ask_user", t["steps"][1]["result_summary"]["message"])

    def test_lodging_and_breakfast_allows_partial(self):
        source = qa.read_document(self.docs, "D02")
        replies = [response("read_document", doc_id="D02"), response("search_documents", query="早餐"),
                   response("finish", status="部分已回答", answer="上海每人每晚最高 500 元，早餐费缺少依据。",
                            partial_items={"answered": "上海住宿上限", "unsupported": "早餐费"},
                            gaps=["缺少早餐费条款"], citations=[source])]
        with patch.object(deepseek, "completion", side_effect=replies):
            t = self.ask("上海住宿上限是多少，早餐费能单独报销吗？")
        self.assertEqual(t["status"], "部分已回答")
        self.assertEqual(t["citations"], [source])

    def test_batch_is_rejected_then_model_reads_one_at_a_time(self):
        self.docs.update(qa.load_documents(ROOT / "data/conflict.json"))
        batch = response("read_document", doc_id="D01")
        other = response("read_document", doc_id="D04")["choices"][0]["message"]["tool_calls"][0]
        other["id"] = "other_read"
        batch["choices"][0]["message"]["tool_calls"].append(other)
        sources = [qa.read_document(self.docs, k) for k in ("D01", "D04")]
        replies = iter([batch, response("read_document", doc_id="D01"),
                        response("read_document", doc_id="D04"),
                        response("ask_user", status="待确认", answer="请提供适用依据。",
                                 gaps=["优先级"], citations=sources)])
        def reply(messages):
            if len(messages) == 5:
                self.assertEqual([m["tool_call_id"] for m in messages[-2:]], ["call_read_document", "other_read"])
                self.assertTrue(all("invalid_arguments" in m["content"] for m in messages[-2:]))
            return next(replies)
        with patch.object(deepseek, "completion", reply):
            trace = self.ask()
        self.assertEqual(trace["status"], "待确认")
        self.assertEqual(trace["citations"], sources)
        self.assertEqual(trace["steps"][0]["arguments"]["count"], 2)
        self.assertEqual(len(trace["steps"]), 4)

    def test_empty_result_cannot_be_reported_as_tool_error(self):
        replies = [response("search_documents", query="早餐"),
                   response("finish", answer="无法核对", status="工具失败", gaps=["早餐"], citations=[]),
                   response("finish", answer="无对应制度", status="依据不足", gaps=["早餐"], citations=[])]
        with patch.object(deepseek, "completion", side_effect=replies):
            t = self.ask()
        self.assertEqual(t["status"], "依据不足")
        self.assertEqual(t["steps"][1]["result_summary"]["error"], "invalid_answer")

    def test_timeout_then_empty_retry_can_finish_as_tool_failure(self):
        replies = [response("search_documents", query="报销单"),
                   response("search_documents", query="费用申请"),
                   response("finish", answer="首次检索超时，换词后仍无依据。",
                            status="工具失败", gaps=["期限未核实"], citations=[])]
        with patch.object(deepseek, "completion", side_effect=replies):
            t = self.ask(first_search_timeout=True)
        self.assertEqual(t["status"], "工具失败")
        self.assertEqual(t["steps"][1]["result_summary"], {"candidate_ids": []})

    def setUp(self):
        self.docs = qa.load_documents(ROOT / "data/policies.json")

    def ask(self, question="差旅报销期限？", **options):
        return qa.answer_question(question, self.docs, model=deepseek.deepseek_turn, **options)

    def test_tool_roundtrip_and_timeout_observation(self):
        source = qa.read_document(self.docs, "D01")
        replies = [response("search_documents", query="报销期限"),
                   response("search_documents", query="报销期限"),
                   response("read_document", doc_id="D01"),
                   response("finish", answer=source["quote"], status="已回答", citations=[source], gaps=[])]
        requests = []

        def reply(payload, key):
            self.assertEqual(key, "unit-fixture")
            requests.append(json.loads(json.dumps(payload)))
            return replies.pop(0)

        with patch.dict(os.environ, DEEPSEEK_API_KEY="unit-fixture"), patch.object(deepseek, "post", reply):
            t = self.ask(first_search_timeout=True)
        self.assertEqual(t["citations"], [source])
        self.assertEqual(t["status"], "已回答")
        self.assertEqual(t["mode"], "deepseek")
        self.assertEqual(requests[0]["model"], "deepseek-flash")
        self.assertEqual(json.loads(requests[1]["messages"][-1]["content"])["error"], "search_timeout")
        self.assertEqual(requests[2]["messages"][-1]["tool_call_id"], "call_search_documents")
        self.assertEqual(json.loads(requests[2]["messages"][-1]["content"]), ["D01"])
        self.assertEqual(json.loads(requests[3]["messages"][-1]["content"]), source)
        self.assertNotIn("PRIVATE_TEST", str(requests) + str(t))
        self.assertNotIn("unit-fixture", str(t))

    def test_timeout_ends_turn(self):
        with patch.dict(os.environ, DEEPSEEK_API_KEY="unit-fixture"), patch.object(
                deepseek, "HTTPSConnection") as transport:
            transport.return_value.getresponse.side_effect = TimeoutError
            t = self.ask(first_search_timeout=True)
            transport.assert_called_once_with("api.deepseek.com", timeout=60)
        self.assertEqual(t["model_error"], {"code": "model_timeout", "at_decision": 1})
        self.assertEqual(t["status"], "模型请求失败")
        self.assertEqual(t["steps"], [])
        self.assertEqual(t["request_timeout_seconds"], 60)

    def test_missing_key_never_sends(self):
        with patch.dict(os.environ, DEEPSEEK_API_KEY=""), patch.object(deepseek, "post") as send:
            t = self.ask()
            send.assert_not_called()
        self.assertEqual(t["model_error"]["code"], "missing_key")
        self.assertEqual(t["steps"], [])

    def test_session_uses_previous_question_and_answer(self):
        ctx = {}
        with patch.object(deepseek, "completion", return_value=response(
                "ask_user", status="待确认", answer="目的地是哪里？", gaps=["目的地"], citations=[])):
            self.ask("住宿限额？", context=ctx)
        with patch.object(deepseek, "completion", return_value={}) as send:
            t = self.ask("上海", context=ctx)
        self.assertEqual([m["content"] for m in send.call_args.args[0][1:]],
                         ["住宿限额？", "目的地是哪里？", "上海"])
        self.assertEqual(t["model_error"]["code"], "model_response")
