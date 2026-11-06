"""差旅问答的终端显示。"""
import os
import sys
from contextlib import contextmanager
from itertools import cycle
from threading import Event, Thread


def supports_color():
    if not sys.stdout.isatty() or os.environ.get("NO_COLOR") or os.environ.get("TERM") == "dumb":
        return False
    if os.name != "nt":
        return True
    # Windows 控制台须先开启 VT，才能解释颜色控制符。
    import ctypes
    import msvcrt
    handle = ctypes.c_void_p(msvcrt.get_osfhandle(sys.stdout.fileno()))
    mode = ctypes.c_uint()
    console = ctypes.windll.kernel32
    return bool(console.GetConsoleMode(handle, ctypes.byref(mode))
                and console.SetConsoleMode(handle, mode.value | 0x0004))


@contextmanager
def waiting():
    if not sys.stdout.isatty() or os.environ.get("TERM") == "dumb":
        yield
        return
    stop = Event()
    label = "正在处理问题"

    def animate():
        for frame in cycle("|/-\\"):
            if stop.wait(0.15):
                return
            print(f"\r{frame} {label}…", end="", flush=True)

    worker = Thread(target=animate, daemon=True)
    worker.start()
    try:
        yield
    finally:
        stop.set()
        worker.join()
        print("\r" + " " * 16 + "\r", end="", flush=True)


def styled(text, code, color):
    return f"\033[{code}m{text}\033[0m" if color else text


COMMANDS = {"/examples": "查看示例问法", "/sources": "列出本次加载的制度",
            "/help": "查看指令", "/exit": "退出会话"}


def command_prompt(color):
    from prompt_toolkit import PromptSession
    from prompt_toolkit.completion import WordCompleter
    from prompt_toolkit.filters import Condition
    from prompt_toolkit.application import get_app
    from prompt_toolkit.key_binding import KeyBindings

    bindings = KeyBindings()

    @Condition
    def command_line():
        return get_app().current_buffer.text.startswith("/")

    @bindings.add("escape", filter=command_line, eager=True)
    def cancel(event):
        event.current_buffer.reset()

    @bindings.add("enter", filter=command_line)
    def execute(event):
        buf = event.current_buffer
        # 方向键会把选中指令填入输入行。直接回车则取第一个匹配项。
        command = next((c for c in COMMANDS if c.startswith(buf.text)), buf.text)
        event.app.exit(result=command)

    return PromptSession([("bold ansicyan" if color else "", "› ")],
                         completer=WordCompleter(list(COMMANDS), sentence=True, meta_dict=COMMANDS),
                         complete_while_typing=command_line, key_bindings=bindings,
                         reserve_space_for_menu=len(COMMANDS))


def interactive_questions(mode, documents, color):
    print("\n" + styled("差旅制度问答", "1;36", color) + "  ·  " + mode)
    prompt = styled("› ", "1;36", color)
    session = None
    if sys.stdin.isatty() and sys.stdout.isatty() and os.environ.get("TERM") != "dumb":
        try:
            session = command_prompt(color)
        except ModuleNotFoundError as exc:
            if exc.name != "prompt_toolkit":
                raise
    hint = "输入 / 展开菜单，↑↓ 选择，回车执行，Esc 取消。" if session else "输入 / 并回车查看指令。"
    print("直接提问，回车发送。" + hint + "\n")
    while True:
        try:
            question = (session.prompt() if session else input(prompt)).strip()
        except EOFError:
            return
        if question in ("/exit", "退出"):
            return
        if question in ("/", "/help"):
            for command, description in COMMANDS.items():
                print(f"  {command:10}{description}")
            print()
        elif question == "/examples":
            print("  国内出差返程后多久要提交报销单？\n  上海出差住宿标准是多少？"
                  "\n  自行升至一等座怎么报销？\n")
        elif question == "/sources":
            for doc in documents.values():
                print(f"  {doc['doc_id']}  {doc['title']}  [{doc['version']}]")
            print()
        elif question.startswith("/"):
            print("未知指令。输入 / 查看可用指令。\n")
        elif question:
            yield question


def show_result(trace, path, mode, color, *, echo_question):

    if echo_question:
        print("\n问题：" + trace["question"])
    print("\n" + styled("回答：", "1;36", color) + "  " + styled("[状态：" + trace["status"] + "]", "36", color))
    print(styled(trace["answer"], "1", color))
    print()
    details = [f"引用：{c['doc_id']} [{c['version']}] {c['quote']}" for c in trace["citations"]]
    details.extend("资料缺口：" + gap for gap in (trace["gaps"] or ["无"]))
    details.extend(["模式：" + mode, f"记录路径：{path}"])
    for line in details:
        print(styled("  " + line, "90", color))
    print()
