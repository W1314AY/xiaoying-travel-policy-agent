"""差旅制度 CLI，默认离线，可显式选择 DeepSeek。"""
import argparse
import json
import re
from copy import deepcopy
from pathlib import Path
from uuid import uuid4
from deepseek import MODEL, TIMEOUT, ModelError, deepseek_turn
from terminal_ui import interactive_questions, show_result, supports_color, waiting

ROOT = Path(__file__).resolve().parents[2]
MAX_STEPS = 8


def load_documents(path):
    rows = json.loads(path.read_text(encoding="utf-8-sig"))
    documents = {}
    if not isinstance(rows, list) or not rows:
        raise ValueError("制度资料必须是非空列表")
    for row in rows:
        if (not isinstance(row, dict)
                or not all(isinstance(row.get(k), str) and row[k].strip()
                           for k in ("doc_id", "title", "version", "text"))
                or not isinstance(row.get("keywords"), list)
                or not row["keywords"]
                or not all(isinstance(k, str) and k.strip() for k in row["keywords"])):
            raise ValueError("制度记录缺少有效的文档 ID、标题、版本、原文或关键词")
        if row["doc_id"] in documents:
            raise ValueError(f"重复文档 ID：{row['doc_id']}")
        documents[row["doc_id"]] = row
    return documents


def search_documents(documents, query):
    mentioned = re.findall(r"\bD\d+\b", query, flags=re.ASCII)
    fragments = [s.strip() for s in re.findall(r"「([^」]+)」", query) if s.strip()]
    return [row["doc_id"] for row in documents.values()
            if row["doc_id"] in mentioned or any(s in row["text"] for s in fragments)
            or any(word in query for word in (row["title"], *row["keywords"]))]


def read_document(documents, doc_id):
    row = documents[doc_id]
    return {"doc_id": doc_id, "version": row["version"], "quote": row["text"]}


def destination(question):
    # shortcut: 离线样例只识别列出的国内城市，扩大地域覆盖时需接入城市资料。
    cities = ("北京", "上海", "广州", "深圳", "杭州", "南京", "成都", "武汉", "西安", "苏州")
    return next((city for city in cities if city in question), None)


def mock_turn(question, context, documents):
    """每次 yield 请求一步操作；send 接收实际执行结果。"""
    def search(query, why):
        result = yield "search_documents", {"query": query}, why
        if isinstance(result, dict) and result.get("error") == "search_timeout":
            result = yield "search_documents", {"query": query}, "检索超时，重试一次以核对制度。"
        return result

    def read(doc_id):
        return "read_document", {"doc_id": doc_id}, "读取本地原文，核对版本和条款。"

    old_conflict = context.get("conflict")
    city = destination(question)
    if city:
        context["city"] = city
    query = question
    new_topic = any(word in question for row in documents.values() for word in row["keywords"])
    followup = not new_topic and "早餐" not in question
    if context.pop("needs_city", False) and followup:
        query = "住宿限额"
    review = old_conflict and (followup or "「" in question or re.search(r"D\d+", question)
                               or any(row["title"] in question for row in documents.values()))
    if review:
        query = old_conflict
    context.pop("conflict", None)

    breakfast = "早餐" in query
    lodging = "住宿" in query or "酒店" in query
    topics = [query]
    if breakfast:
        topics = ["住宿限额", "早餐费"] if lodging else ["早餐费"]
    citations, answers, gaps = [], [], []
    pending = False
    for topic in topics:
        ids = yield from search(topic, "按员工问题或会话中待补的事项检索制度。")
        if not ids and any(word in topic for word in ("递交费用申请", "上交费用单", "提交费用申请")):
            ids = yield from search("报销期限", "首次检索无候选，将费用申请的提交时间改写为报销期限。")
        if not ids:
            gaps.append("现有制度未说明早餐费能否单独报销。" if "早餐" in topic
                        else "检索未命中相关制度。")
            continue
        if review:
            clues = yield from search(question, "在本地查找员工指出的文档或原文线索。")
            ids = list(dict.fromkeys([*ids, *clues]))
        sources = []
        for doc_id in ids:
            sources.append((yield read(doc_id)))
        citations.extend(sources)
        by_id = {source["doc_id"]: source["quote"] for source in sources}
        if "D01" in by_id and "D04" in by_id:
            if by_id["D01"] == by_id["D04"]:
                answers.append(by_id["D01"])
                continue
            # shortcut: 离线样例只识别适用范围和替代关系都明确的合成条款。
            winners = [new for new, old in (("D04", "D01"), ("D01", "D04"))
                       if f"普通员工国内出差适用以下替代关系。{new} 替代 {old}。" in by_id.values()]
            if len(winners) == 1:
                answers.append(f"按 {winners[0]} 执行。{by_id[winners[0]]}")
            else:
                pending = True
                context["conflict"] = "报销期限"
                answers.append(f"两份制度规定的期限不一致。D01：{by_id['D01']} D04：{by_id['D04']}")
                gaps.append("适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。")
        elif "D02" in by_id and len(sources) == 1:
            city = context.get("city")
            if not city:
                context["needs_city"] = pending = True
                gaps.append("请问本次国内出差的目的地是哪座城市？")
                continue
            sentences = by_id["D02"].split("。")
            line = next((s for s in sentences if city in s), None)
            if not line:
                line = next((s for s in sentences if "其他国内城市" in s), None)
            if line:
                basis = next((s for s in sentences if "按实际" in s), "")
                answers.append(f"{city}适用的条款为「{line}」。" + (basis + "。" if basis else ""))
            else:
                gaps.append("已读取的制度未说明该目的地的住宿标准。")
        elif len(sources) == 1:
            answers.append(sources[0]["quote"])
        else:
            pending = True
            gaps.append("命中多份制度，需核对适用条款。")
    status = ("待确认" if pending else "部分已回答" if answers and gaps
              else "已回答" if answers else "依据不足")
    action = "ask_user" if pending else "finish"
    yield action, dict(status=status, answer=" ".join(answers + gaps), gaps=gaps,
                       citations=citations), "根据已读取的条款与尚缺的信息结束本轮。"


