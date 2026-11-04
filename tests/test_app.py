import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import memory_store


class AppTests(unittest.TestCase):
    def test_chat_reply_has_speech_button_immediately(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "memory.db"), \
                 patch("jarvis_ai.generate_reply", return_value="Hello from JARVIS"), \
                 patch("voice_output.speak_button") as speak:
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
                app.run()
                self.assertEqual(len(app.exception), 0)
                app.chat_input[0].set_value("Hello").run()
                self.assertEqual(len(app.exception), 0)
                self.assertEqual(app.session_state["chat"][-1]["content"], "Hello from JARVIS")
                speak.assert_called_once_with("Hello from JARVIS")


if __name__ == "__main__":
    unittest.main()
