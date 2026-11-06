import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "develope/src"))
import travel_qa
from terminal_ui import waiting


class TerminalInterrupt(unittest.TestCase):
    def test_ctrl_c_at_prompt_exits_without_traceback(self):
        with patch.object(sys, "argv", ["travel_qa.py"]), patch("builtins.input", side_effect=KeyboardInterrupt):
            with patch.object(sys, "stdout", io.StringIO()), patch.object(sys, "stderr", io.StringIO()) as err:
                with self.assertRaises(SystemExit) as stopped:
                    travel_qa.main()
                self.assertEqual(stopped.exception.code, 130)
                self.assertIn("已中断", err.getvalue())
                self.assertNotIn("Traceback", err.getvalue())

    def test_ctrl_c_during_answer_exits(self):
        with patch.object(sys, "argv", ["travel_qa.py", "上海住宿标准？"]):
            with patch.object(travel_qa, "answer_question", side_effect=KeyboardInterrupt):
                with patch.object(sys, "stderr", io.StringIO()) as err:
                    with self.assertRaises(SystemExit) as stopped:
                        travel_qa.main()
                    self.assertEqual(stopped.exception.code, 130)
                    self.assertIn("已中断", err.getvalue())

    def test_waiting_cleans_up_on_interrupt(self):
        output = io.StringIO()
        output.isatty = lambda: True
        with patch.object(sys, "stdout", output), patch.dict("os.environ", {"TERM": "xterm"}):
            with self.assertRaises(KeyboardInterrupt):
                with waiting():
                    raise KeyboardInterrupt
        self.assertTrue(output.getvalue().endswith("\r"))