def validate_tool(action, args, documents):
    if action == "rejected_batch":
        return "本步所有调用均未执行。请选择一个动作，收到结果后再决定下一步。"
    if not isinstance(action, str):
        return "工具名称必须是字符串。"
    parameter = {"search_documents": "query", "read_document": "doc_id"}.get(action)
    if not parameter:
        return "不支持的工具名称。"
    if (not isinstance(args, dict) or set(args) != {parameter}
            or not isinstance(args[parameter], str) or not args[parameter].strip()):
        return f"{action} 需要一个非空字符串参数 {parameter}。"
    if action == "read_document" and args[parameter] not in documents:
        return "未找到这个本地文档 ID。"


def validate_answer(action, args, reads, user_questions=None):
    fields = {"status", "answer", "gaps", "citations"}
    if isinstance(args, dict) and args.get("status") == "部分已回答" and user_questions is not None:
        items = args.get("partial_items")
        if isinstance(items, dict) and set(items) == {"answered", "unsupported"}:
            answered, unsupported = items["answered"], items["unsupported"]
            if (all(isinstance(s, str) and s.strip() and any(s in q for q in user_questions)
                    for s in (answered, unsupported))
                    and answered not in unsupported and unsupported not in answered):
                fields.add("partial_items")
        if "partial_items" not in fields:
            return "部分已回答需要分别摘录员工已问的两个独立事项。若仅缺一个事项的适用条件，请用 ask_user 返回待确认。"
    if not isinstance(args, dict) or set(args) != fields:
        return "回答字段不完整。"
    if (args["status"] not in ("已回答", "部分已回答", "依据不足", "工具失败", "待确认", "未完成")
            or (args["status"] == "待确认") != (action == "ask_user")
            or not isinstance(args["answer"], str) or not args["answer"].strip()
            or not isinstance(args["gaps"], list)
            or not all(isinstance(g, str) for g in args["gaps"])
            or not isinstance(args["citations"], list)):
        return "回答的状态、正文或列表格式无效。"
    if args["status"] in ("已回答", "部分已回答") and not args["citations"]:
        return "制度结论需要本轮实际读取的引用。"
    for citation in args["citations"]:
        if not isinstance(citation, dict) or not all(
                isinstance(citation.get(k), str) and citation[k].strip()
                for k in ("doc_id", "version", "quote")):
            return "引用需要文档 ID、版本和非空原文。"
        source = reads.get(citation["doc_id"])
        if not source:
            return "引用了本轮未读取的文档。"
        if citation["version"] != source["version"] or citation["quote"] not in source["quote"]:
            return "引用的版本或片段与读取结果不符。"


def failure(status, message):
    return dict(status=status, answer=message, citations=[], gaps=[message])


