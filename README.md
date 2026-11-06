# 差旅制度问答 Agent

在终端查询国内差旅报销期限、住宿标准和铁路席别，回答附带文档 ID、版本及原文引用。支持多轮追问、制度冲突查证、检索故障演示，以及逐步执行记录（Trace）。

所有制度及金额为合成测试资料。默认使用离线 Mock，真实模式需显式选择 DeepSeek。Mock 验证流程，真实模型决策效果见运行记录。

## 安装和启动

使用 Python 3.12，在仓库根目录打开 PowerShell。基础问答只用标准库。

```powershell
python -X utf8 develope/src/travel_qa.py "国内出差返程后多久要提交报销单？"
python -X utf8 develope/src/travel_qa.py
```

省略问题参数即可逐轮提问，输入“退出”结束。即时指令菜单需要项目内的可选依赖：

```powershell
python -m venv --without-pip .venv
python -m pip --python .venv install -r requirements-cli.txt
.\.venv\Scripts\python.exe -X utf8 develope/src/travel_qa.py
```

输入 `/` 立即显示菜单，↑↓ 选择，Enter 执行，Esc 取消。继续输入字母可筛选指令。

| 指令 | 作用 |
| --- | --- |
| /help | 显示指令列表 |
| /examples | 显示示例问法 |
| /sources | 列出本次加载的制度及版本 |
| /exit | 结束会话 |

终端突出显示回答，以灰色显示引用、缺口和记录路径，等待时显示动画。基础整行输入模式使用 `/` 加回车查看指令。Ctrl+C 显示中断提示并结束会话，已完成轮次的记录保留。

## DeepSeek 模式

通过进程环境变量 `DEEPSEEK_API_KEY` 配置密钥，不要把真实密钥写入仓库。`.env.example` 展示变量名，程序不会自动加载 .env 文件。模型使用 `deepseek-flash`，单次请求超时为 60 秒，每轮最多 8 次决策。

若已配置同名 Windows 用户环境变量，可载入当前终端：

```powershell
if (!$env:DEEPSEEK_API_KEY) { $env:DEEPSEEK_API_KEY = [Environment]::GetEnvironmentVariable('DEEPSEEK_API_KEY','User') }
.\.venv\Scripts\python.exe -X utf8 develope/src/travel_qa.py --mode deepseek
```

真实模式会调用外部 API 并产生相应费用。达到决策上限返回未完成。

## 示例与测试

```powershell
python -X utf8 develope/src/travel_qa.py "高铁二等座怎么报销？"
python -X utf8 develope/src/travel_qa.py "自行升至一等座怎么报销？"
python -X utf8 develope/src/travel_qa.py "这趟出差住宿费上限是多少？" "上海"
python -X utf8 develope/src/travel_qa.py "国内出差返程后多久要提交报销单？" "请查 D04" --extra-data data/conflict.json
python -X utf8 develope/src/travel_qa.py "国内出差返程后多久要提交报销单？" --first-search-timeout
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -v
```

基础环境也可使用 `python -X utf8 -B -m unittest discover -s tests -v`，未安装终端依赖时跳过两项菜单测试。完整环境的本地回归记录为 34 项通过。

常规资料位于 `data/policies.json`。用 `--data` 指定基础资料，`--extra-data` 添加制度，`--trace-dir` 指定记录目录。`--first-search-timeout` 模拟每轮首次制度检索超时。

真实模型三轮评估依次为 3/6、4/6、5/6。最终第三轮正常组在首个模型请求超时，之后单独复跑成功，补测单列。两处措辞限制见 [评估报告](docs/03-evaluation.md)。每组每轮仅执行一次，无法据此估计稳定性。

需要重新运行真实评估时执行 `python -X utf8 -B tests/evaluate_deepseek.py`。历史执行记录保留失败与补测结果，部分本机路径以 `<project>` 等占位符展示。

## 文档与运行记录

- [业务需求](docs/01-requirements.md)
- [实现方案](docs/02-solution.md)
- [测试结果与限制](docs/03-evaluation.md)
- [AI 使用与个人贡献](docs/04-ai-usage.md)
- [复盘](docs/05-retrospective.md)
- [多轮问答与冲突记录](examples/task02/verification.md)
- [失败处理与决策上限](examples/task03/verification.md)
- [真实评估记录](examples/task04/verification.md)
- [终端交互验证](examples/task05/cli-final-20261105/review.md)
