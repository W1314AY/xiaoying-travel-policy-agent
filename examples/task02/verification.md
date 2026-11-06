# 任务 02 离线验收记录

在项目根目录使用 Python 3.12 运行。D05 仅属于额外的正向测试夹具。每个代码块包含本次实际命令和终端输出。

## 住宿追问

[第 1 轮 Trace](b292243f2204496c95fe66b3c14d4fbe-01.json) · [第 2 轮 Trace](b292243f2204496c95fe66b3c14d4fbe-02.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "这趟出差住宿费上限是多少？" "上海" --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：这趟出差住宿费上限是多少？
状态：待确认
回答：请问本次国内出差的目的地是哪座城市？
引用：D02 [2026-09-01] 普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币。在其他国内城市住宿，每人每晚上限为 350 元人民币。限额内按实际住宿费用报销。
资料缺口：请问本次国内出差的目的地是哪座城市？
记录路径：<project>\examples\task02\b292243f2204496c95fe66b3c14d4fbe-01.json
模式：离线 Mock（合成制度）
问题：上海
状态：已回答
回答：上海适用的条款为「普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币」。限额内按实际住宿费用报销。
引用：D02 [2026-09-01] 普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币。在其他国内城市住宿，每人每晚上限为 350 元人民币。限额内按实际住宿费用报销。
资料缺口：无
记录路径：<project>\examples\task02\b292243f2204496c95fe66b3c14d4fbe-02.json
~~~

## 重启进程

[第 1 轮 Trace](0adb48499ab14acab801968402a766df-01.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "这趟出差住宿费上限是多少？" --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：这趟出差住宿费上限是多少？
状态：待确认
回答：请问本次国内出差的目的地是哪座城市？
引用：D02 [2026-09-01] 普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币。在其他国内城市住宿，每人每晚上限为 350 元人民币。限额内按实际住宿费用报销。
资料缺口：请问本次国内出差的目的地是哪座城市？
记录路径：<project>\examples\task02\0adb48499ab14acab801968402a766df-01.json
~~~

## 相似问法

[第 1 轮 Trace](3b2ba6b69d7a45269708a0423f6835af-01.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "出差回来最晚什么时候交单？" --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：出差回来最晚什么时候交单？
状态：已回答
回答：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
资料缺口：无
记录路径：<project>\examples\task02\3b2ba6b69d7a45269708a0423f6835af-01.json
~~~

## 首查未中后改写

[第 1 轮 Trace](1896108b2cf341b1954d004d69212187-01.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "出差结束后最迟几天递交费用申请？" --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：出差结束后最迟几天递交费用申请？
状态：已回答
回答：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
资料缺口：无
记录路径：<project>\examples\task02\1896108b2cf341b1954d004d69212187-01.json
~~~

## 单问早餐费

[第 1 轮 Trace](b58a5390b43b4766829b0d50a3f7d493-01.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "早餐费能单独报销吗？" --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：早餐费能单独报销吗？
状态：依据不足
回答：现有制度未说明早餐费能否单独报销。
资料缺口：现有制度未说明早餐费能否单独报销。
记录路径：<project>\examples\task02\b58a5390b43b4766829b0d50a3f7d493-01.json
~~~

## 住宿和早餐费

[第 1 轮 Trace](03797d2ff770490b837b0070550b7efa-01.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "上海住宿限额是多少，早餐费能单独报销吗？" --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：上海住宿限额是多少，早餐费能单独报销吗？
状态：部分已回答
回答：上海适用的条款为「普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币」。限额内按实际住宿费用报销。 现有制度未说明早餐费能否单独报销。
引用：D02 [2026-09-01] 普通员工国内出差，在北京、上海、广州、深圳住宿，每人每晚上限为 500 元人民币。在其他国内城市住宿，每人每晚上限为 350 元人民币。限额内按实际住宿费用报销。
资料缺口：现有制度未说明早餐费能否单独报销。
记录路径：<project>\examples\task02\03797d2ff770490b837b0070550b7efa-01.json
~~~

## 常规资料

[第 1 轮 Trace](72cb22522179474b85fe4ce224c871bf-01.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "国内出差返程后多久要提交报销单？" --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：国内出差返程后多久要提交报销单？
状态：已回答
回答：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
资料缺口：无
记录路径：<project>\examples\task02\72cb22522179474b85fe4ce224c871bf-01.json
~~~

## 加入 D04 及继续查证

[第 1 轮 Trace](fa90fa3931224a6bb1d2781f66b6fa4c-01.json) · [第 2 轮 Trace](fa90fa3931224a6bb1d2781f66b6fa4c-02.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "国内出差返程后多久要提交报销单？" "以 D04 为准" --extra-data data/conflict.json --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：国内出差返程后多久要提交报销单？
状态：待确认
回答：两份制度规定的期限不一致。D01：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。 D04：普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。 适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D04 [2026-10-01] 普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。
资料缺口：适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
记录路径：<project>\examples\task02\fa90fa3931224a6bb1d2781f66b6fa4c-01.json
模式：离线 Mock（合成制度）
问题：以 D04 为准
状态：待确认
回答：两份制度规定的期限不一致。D01：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。 D04：普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。 适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D04 [2026-10-01] 普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。
资料缺口：适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
记录路径：<project>\examples\task02\fa90fa3931224a6bb1d2781f66b6fa4c-02.json
~~~

## 独立合成测试：依据明确的替代条款

[第 1 轮 Trace](af055b2d923741fab51702a5568370ab-01.json) · [第 2 轮 Trace](af055b2d923741fab51702a5568370ab-02.json)

~~~powershell
python -X utf8 develope/src/travel_qa.py "国内出差返程后多久要提交报销单？" "请查 D05" --extra-data data/conflict.json --extra-data tests/fixtures/precedence.json --trace-dir examples/task02
~~~

~~~text
模式：离线 Mock（合成制度）
问题：国内出差返程后多久要提交报销单？
状态：待确认
回答：两份制度规定的期限不一致。D01：普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。 D04：普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。 适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D04 [2026-10-01] 普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。
资料缺口：适用对象和起算日相同，版本日期无法证明替代关系。请提供说明优先级的本地文档 ID、标题或用「」标出的原文线索。
记录路径：<project>\examples\task02\af055b2d923741fab51702a5568370ab-01.json
模式：离线 Mock（合成制度）
问题：请查 D05
状态：已回答
回答：按 D04 执行。普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。
引用：D01 [2026-09-01] 普通员工国内出差，应自返程次日起 30 个自然日内提交本次出差的报销单。
引用：D04 [2026-10-01] 普通员工国内出差，应自返程次日起 15 个自然日内提交本次出差的报销单。
引用：D05 [2026-10-01] 普通员工国内出差适用以下替代关系。D04 替代 D01。
资料缺口：无
记录路径：<project>\examples\task02\af055b2d923741fab51702a5568370ab-02.json
~~~

## 自动化测试

~~~powershell
python -X utf8 -B -m unittest discover -s tests -v
~~~

~~~text
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
Ran 10 tests in 2.185s

OK
~~~
