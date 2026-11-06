# 任务 03 实际验收记录

运行目录为 `<project>`，Python 3.12.10，离线 Mock，合成制度。CLI 演示和回归使用默认 Mock。异常测试通过可控 Mock 请求动作，由同一个执行器实际校验、调用工具和生成记录。

## 逐项结果

| 验收场景 | 本次执行记录 |
| --- | --- |
| 首次检索超时 | [选择重试，4 步已回答](cases/timeout-retry.json) · [选择停止，2 步工具失败](cases/timeout-stop.json) · [重试仍超时，2 步工具失败](cases/timeout-twice.json) |
| 缺少文档 ID | [补传后执行](cases/param-fixed.json) · [再次无效](cases/param-rejected.json) · [无剩余步数](cases/step8-param.json) |
| 未读文档 | [修正成功](cases/cite-doc_id-fixed.json) · [修正失败](cases/cite-doc_id-rejected.json) |
| 版本不符 | [修正成功](cases/cite-version-fixed.json) · [修正失败](cases/cite-version-rejected.json) |
| 原文不符 | [修正成功](cases/cite-quote-fixed.json) · [修正失败](cases/cite-quote-rejected.json) · [第 8 步失败](cases/step8-cite.json) |
| 逐轮核对引用 | [前一轮读取](cases/prior-turn.json) · [本轮拦下旧引用，重读后采纳原文片段](cases/reread-before-citing.json) |
| 8 步边界 | [第 8 步读取，未完成](cases/step8-read.json) · [接着输入，从第 1 步开始](cases/next-turn.json) · [第 8 步有效回答](cases/step8-finish.json) |

## 首次检索超时演示

[CLI Trace](950c988a9536437ab646ea8e37755e98-01.json)

```powershell
python -X utf8 -B develope/src/travel_qa.py '国内出差返程后多久要提交报销单？' --first-search-timeout --trace-dir examples/task03
```

```text
模式：离线 Mock（合成制度）
问题：国内出差返程后多久要提交报销单？
状态：已回答
回答：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
资料缺口：无
记录路径：<project>\examples\task03\950c988a9536437ab646ea8e37755e98-01.json
```

## 任务 03 专项测试

归档命令使用新建目录以保留旧记录。复跑时可省略 `--trace-dir`，或指定一个新目录。

```powershell
python -X utf8 -B tests/test_guardrails.py -v --trace-dir examples/task03/cases
```

```text
test_citation_checks (__main__.Guardrails.test_citation_checks) ... ok
test_eighth_tool_then_next_turn (__main__.Guardrails.test_eighth_tool_then_next_turn) ... ok
test_eighth_valid_answer (__main__.Guardrails.test_eighth_valid_answer) ... ok
test_first_timeout_and_retry (__main__.Guardrails.test_first_timeout_and_retry) ... ok
test_missing_parameter (__main__.Guardrails.test_missing_parameter) ... ok
test_no_room_for_correction (__main__.Guardrails.test_no_room_for_correction) ... ok
test_prior_turn_is_not_current_evidence (__main__.Guardrails.test_prior_turn_is_not_current_evidence) ... ok
test_retry_fails (__main__.Guardrails.test_retry_fails) ... ok
test_timeout_then_stop (__main__.Guardrails.test_timeout_then_stop) ... ok

----------------------------------------------------------------------
Ran 9 tests in 0.030s

OK
```

## 任务 01、02 回归

```powershell
python -X utf8 -B -m unittest discover -s tests -p test_offline_cli.py -v
```

```text
test_conflict_rechecks_without_trusting_user_or_newest (test_offline_cli.OfflineCLI.test_conflict_rechecks_without_trusting_user_or_newest) ... ok
test_context_in_earlier_statement (test_offline_cli.OfflineCLI.test_context_in_earlier_statement) ... ok
test_deadline_without_key (test_offline_cli.OfflineCLI.test_deadline_without_key) ... ok
test_interactive_destination_and_restart (test_offline_cli.OfflineCLI.test_interactive_destination_and_restart) ... ok
test_no_match (test_offline_cli.OfflineCLI.test_no_match) ... ok
test_paraphrase_and_empty_first_search (test_offline_cli.OfflineCLI.test_paraphrase_and_empty_first_search) ... ok
test_partly_answered (test_offline_cli.OfflineCLI.test_partly_answered) ... ok
test_rail_seats (test_offline_cli.OfflineCLI.test_rail_seats) ... ok
test_replacement_uses_read_text (test_offline_cli.OfflineCLI.test_replacement_uses_read_text) ... ok
test_verified_local_precedence (test_offline_cli.OfflineCLI.test_verified_local_precedence) ... ok

----------------------------------------------------------------------
Ran 10 tests in 2.997s

OK
```

