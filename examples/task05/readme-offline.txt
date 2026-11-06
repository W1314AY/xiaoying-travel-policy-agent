本机临时目录前缀已脱敏，保留 pip 清理警告及退出码。

$ python --version
Python 3.12.10
exit=0

$ python -m pip install --no-index -r requirements.txt
Defaulting to user installation because normal site-packages is not writeable
WARNING: Failed to remove contents in a temporary directory '%TEMP%/pip-build-tracker-p9aq7nzo'.
You can safely remove it manually.
WARNING: Failed to remove contents in a temporary directory '%TEMP%/pip-unpack-z7bi13xg'.
You can safely remove it manually.
WARNING: Failed to remove contents in a temporary directory '%TEMP%/pip-ephem-wheel-cache-calhntaw'.
You can safely remove it manually.
WARNING: Failed to remove contents in a temporary directory '%TEMP%/pip-install-2uar1v4f'.
You can safely remove it manually.
exit=0

$ python -X utf8 develope/src/travel_qa.py "国内出差返程后多久要提交报销单？"
模式：离线 Mock（合成制度）
问题：国内出差返程后多久要提交报销单？
状态：已回答
回答：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
资料缺口：无
记录路径：<project>\examples\offline\2274784143984ee8be52a39eeb31a8f3-01.json
exit=0

$ python -X utf8 develope/src/travel_qa.py "高铁二等座怎么报销？"
模式：离线 Mock（合成制度）
问题：高铁二等座怎么报销？
状态：已回答
回答：普通员工国内出差乘坐高铁或动车，二等座按实际票价报销。自行选择一等座的，最高按同车次、同区间二等座票价报销，差额由本人承担。
引用：D03 [2026-09-01] 普通员工国内出差乘坐高铁或动车，二等座按实际票价报销。自行选择一等座的，最高按同车次、同区间二等座票价报销，差额由本人承担。
资料缺口：无
记录路径：<project>\examples\offline\f23646ef2277456886a2391835f53843-01.json
exit=0

$ python -X utf8 develope/src/travel_qa.py "自行升至一等座怎么报销？"
模式：离线 Mock（合成制度）
问题：自行升至一等座怎么报销？
状态：已回答
回答：普通员工国内出差乘坐高铁或动车，二等座按实际票价报销。自行选择一等座的，最高按同车次、同区间二等座票价报销，差额由本人承担。
引用：D03 [2026-09-01] 普通员工国内出差乘坐高铁或动车，二等座按实际票价报销。自行选择一等座的，最高按同车次、同区间二等座票价报销，差额由本人承担。
资料缺口：无
记录路径：<project>\examples\offline\f48a9b06dcce46dfa72f021e53b0b171-01.json
exit=0

$ python -X utf8 develope/src/travel_qa.py "这趟出差住宿费上限是多少？" "上海"
模式：离线 Mock（合成制度）
问题：这趟出差住宿费上限是多少？
状态：待确认
回答：请问本次国内出差的目的地是哪座城市？
引用：D02 [2026-09-01] 普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币。在其他国内城市住宿，每人每晚上限为 350 元人民币。限额内按实际住宿费用报销。
资料缺口：请问本次国内出差的目的地是哪座城市？
记录路径：<project>\examples\offline\d6120b48d7b147b1a2e1805c013ab334-01.json
模式：离线 Mock（合成制度）
问题：上海
状态：已回答
回答：上海适用的条款为「普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币」。限额内按实际住宿费用报销。
引用：D02 [2026-09-01] 普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币。在其他国内城市住宿，每人每晚上限为 350 元人民币。限额内按实际住宿费用报销。
资料缺口：无
记录路径：<project>\examples\offline\d6120b48d7b147b1a2e1805c013ab334-02.json
exit=0

$ python -X utf8 develope/src/travel_qa.py "国内出差返程后多久要提交报销单？" "请查 D04" --extra-data data/conflict.json
模式：离线 Mock（合成制度）
问题：国内出差返程后多久要提交报销单？
状态：待确认
回答：两份制度规定的期限不一致。D01：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。 D04：普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。 适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D04 [2026-10-01] 普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。
资料缺口：适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
记录路径：<project>\examples\offline\dd365ce847de4f7bbf2f0f66d5959fca-01.json
模式：离线 Mock（合成制度）
问题：请查 D04
状态：待确认
回答：两份制度规定的期限不一致。D01：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。 D04：普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。 适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D04 [2026-10-01] 普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。
资料缺口：适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
记录路径：<project>\examples\offline\dd365ce847de4f7bbf2f0f66d5959fca-02.json
exit=0

$ python -X utf8 -B develope/src/travel_qa.py "国内出差返程后多久要提交报销单？" --first-search-timeout
模式：离线 Mock（合成制度）
问题：国内出差返程后多久要提交报销单？
状态：已回答
回答：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
资料缺口：无
记录路径：<project>\examples\offline\95837d7f74394dec957dcc8abcdfdc6f-01.json
exit=0

$ python -X utf8 -B -m unittest discover -s tests -v
test_batch_is_rejected_then_model_reads_one_at_a_time (test_deepseek.DeepSeekAdapter.test_batch_is_rejected_then_model_reads_one_at_a_time) ... ok
test_empty_result_cannot_be_reported_as_tool_error (test_deepseek.DeepSeekAdapter.test_empty_result_cannot_be_reported_as_tool_error) ... ok
test_missing_key_never_sends (test_deepseek.DeepSeekAdapter.test_missing_key_never_sends) ... ok
test_session_uses_previous_question_and_answer (test_deepseek.DeepSeekAdapter.test_session_uses_previous_question_and_answer) ... ok
test_timeout_ends_turn (test_deepseek.DeepSeekAdapter.test_timeout_ends_turn) ... ok
test_timeout_then_empty_retry_can_finish_as_tool_failure (test_deepseek.DeepSeekAdapter.test_timeout_then_empty_retry_can_finish_as_tool_failure) ... ok
test_tool_roundtrip_and_timeout_observation (test_deepseek.DeepSeekAdapter.test_tool_roundtrip_and_timeout_observation) ... ok
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
Ran 26 tests in 4.957s

OK
exit=0
