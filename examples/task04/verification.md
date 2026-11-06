# 任务 04 六组评估记录

最终版本第三轮机器判定 5/6，普通组在模型请求阶段超时，住宿追问和首次检索超时两组通过。[第三轮逐例核查与 Trace](live-third/review.md)

两轮严格按同一标准评分。首轮 3/6，第二轮 4/6。[第二轮逐项变化及 Trace](live-second/review.md)

## 首轮真实评估 · 2026-11-03

配置用户环境变量后，使用 `deepseek-flash` 对六类场景各运行一次，得到七份逐轮 Trace。程序判定三组通过、三组失败。下表按工具返回及本地合成原文逐例复核。[逐组运行命令与机器判定](live-first/results.json)

| 场景 | 机器判定 | 逐例复核 | 实际记录 |
| --- | --- | --- | --- |
| 正常检索 | passed | 3 步。检索命中 D01，读取后回答普通员工自返程次日起 30 个自然日内提交，与 D01 的起算日和期限一致。 | [Trace](live-first/normal/4390bb8e3a1743659e77d7c943de7662-01.json) · [终端](live-first/normal/terminal.txt) |
| 首次检索超时 | passed | 5 步。首次检索超时，模型换词重试。重试成功返回空候选，随后两次改写也为空。模型返回“工具失败”，无引用、无期限结论。测试允许此状态；记录中只有首次调用发生超时，后三次检索均执行成功。 | [Trace](live-first/timeout/cde854178ea4411b91978c12c38fe5ee-01.json) · [终端](live-first/timeout/terminal.txt) |
| 制度冲突 | failed | 第 1 步检索得到 D01、D04。第 2 次决策的响应未能解析为单个有效工具调用，返回 model_response，两份制度都未读取。适配器没有记录更细的错误原因，不能确定是多调用还是其他格式问题。 | [Trace](live-first/conflict/dc88ab8a70bc4fb1b7c14e4e72f76c2e-01.json) · [终端](live-first/conflict/terminal.txt) |
| 资料外问题 | failed | 4 步。三次检索均正常返回空候选。模型指出无条款可引用，却标记为“工具失败”。按验收规则应为“依据不足”。 | [Trace](live-first/outside/c743b30ecccf4d65b891e40bc242bb9c-01.json) · [终端](live-first/outside/terminal.txt) |
| 相似问法 | passed | 3 步。以“国内差旅 报销 交单 时限”首次检索就命中 D01，读取后给出返程次日起 30 个自然日。没有发生空结果后的再次改写。 | [Trace](live-first/similar/4faffda55eb749d8a35ea4757e2f2163-01.json) · [终端](live-first/similar/terminal.txt) |
| 上下文追问 | failed | 两轮各 3 步。首轮指出缺少目的地，却用 finish 给出“部分已回答”，未按约定用 ask_user 返回“待确认”。第二轮接到“上海”，重新读取 D02，答对每人每晚上限 500 元、限额内按实报销。会议住宿等补充情形未在 D02 中规定。 | [第 1 轮](live-first/context/12a32dedd06c45acbda14acb48663e44-01.json) · [第 2 轮](live-first/context/12a32dedd06c45acbda14acb48663e44-02.json) · [终端](live-first/context/terminal.txt) |

### 正常检索和首次超时的动作差异

员工输入均为“国内出差返程后多久要提交报销单？”，两组使用相同的 D01–D03 和模型设置。只有超时组启用了本地首次检索故障。模型自行生成查询词，两次首次查询的措辞也不同。

| 决策步 | 正常组 | 首次超时组 |
| --- | --- | --- |
| 1 | 查“国内差旅费报销 提交报销单 时限”，返回 D01 | 查“国内差旅报销单提交时限 出差返程后”，收到模拟的 search_timeout |
| 2 | read_document 读取 D01 原文 | search_documents 换词重试“差旅费报销 时限”，返回空列表 |
| 3 | finish 引用 D01 给出 30 个自然日 | 改查“国内差旅费管理办法”，返回空列表 |
| 4 | 已结束 | 再查“报销”，返回空列表 |
| 5 | 已结束 | finish 标记“工具失败”，说明无法核实期限 |

本地检索使用制度标题或已配置关键词的子串匹配。超时后选择的三个查询均没有包含 D01 的完整匹配词。真实记录证明本次模型根据工具结果改变了下一步；每组只运行一次，尚无法据此估计通过率或重试概率。

### 复跑

```powershell
Set-Location '<project>'
$env:DEEPSEEK_API_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','User')
python -X utf8 -B tests/evaluate_deepseek.py
```

本次实际命令另带 `--output examples/task04/live-first`。上面的复跑命令会创建新目录。只要有用例失败，批处理就会在保留各组结果后以退出码 1 结束。

## 先前的无密钥预检

早期预检时六组均缺少凭据，远端请求 0 次。以下保留当时的启动失败记录。

| 场景 | CLI 命令以外的复核材料 |
| --- | --- |
| 明确答案 | [实际终端输出](preflight/normal/terminal.txt) · [启动失败 Trace](preflight/normal/53ad5e64c0074a17bb265b98e7d9369f-01.json) |
| 首次检索超时 | [实际终端输出](preflight/timeout/terminal.txt) · [启动失败 Trace](preflight/timeout/844c0c6fabbf4b27a723cb595630ed08-01.json) |
| 制度冲突 | [实际终端输出](preflight/conflict/terminal.txt) · [启动失败 Trace](preflight/conflict/5037b29044af460bab83cdfb15f604fc-01.json) |
| 资料外 | [实际终端输出](preflight/outside/terminal.txt) · [启动失败 Trace](preflight/outside/6b12bbfe645042f98a6a4d690d195e1b-01.json) |
| 相似问法 | [实际终端输出](preflight/similar/terminal.txt) · [启动失败 Trace](preflight/similar/4d24cdffd1a14920a5ebea0b5099144c-01.json) |
| 上下文追问 | [实际终端输出](preflight/context/terminal.txt) · [启动失败 Trace](preflight/context/d4a4afdc884548fcaef28b07052ba7f3-01.json) |

[逐组命令与机器判定](preflight/results.json) · [可控测试与离线回归](offline-tests.txt)

从项目根目录运行 `python -X utf8 -B tests/evaluate_deepseek.py`，程序在 `examples/task04/` 新建目录，分别保存终端输出、完整 Trace 和机器判定。上下文组在同一进程完成两轮。`passed` 表示状态、引用、步数等程序检查通过，答案与条款含义仍须逐例复核。
