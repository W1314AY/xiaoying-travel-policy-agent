# 六组真实评估 · 第二轮

使用同一份制度、六组输入、评估程序和八步上限，每组各跑一次。六组共七轮。首轮 3/6，第二轮 4/6；两轮都是单次观察。[首轮](../verification.md) · [本轮程序判定与具体命令](results.json)

| 场景 | 首轮 | 第二轮 | 对照条款和执行步骤的复核 | 记录 |
| --- | --- | --- | --- | --- |
| 正常检索 | 通过 | 通过 | 3 步，命中后读取 D01，答复自返程次日起 30 个自然日内。 | [Trace](normal/a90076b2ad94401c9d41e9a91efd0826-01.json) · [终端](normal/terminal.txt) |
| 首次检索超时 | 通过 | 失败 | 6 步，超时后换词重试，后续检索均为空。第 5 步提交工具失败被程序拒绝，第 6 步改报依据不足。未给无依据的期限。 | [Trace](timeout/53eede1d9fa34ec1a2124aa6423c2467-01.json) · [终端](timeout/terminal.txt) |
| 制度冲突 | 失败 | 通过 | 5 步，换词命中 D01、D04，按步分别读取，用 ask_user 并列 30 天和 15 天，请补充废止或生效依据。 | [Trace](conflict/43cc5ab1f08047a4abc89fe4a87bfcf9-01.json) · [终端](conflict/terminal.txt) |
| 资料外问题 | 失败 | 通过 | 4 步，三次正常检索均为空，finish 返回依据不足，无早餐费报销结论。 | [Trace](outside/51583f82bc524bdf85e4956eb5a5bf56-01.json) · [终端](outside/terminal.txt) |
| 相似问法 | 通过 | 通过 | 3 步，首次检索命中 D01，读取后给出正确的 30 个自然日。 | [Trace](similar/adf32339e2b64df1adc2df06faefe2fc-01.json) · [终端](similar/terminal.txt) |
| 上下文追问 | 失败 | 失败 | 首轮 3 步，识别目的地缺失却用 finish 返回部分已回答。次轮 4 步，修正了无效工具名，重新读取 D02，上海每人每晚最高 500 元、限额内按实报销。 | [第 1 轮](context/d72fb25aaa0141ca930301911d6bbead-01.json) · [第 2 轮](context/d72fb25aaa0141ca930301911d6bbead-02.json) · [终端](context/terminal.txt) |

正常组搜索“国内差旅费报销单提交时限”，随后读取 D01。超时组首次搜索“国内差旅费报销单提交时限 出差返程后”，收到模拟错误后改查“差旅报销 提交时间”，再查“差旅费”和“费用报销”。三次都没有候选。第二轮实际的第 5、6 步分别保留了模型的初判和程序反馈后的修改。

模型接入与检索超时使用不同错误类型。本轮故障位于本地检索，模型请求正常。评估后调整了校验器，以区分“本轮曾发生超时”和“最近一次检索失败”；此修改仅经本地回归验证，未计入线上成绩。住宿首轮仍需验证模型能稳定选择 ask_user。

```powershell
# 在项目根目录执行；本轮实际输出目录为 examples/task04/live-second
$env:DEEPSEEK_API_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','User')
python -X utf8 -B tests/evaluate_deepseek.py
```
