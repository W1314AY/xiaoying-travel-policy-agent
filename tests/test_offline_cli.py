import json
import os
from pathlib import Path
import subprocess
import sys
from uuid import uuid4
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "develope/src/travel_qa.py"
DATA = ROOT / "data/policies.json"
DEADLINE = "国内出差返程后多久要提交报销单？"


class OfflineCLI(unittest.TestCase):
    def setUp(self):
        self.directory = ROOT / ".scratch" / ("cli-test-" + uuid4().hex)
        self.directory.mkdir(parents=True)
        self.addCleanup(self.clean_directory)

    def clean_directory(self):
        for file in self.directory.iterdir():
            file.unlink()
        self.directory.rmdir()

    def session(self, questions, *extra, interactive=False):
        env = dict(os.environ)
        env.pop("DEEPSEEK_API_KEY", None)
        run = subprocess.run(
            [sys.executable, "-X", "utf8", str(CLI), *([] if interactive else questions),
             "--trace-dir", str(self.directory), *extra],
            cwd=ROOT, env=env, capture_output=True, encoding="utf-8", timeout=10,
            input="\n".join([*questions, "退出"]) if interactive else None,
        )
        self.assertEqual(run.returncode, 0, run.stderr)
        paths = [Path(line.split("记录路径：", 1)[1]) for line in run.stdout.splitlines()
                 if "记录路径：" in line]
        traces = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
        self.assertEqual([t["question"] for t in traces], questions)
        self.assertEqual(len({t["session_id"] for t in traces}), 1)
        self.assertEqual([t["turn"] for t in traces], list(range(1, len(questions) + 1)))
        for trace in traces:
            reads = [s["result_summary"] for s in trace["steps"] if s["action"] == "read_document"]
            for citation in trace["citations"]:
                self.assertIn(citation, reads)
        return run.stdout, traces

    def ask(self, question, *extra):
        output, (trace,) = self.session([question], *extra)
        self.assertEqual(trace["mode"], "offline_mock")
        self.assertEqual(trace["question"], question)
        for field in ("状态：", "回答：", "资料缺口："):
            self.assertIn(field, output)
        return output, trace

    def test_interactive_commands_preserve_followup(self):
        lines = ["", "/", "/examples", "这趟出差住宿费上限是多少？", "/sources",
                 "/typo", "上海", "/exit", "不应处理这行"]
        run = subprocess.run(
            [sys.executable, "-X", "utf8", str(CLI), "--trace-dir", str(self.directory)],
            input="\n".join(lines), capture_output=True, encoding="utf-8", timeout=10, check=True)
        for hint in ("/help", "自行升至一等座怎么报销", "D02", "未知指令"):
            self.assertIn(hint, run.stdout)
        traces = [json.loads(f.read_text(encoding="utf-8")) for f in sorted(self.directory.glob("*.json"))]
        self.assertEqual([(t["turn"], t["question"], t["status"]) for t in traces],
                         [(1, lines[3], "待确认"), (2, "上海", "已回答")])

    def test_deadline_without_key(self):
        output, t = self.ask(DEADLINE)
        self.assertIn("返程次日起 30 个自然日内", output)
        self.assertIn("D01", output)
        self.assertIn("2026-09-01", output)
        self.assertEqual([s["action"] for s in t["steps"]],
                         ["search_documents", "read_document", "finish"])
        self.assertEqual(t["steps"][1]["arguments"], {"doc_id": "D01"})
        self.assertEqual(t["citations"][0]["quote"], t["answer"])
        self.assertEqual(t["status"], "已回答")

    def test_rail_seats(self):
        for question, detail in [("高铁二等座怎么报销？", "按实际票价报销"),
                                 ("自行升至一等座怎么报销？", "差额由本人承担")]:
            with self.subTest(question=question):
                out, t = self.ask(question)
                self.assertIn(detail, out)
                self.assertIn(detail, t["answer"])
                self.assertEqual(t["citations"][0]["doc_id"], "D03")
                if "一等座" in question:
                    self.assertIn("同车次、同区间二等座票价", t["answer"])

    def test_replacement_uses_read_text(self):
        original = DATA.read_bytes()
        docs = json.loads(original)
        d = next(d for d in docs if d["doc_id"] == "D01")
        d["text"] = "员工须自返程当日起 21 个自然日内提交差旅报销单。"
        d["version"] = "2026-10-15"
        copy = self.directory / "changed.json"
        copy.write_text(json.dumps(docs, ensure_ascii=False), encoding="utf-8")
        out, t = self.ask(DEADLINE, "--data", str(copy))
        self.assertEqual(t["answer"], d["text"])
        self.assertEqual(t["citations"], [{"doc_id": "D01", "version": d["version"],
                                          "quote": d["text"]}])
        self.assertIn(d["version"], out)
        self.assertNotIn("30 个自然日", out)
        self.assertEqual(DATA.read_bytes(), original)

    def test_no_match(self):
        _, t = self.ask("早餐费能单独报销吗？")
        self.assertEqual(t["status"], "依据不足")
        self.assertFalse(t["citations"])
        self.assertTrue(t["gaps"])


    def test_interactive_destination_and_restart(self):
        q = "这趟出差住宿费上限是多少？"
        _, (first, second) = self.session([q, "上海"], interactive=True)
        self.assertEqual(first["status"], "待确认")
        self.assertIn("目的地", first["answer"])
        self.assertEqual(second["status"], "已回答")
        self.assertIn("每人每晚上限为 500 元", second["answer"])
        self.assertIn("按实际住宿费用报销", second["answer"])
        self.assertEqual([s["doc_id"] for s in second["citations"]], ["D02"])
        files = {p: p.read_bytes() for p in self.directory.iterdir()}
        _, fresh = self.ask(q)
        self.assertNotEqual(fresh["session_id"], first["session_id"])
        self.assertEqual(fresh["status"], "待确认")
        self.assertEqual(fresh["context_before"], {})
        self.assertEqual(files, {p: p.read_bytes() for p in files})

    def test_context_in_earlier_statement(self):
        _, (_, result) = self.session(["我去杭州出差", "酒店上限是多少？"])
        self.assertIn("350 元", result["answer"])
        self.assertNotIn("500 元", result["answer"])

    def test_paraphrase_and_empty_first_search(self):
        for q, rewrite in [("出差回来最晚什么时候交单？", False),
                           ("出差结束后最迟几天递交费用申请？", True)]:
            with self.subTest(q=q):
                _, t = self.ask(q)
                self.assertEqual(t["status"], "已回答")
                self.assertEqual([s["doc_id"] for s in t["citations"]], ["D01"])
                self.assertIn("返程次日起 30 个自然日", t["answer"])
                searches = [s for s in t["steps"] if s["action"] == "search_documents"]
                self.assertEqual(searches[0]["arguments"]["query"], q)
                self.assertEqual(len(searches), 2 if rewrite else 1)
                if rewrite:
                    self.assertEqual(searches[0]["result_summary"]["candidate_ids"], [])
                    self.assertEqual(searches[1]["arguments"]["query"], "报销期限")

    def test_partly_answered(self):
        _, t = self.ask("上海住宿限额是多少，早餐费能单独报销吗？")
        self.assertEqual(t["status"], "部分已回答")
        self.assertEqual([s["doc_id"] for s in t["citations"]], ["D02"])
        self.assertIn("500 元", t["answer"])
        self.assertIn("早餐费", t["gaps"][0])
        self.assertEqual(t["steps"][-2]["result_summary"]["candidate_ids"], [])

    def test_conflict_rechecks_without_trusting_user_or_newest(self):
        _, normal = self.ask(DEADLINE)
        self.assertEqual(normal["status"], "已回答")
        self.assertIn("30 个自然日", normal["answer"])
        _, traces = self.session([DEADLINE, "以 D04 为准", "看「15 个自然日」"],
                                 "--extra-data", "data/conflict.json")
        for t in traces:
            self.assertEqual(t["status"], "待确认")
            self.assertEqual([s["doc_id"] for s in t["citations"]], ["D01", "D04"])
            self.assertIn("30 个自然日", t["citations"][0]["quote"])
            self.assertIn("15 个自然日", t["citations"][1]["quote"])
            self.assertIn("替代关系", t["gaps"][0])
        self.assertEqual(traces[-1]["steps"][1]["result_summary"]["candidate_ids"], ["D04"])

    def test_verified_local_precedence(self):
        for q in ["请查 D05", "看「以下替代关系」"]:
            with self.subTest(q=q):
                _, (first, second) = self.session([DEADLINE, q], "--extra-data", "data/conflict.json",
                                                  "--extra-data", "tests/fixtures/precedence.json")
                self.assertEqual(first["status"], "待确认")
                self.assertEqual(second["status"], "已回答")
                self.assertIn("按 D04 执行", second["answer"])
                self.assertIn("15 个自然日", second["answer"])
                self.assertEqual([s["doc_id"] for s in second["citations"]],
                                 ["D01", "D04", "D05"])
