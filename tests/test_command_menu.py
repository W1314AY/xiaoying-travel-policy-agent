import asyncio
from importlib.util import find_spec
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "develope/src"))
from terminal_ui import command_prompt


@unittest.skipUnless(find_spec("prompt_toolkit"), "可选终端依赖未安装")
class CommandMenu(unittest.IsolatedAsyncioTestCase):
    async def test_slash_opens_before_enter_and_arrows_select(self):
        from prompt_toolkit.application import create_app_session
        from prompt_toolkit.input import create_pipe_input
        from prompt_toolkit.output import DummyOutput

        with create_pipe_input() as keys, create_app_session(input=keys, output=DummyOutput()):
            session = command_prompt(False)
            async with asyncio.timeout(5):
                result = asyncio.create_task(session.prompt_async())
                keys.send_text("/")
                while not session.default_buffer.complete_state:
                    await asyncio.sleep(0.01)
                self.assertEqual(session.default_buffer.complete_state.completions[1].text, "/sources")
                keys.send_text("\x1b[B\x1b[B\x1b[B\x1b[A\r")
                self.assertEqual(await result, "/sources")

    async def test_cancel_menu_then_enter_chinese(self):
        from prompt_toolkit.application import create_app_session
        from prompt_toolkit.input import create_pipe_input
        from prompt_toolkit.output import DummyOutput

        with create_pipe_input() as keys, create_app_session(input=keys, output=DummyOutput()):
            session = command_prompt(False)
            async with asyncio.timeout(5):
                result = asyncio.create_task(session.prompt_async())
                keys.send_text("/s")
                while not session.default_buffer.complete_state:
                    await asyncio.sleep(0.01)
                self.assertEqual([c.text for c in session.default_buffer.complete_state.completions], ["/sources"])
                keys.send_text("\x1b")
                while session.default_buffer.text:
                    await asyncio.sleep(0.01)
                keys.send_text("上海住宿标准是多少？\r")
                self.assertEqual(await result, "上海住宿标准是多少？")