[第 1 轮 Trace](regression/f1ce6c192c1e47989b5961cd48606f99-01.json) · [第 2 轮 Trace](regression/f1ce6c192c1e47989b5961cd48606f99-02.json) · [第 3 轮 Trace](regression/f1ce6c192c1e47989b5961cd48606f99-03.json)

```powershell
python -X utf8 -B develope/src/travel_qa.py '国内出差返程后多久要提交报销单？' '这趟出差住宿费上限是多少？' '上海' --trace-dir examples/task03/regression
```

```text
模式：离线 Mock（合成制度）
问题：国内出差返程后多久要提交报销单？
状态：已回答
回答：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
资料缺口：无
记录路径：<project>\examples\task03\regression\f1ce6c192c1e47989b5961cd48606f99-01.json
模式：离线 Mock（合成制度）
问题：这趟出差住宿费上限是多少？
状态：待确认
回答：请问本次国内出差的目的地是哪座城市？
引用：D02 [2026-09-01] 普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币。在其他国内城市住宿，每人每晚上限为 350 元人民币。限额内按实际住宿费用报销。
资料缺口：请问本次国内出差的目的地是哪座城市？
记录路径：<project>\examples\task03\regression\f1ce6c192c1e47989b5961cd48606f99-02.json
模式：离线 Mock（合成制度）
问题：上海
状态：已回答
回答：上海适用的条款为「普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币」。限额内按实际住宿费用报销。
引用：D02 [2026-09-01] 普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币。在其他国内城市住宿，每人每晚上限为 350 元人民币。限额内按实际住宿费用报销。
资料缺口：无
记录路径：<project>\examples\task03\regression\f1ce6c192c1e47989b5961cd48606f99-03.json
```

## 完整测试

```powershell
python -X utf8 -B -m unittest discover -s tests -v
```

```text
test_citation_checks (test_guardrails.Guardrails.test_citation_checks) ... ok
test_eighth_tool_then_next_turn (test_guardrails.Guardrails.test_eighth_tool_then_next_turn) ... ok
test_eighth_valid_answer (test_guardrails.Guardrails.test_eighth_valid_answer) ... ok
test_first_timeout_and_retry (test_guardrails.Guardrails.test_first_timeout_and_retry) ... ok
test_missing_parameter (test_guardrails.Guardrails.test_missing_parameter) ... ok
test_no_room_for_correction (test_guardrails.Guardrails.test_no_room_for_correction) ... ok
test_prior_turn_is_not_current_evidence (test_guardrails.Guardrails.test_prior_turn_is_not_current_evidence) ... ok
test_retry_fails (test_guardrails.Guardrails.test_retry_fails) ... ok
test_timeout_then_stop (test_guardrails.Guardrails.test_timeout_then_stop) ... ok
test_conflict_rechecks_without_trusting_user_or_newest (test_offline_cli.OfflineCLI.test_conflict_rechecks_without_trusting_user_or_newest) ... ok
test_context_in_earlier_statement (test_offline_cli.OfflineCLI.test_context_in_earlier_statement) ... ok
test_deadline_without_key (test_offline_cli.OfflineCLI.test_deadline_without_key) ... ok
test_interactive_destination_and_restart (test_offline_cli.OfflineCLI.test_interactive_destination_and_restart) ... ok
test_no_match (test_offline_cli.OfflineCLI.test_no_match) ... ok
test_paraphrase_and_empty_first_search (test_offline_cli.OfflineCLI.test_paraphrase_and_empty_first_search) ... ok
test_partly_answered (test_offline_cli.OfflineCLI.test_partly_answered) ... ok
test_rail_seats (test_offline_cli.OfflineCLI.test_rail_seats) ... ok
test_replacement_uses_read_text (test_offline_cli.OfflineCLI.test_replacement_uses_read_text) ... ok
test_verified_local_precedence (test_offline_cli.OfflineCLI.test_verified_local_precedence) ... ok

----------------------------------------------------------------------
Ran 19 tests in 2.756s

OK
```
