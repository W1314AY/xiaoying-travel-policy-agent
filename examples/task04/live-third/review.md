# 六组真实评估 · 第三轮

本轮沿用前两轮的模型、输入、制度、请求时限、决策上限和判定程序，六类场景各运行一次，共七份 Trace。首轮 3/6、第二轮 4/6、本轮 5/6。[机器结果及各组命令](results.json) · [第二轮](../live-second/review.md) · [首轮](../live-first/results.json)

| 场景 | 程序判定 | 对照原文的复核 | 记录 |
| --- | --- | --- | --- |
| 正常检索 | failed | 首个模型请求 60 秒超时。无模型动作，本地检索未执行。 | [Trace](normal/a0f87245dbdf4764a162add8ad1be5b1-01.json) · [终端](normal/terminal.txt) |
| 首次检索超时 | passed | 首次工具超时后，模型改查“差旅费报销 报销单 期限”，命中并读取 D01，回答返程次日起 30 个自然日内。ID、版本和引文正确；正文自行写成《国内差旅制度》，实际标题为《差旅报销期限》。本次未走重试为空的分支，该分支有离线回归。 | [Trace](timeout/5c4ecf89b93648378c4ff57c96cb1082-01.json) · [终端](timeout/terminal.txt) |
| 制度冲突 | passed | 命中 D01、D04；批量请求被拒绝后分两步读取，并列引用 30 天和 15 天，请求补充适用依据。 | [Trace](conflict/79a236490a914abbba7ba93d6bb09e6c-01.json) · [终端](conflict/terminal.txt) |
| 资料外问题 | passed | 三次正常检索均为空，返回依据不足，无早餐费报销结论。 | [Trace](outside/54593d3bcf5c4d0db31e286cc3c03182-01.json) · [终端](outside/terminal.txt) |
| 相似问法 | passed | 首次检索命中 D01，正确引用返程次日起 30 个自然日。附加例子中的“10 月 1 日前”容易被理解为不含当天；若 9 月 1 日返程，第 30 天为 10 月 1 日，应写“最迟 10 月 1 日（含当天）”。 | [Trace](similar/a7c86a81f56f47809b526154a7034217-01.json) · [终端](similar/terminal.txt) |
| 上下文追问 | passed | 首轮读取 D02 后主动选择 ask_user，给出两档标准并询问目的地；员工回复上海后重新读取 D02，以已回答结束。500 元每人每晚、限额内按实报销与原文一致。 | [第 1 轮](context/3caa8f9c19ab4d4083a217e1d49eed51-01.json) · [第 2 轮](context/3caa8f9c19ab4d4083a217e1d49eed51-02.json) · [终端](context/terminal.txt) |

住宿问题的修复保留了模型选动作的职责。真实模式下，模型提交“部分已回答”需要同时摘录员工已问的两个事项，分别说明哪一项已答、哪一项缺制度。程序检查摘录是否来自用户提问，拒绝格式不完整或两项互相包含的提交，并沿用一次修正机会。文字匹配只能核对出处，事项在语义上是否独立仍须复核。成对测试覆盖“单问住宿但缺目的地”和“上海住宿上限加早餐费”。本地 28/28，通过后才启动本轮实测。[本地测试输出](offline-tests.txt)

普通组在首次模型决策前超时，因此本轮不能据它推断正常检索后的动作。上轮正常组的三步记录可单独对照；本轮故障组记录了 search_documents → search_documents → read_document → finish。每轮每组只采样一次。

```powershell
# 在项目根目录执行；本轮实际指定 --output examples/task04/live-third
$env:DEEPSEEK_API_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY', 'User')
python -X utf8 -B tests/evaluate_deepseek.py
```
