"""经授权后显式运行六个 DeepSeek 场景，保留失败与首轮原始材料。"""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
Q = "国内出差返程后多久要提交报销单？"
CASES = [
    ("normal", [Q], [], ["已回答"], [{"D01"}]),
    ("timeout", [Q], ["--first-search-timeout"], [("已回答", "工具失败")], [set()]),
    ("conflict", [Q], ["--extra-data", "data/conflict.json"], ["待确认"], [{"D01", "D04"}]),
    ("outside", ["早餐费能单独报销吗？"], [], ["依据不足"], [set()]),
    ("similar", ["出差回来最晚什么时候交单？"], [], ["已回答"], [{"D01"}]),
    ("context", ["这趟出差住宿费上限是多少？", "上海"], [], ["待确认", "已回答"], [set(), {"D02"}]),
]


def inspect_turn(t, status, needed, case, docs):
    errors = []
    steps = t["steps"]
    if t["mode"] != "deepseek" or t["status"] not in ((status,) if isinstance(status, str) else status):
        errors.append("模式或状态不符合用例预期")
    if not 1 <= len(steps) <= 8:
        errors.append("有效动作数不在 1–8 之间")
    ids = set()
    reads = {s["arguments"]["doc_id"]: s["result_summary"] for s in steps
             if s["action"] == "read_document" and "quote" in s["result_summary"]}
    for c in t["citations"]:
        key = c["doc_id"]
        ids.add(key)
        if (key not in reads or key not in docs or c["version"] != docs[key]["version"]
                or c["version"] != reads[key]["version"] or not c["quote"].strip()
                or c["quote"] not in reads[key]["quote"] or c["quote"] not in docs[key]["text"]):
            errors.append("引用未与本轮读取和合成资料匹配")
    if not needed <= ids or (case == "timeout" and t["status"] == "已回答" and "D01" not in ids):
        errors.append("缺少预期文档引用")
    if case == "timeout" and not any(s["action"] == "search_documents"
            and s["result_summary"].get("error") == "search_timeout"
            and s["result_summary"].get("simulated") is True for s in steps):
        errors.append("未实际触发首次检索超时")
    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "examples/task04" / uuid4().hex)
    folder = parser.parse_args().output.resolve()
    folder.mkdir(parents=True, exist_ok=False)
    report = []
    for name, questions, flags, statuses, required in CASES:
        path = folder / name
        args = ["-X", "utf8", "-B", "develope/src/travel_qa.py", "--mode", "deepseek",
                *flags, "--trace-dir", str(path), *questions]
        run = subprocess.run([sys.executable, *args], cwd=ROOT, capture_output=True, encoding="utf-8")
        path.mkdir(exist_ok=True)
        (path / "terminal.txt").write_text(run.stdout + run.stderr, encoding="utf-8")
        docs = {}
        for file in ["data/policies.json"] + (["data/conflict.json"] if name == "conflict" else []):
            docs.update((d["doc_id"], d) for d in json.loads((ROOT / file).read_text(encoding="utf-8")))
        files = sorted(path.glob("*.json"))
        turns = [json.loads(f.read_text(encoding="utf-8")) for f in files]
        issues = []
        blocked = False
        for i, t in enumerate(turns):
            if t.get("model_error"):
                code = t["model_error"]["code"]
                blocked = code in ("missing_key", "http_401", "http_402", "http_403", "model_network")
                issues.append(code)
            else:
                issues.extend(inspect_turn(t, statuses[i], required[i], name, docs))
        if [t["question"] for t in turns] != questions:
            issues.append("对话尚未跑完")
        if run.returncode and not issues:
            issues.append("CLI 非零退出")
        result = "blocked" if blocked else "failed" if issues else "passed"
        report.append(dict(case=name, command=["python", *args], questions=questions, result=result,
                           issues=issues, traces=[f.relative_to(folder).as_posix() for f in files],
                           terminal=f"{name}/terminal.txt"))
        print(name, result, [t["status"] for t in turns], issues, flush=True)
        (folder / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(folder)
    return int(any(row["result"] != "passed" for row in report))


if __name__ == "__main__":
    sys.exit(main())