def answer_question(question, documents, context=None, *, model=mock_turn, first_search_timeout=False):
    if context is None:
        context = {}
    trace = {"mode": "offline_mock", "question": question, "steps": [],
             "context_before": context.copy()}
    if model is deepseek_turn:
        trace.update(mode="deepseek", model=MODEL, request_timeout_seconds=TIMEOUT,
                     first_search_timeout=first_search_timeout)
    updated = context.copy()
    user_questions = None
    if model is deepseek_turn:
        user_questions = [m["content"] for m in context.get("history", []) if m["role"] == "user"] + [question]
    decision = model(question, updated, documents)
    reads, rejected = {}, set()
    inject_timeout = first_search_timeout
    search_failed = False
    had_search_timeout = False
    observation = None
    outcome = None
    for index in range(1, MAX_STEPS + 1):
        try:
            action, args, reason = decision.send(observation)
        except ModelError as exc:
            trace["model_error"] = {"code": exc.code, "at_decision": index}
            outcome = failure("模型请求失败", str(exc))
            break
        except StopIteration:
            outcome = failure("未完成", "决策器结束时没有提交有效回答。")
            break
        terminal = action in ("finish", "ask_user")
        problem = (validate_answer(action, args, reads, user_questions) if terminal
                   else validate_tool(action, args, documents))
        if terminal and not problem and args["status"] == "工具失败" and not had_search_timeout:
            problem = "本轮没有发生检索错误。若所有事项均缺少制度依据，请选择依据不足。"
        if problem:
            kind = "invalid_answer" if terminal else "invalid_arguments"
            observation = summary = {"error": kind, "message": problem}
            if kind in rejected:
                outcome = failure("未完成", f"一次修正后仍未通过校验。{problem}")
            rejected.add(kind)
        elif terminal:
            if search_failed:
                outcome = failure("工具失败", "检索超时，未能完成本轮制度核对。")
            else:
                outcome = args
                context.clear()
                context.update(updated)
            summary = outcome["status"]
        elif action == "search_documents":
            simulated = inject_timeout
            inject_timeout = False
            try:
                if simulated:
                    raise TimeoutError("首次检索模拟超时")
                observation = search_documents(documents, **args)
                summary = {"candidate_ids": observation}
                search_failed = False
            except TimeoutError:
                had_search_timeout = True
                observation = summary = {"error": "search_timeout", "simulated": simulated,
                                         "message": "制度检索超时。"}
                if search_failed:
                    outcome = failure("工具失败", "重试后制度检索仍超时，无法核对条款。")
                search_failed = True
        else:
            observation = read_document(documents, **args)
            reads[args["doc_id"]] = observation.copy()
            summary = observation
        if trace["steps"]:
            trace["steps"][-1]["next_action"] = action
        trace["steps"].append({"step": index, "action": action, "arguments": deepcopy(args),
                               "result_summary": deepcopy(summary), "reason": reason,
                               "next_action": "结束"})
        if index == MAX_STEPS and (not terminal or problem):
            outcome = failure("未完成", f"本轮已达到 {MAX_STEPS} 次决策上限。" + (problem or ""))
        if outcome is not None:
            break
    trace.update(outcome)
    if model is deepseek_turn:
        context["history"] = [*context.get("history", []), {"role": "user", "content": question},
                              {"role": "assistant", "content": outcome["answer"]}]
    return trace


def main():
    parser = argparse.ArgumentParser(description="差旅制度问答（合成资料）")
    parser.add_argument("--mode", choices=("offline", "deepseek"), default="offline")
    parser.add_argument("questions", nargs="*", help="同一会话的各轮输入。省略时进入交互模式")
    parser.add_argument("--data", type=Path, default=ROOT / "data/policies.json")
    parser.add_argument("--extra-data", type=Path, action="append", default=[],
                        help="加入本次会话使用的补充制度，可重复")
    parser.add_argument("--trace-dir", type=Path)
    parser.add_argument("--first-search-timeout", action="store_true", help="模拟本轮首次制度检索超时")
    opts = parser.parse_args()
    directory = opts.trace_dir or ROOT / "examples" / opts.mode
    model = deepseek_turn if opts.mode == "deepseek" else mock_turn
    try:
        documents = load_documents(opts.data)
        for path in opts.extra_data:
            extra = load_documents(path)
            if documents.keys() & extra.keys():
                raise ValueError("补充资料与基础资料的文档 ID 重复")
            documents.update(extra)
        context, session = {}, uuid4().hex
        color = supports_color()
        mode_label = f"DeepSeek（{MODEL}）" if opts.mode == "deepseek" else "离线 Mock（合成制度）"
        questions = opts.questions or interactive_questions(mode_label, documents, color)
        for turn, raw in enumerate(questions, 1):
            question = raw.strip()
            if not question:
                parser.error("请输入非空问题")
            with waiting():
                trace = answer_question(question, documents, context, model=model,
                                        first_search_timeout=opts.first_search_timeout)
            trace.update(session_id=session, turn=turn)
            directory.mkdir(parents=True, exist_ok=True)
            path = directory / f"{session}-{turn:02}.json"
            with path.open("x", encoding="utf-8") as output:
                json.dump(trace, output, ensure_ascii=False, indent=2)
                output.write("\n")
            show_result(trace, path.resolve(), mode_label, color, echo_question=bool(opts.questions))
            if "model_error" in trace:
                parser.exit(1)
    except KeyboardInterrupt:
        parser.exit(130, "\n已中断，结束本次会话。\n")
    except (OSError, ValueError) as exc:
        parser.exit(1, f"运行失败：{exc}\n")


if __name__ == "__main__":
    main()
