# CLI 交付收尾验证

执行者为 Codex，日期为 2026-11-05。审查范围为 terminal_ui.py、CLI 入口、菜单与中断测试、两种启动方式和相关交付文档。本次按当时的文件和已确认的交互要求审查。

## 发现与处理

- 实际在交互输入处按 Ctrl+C，原程序退出码为 1，终端显示以 KeyboardInterrupt 结尾的 Python 堆栈。新增中断用例在原代码上同样失败。CLI 入口现捕获该中断并输出“已中断，结束本次会话”。单元测试核对 Python 的退出值 130；Windows PTY 宿主返回 1，终端已无错误堆栈。
- 菜单在 / 输入后立即出现，上下方向键、回车执行与 Esc 取消均按预期工作。继续输入 /s 只显示 /sources。取消后输入中文仍正常。
- 本地指令不进入模型循环，不生成问答 Trace。两轮住宿追问在菜单操作之后仍依次返回待确认和已回答。
- prompt-toolkit 3.0.52 只在项目 .venv 中安装，基础 Python 通过整行输入使用 CLI。两种入口的结果均保存为纯文本，重定向输出未发现 ANSI 颜色控制符或等待动画。
- 问答过程中按 Ctrl+C 会结束进程。中断尚未完成的轮次没有完整 Trace；已保存轮次保留。真实请求已发送时，本地中断不能撤销服务端已接收的请求。

本次源码修改仅在 CLI 最外层增加中断提示。新增测试覆盖输入时中断、问答时中断、等待动画清理，以及筛选和取消菜单后继续中文输入。

## 命令与实际结果

从项目根目录执行：

```powershell
.\.venv\Scripts\python.exe -X utf8 -B -m unittest discover -s tests -v
python -X utf8 -B -m unittest discover -s tests -v
```

| 检查 | 实际结果 | 证据 |
| --- | --- | --- |
| 含菜单完整测试 | 34 项通过 | [输出](tests-menu.txt) |
| 基础环境 | 32 项通过，2 项可选菜单测试跳过 | [输出](tests-base.txt) |
| README 六组离线命令 | 全部退出码 0，含多轮及故障注入 | [命令执行表](run-results.json) |
| 即时菜单与中文问答 | 即时显示、选择、执行、取消和追问通过 | [PTY 按键与输出](menu-terminal.json) |
| Ctrl+C 复验 | 显示简短提示，关闭本次会话 | [PTY 最后一步](menu-terminal.json) |

本机使用 Python 3.12，项目内终端依赖为 prompt-toolkit 3.0.52、wcwidth 0.9.4。检查时环境可读取已配置的 API 密钥，扫描器只输出是否完成精确匹配检查。

README 的六组执行输出依次为 [报销期限](readme-1.txt)、[二等座](readme-2.txt)、[一等座](readme-3.txt)、[住宿追问](readme-4.txt)、[制度冲突](readme-5.txt)、[首次检索超时](readme-6.txt)。每组对应目录中保存完整离线 Trace。记录中的绝对执行路径替换为 <project> 或 <python>。

菜单操作后的住宿首轮 [Trace](manual/bf74429c9ff84e8698ec113f4c13276a-01.json) 为待确认，第二轮“上海” [Trace](manual/bf74429c9ff84e8698ec113f4c13276a-02.json) 为已回答，引用 D02，每人每晚最高 500 元，限额内按实报销。

## 评估边界

真实模型第三轮通过 5/6，正常检索的单独补测和两处措辞限制见 [评估报告](../../../docs/03-evaluation.md)。本轮终端检查未发起真实模型请求。项目作者的交互与 Trace 复核结论见 [AI 使用与个人贡献](../../../docs/04-ai-usage.md)。
