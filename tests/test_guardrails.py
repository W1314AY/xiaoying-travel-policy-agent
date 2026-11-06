"""任务 03：可控 Mock 只提供动作，所有工具、校验、计数及 Trace 均由 CLI 的执行器处理。"""
import argparse
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "develope/src"))
import travel_qa as qa

QUESTION = "国内出差返程后多久要提交报销单？"
SEARCH = ("search_documents", {"query": QUESTION}, "查找报销期限。")
READ = ("read_document", {"doc_id": "D01"}, "读取期限条款。")
MISSING = ("read_document", {}, "测试注入：读文档时漏传 ID。")
TRACE_DIR = None


def finish(source):
    return ("finish", {"status": "已回答", "answer": source["quote"], "citations": [source],
                       "gaps": []}, "提交条款及引用以供校验。")


class Guardrails(unittest.TestCase):
    def setUp(self):
        self.docs = qa.load_documents(ROOT / "data/policies.json")

    def check(self, name, model, status, count, *, question=QUESTION, **options):
        trace = qa.answer_question(question, self.docs, model=model, **options)
        self.assertEqual(trace["status"], status)
        steps = trace["steps"]
        self.assertEqual([s["step"] for s in steps], list(range(1, count + 1)))
        self.assertEqual([s["next_action"] for s in steps],
                         [s["action"] for s in steps[1:]] + ["结束"])
        if status in ("未完成", "工具失败"):
            self.assertEqual(trace["citations"], [])
            self.assertTrue(trace["gaps"])
        if TRACE_DIR:
            path = TRACE_DIR / (name + ".json")
            with path.open("x", encoding="utf-8") as out:
                json.dump({"test_case": name, **trace}, out, ensure_ascii=False, indent=2)
                out.write("\n")
        return trace

    def test_first_timeout_and_retry(self):
        t = self.check("timeout-retry", qa.mock_turn, "已回答", 4, first_search_timeout=True)
        self.assertTrue(t["steps"][0]["result_summary"]["simulated"])
        self.assertEqual(t["steps"][1]["result_summary"], {"candidate_ids": ["D01"]})
        self.assertIn("返程次日起 30 个自然日", t["answer"])

    def test_timeout_then_stop(self):
        def model(*_):
            error = yield SEARCH
            self.assertEqual(error["error"], "search_timeout")
            yield "finish", qa.failure("工具失败", "检索超时，无法核实。"), "选择停止，本轮无法核对。"
            self.fail("不应再次请求模型")
        with patch.object(qa, "search_documents", wraps=qa.search_documents) as search:
            self.check("timeout-stop", model, "工具失败", 2, first_search_timeout=True)
            search.assert_not_called()

    def test_retry_fails(self):
        with patch.object(qa, "search_documents", side_effect=TimeoutError) as search:
            t = self.check("timeout-twice", qa.mock_turn, "工具失败", 2, first_search_timeout=True)
            search.assert_called_once()
            self.assertIn("重试", t["answer"])
            self.assertEqual([s["result_summary"]["error"] for s in t["steps"]], ["search_timeout"] * 2)

    def test_missing_parameter(self):
        for repair in (True, False):
            with self.subTest(repair=repair):
                def model(*_):
                    error = yield MISSING
                    self.assertEqual(error["error"], "invalid_arguments")
                    self.assertIn("doc_id", error["message"])
                    source = yield READ if repair else MISSING
                    if not repair:
                        self.fail("不得给第二次修正机会")
                    yield finish(source)
                with patch.object(qa, "read_document", wraps=qa.read_document) as read:
                    self.check("param-fixed" if repair else "param-rejected", model,
                               "已回答" if repair else "未完成", 3 if repair else 2)
                    self.assertEqual(read.call_count, int(repair))

    def test_citation_checks(self):
        for field, wrong in [("doc_id", "D02"), ("version", "2000-01-01"), ("quote", "报销期限 90 天。")]:
            for repair in (True, False):
                with self.subTest(field=field, repair=repair):
                    def model(*_):
                        source = yield READ
                        bad = dict(source, **{field: wrong})
                        error = yield finish(bad)
                        self.assertEqual(error["error"], "invalid_answer")
                        yield finish(source if repair else bad)
                        self.fail("不得再次请求模型")
                    name = "cite-" + field + ("-fixed" if repair else "-rejected")
                    t = self.check(name, model, "已回答" if repair else "未完成", 3)
                    if repair:
                        self.assertEqual(t["citations"], [t["steps"][0]["result_summary"]])
                    else:
                        self.assertNotIn("90 天", t["answer"])

    def test_eighth_tool_then_next_turn(self):
        def model(*_):
            for _ in range(7):
                yield SEARCH
            yield READ
            self.fail("不得发起第 9 次决策")
        context = {"city": "上海"}
        t = self.check("step8-read", model, "未完成", 8, context=context)
        self.assertEqual(t["steps"][7]["result_summary"]["doc_id"], "D01")
        self.assertIn("8", t["answer"])
        t = self.check("next-turn", qa.mock_turn, "已回答", 3, context=context, question="这次住宿限额？")
        self.assertEqual(t["context_before"]["city"], "上海")
        self.assertIn("500 元", t["answer"])

    def test_prior_turn_is_not_current_evidence(self):
        context = {}
        previous = self.check("prior-turn", qa.mock_turn, "已回答", 3, context=context)
        citation = previous["citations"][0]

        def model(*_):
            error = yield finish(citation)
            self.assertIn("本轮未读取", error["message"])
            source = yield READ
            yield finish(dict(source, quote="返程次日起 30 个自然日内"))
        t = self.check("reread-before-citing", model, "已回答", 3, context=context)
        self.assertEqual(t["citations"][0]["quote"], "返程次日起 30 个自然日内")

    def test_eighth_valid_answer(self):
        def model(*_):
            for _ in range(6):
                yield SEARCH
            source = yield READ
            yield finish(source)
            self.fail("不得发起第 9 次决策")
        t = self.check("step8-finish", model, "已回答", 8)
        self.assertEqual(t["steps"][-1]["action"], "finish")
        self.assertEqual(t["citations"], [t["steps"][-2]["result_summary"]])

    def test_no_room_for_correction(self):
        for kind in ("param", "cite"):
            with self.subTest(kind=kind):
                def model(*_):
                    source = yield READ
                    for _ in range(6):
                        yield SEARCH
                    yield MISSING if kind == "param" else finish(dict(source, quote="错误引文"))
                    self.fail("无剩余步数时不能修正")
                t = self.check("step8-" + kind, model, "未完成", 8)
                self.assertIn("8", t["answer"])
                self.assertIn("error", t["steps"][-1]["result_summary"])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("--trace-dir", type=Path, help="把各验收用例的实际记录写入新目录")
    opts, rest = parser.parse_known_args()
    TRACE_DIR = opts.trace_dir
    if TRACE_DIR:
        TRACE_DIR.mkdir(parents=True, exist_ok=False)
    unittest.main(argv=[sys.argv[0], *rest])
