import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import memory_store


class AppTests(unittest.TestCase):
    def test_memory_search_edit_delete_in_dashboard(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "memory.db"):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
                app.text_area[0].set_value("Test memory: favourite fruit is mango")
                app.button[0].click().run()
                self.assertFalse(app.exception)
                identity = memory_store.list_memories()[0][0]
                app.text_input(key="memory_search").set_value("mango").run()
                self.assertEqual(len(app.expander), 2)
                app.text_area(key=f"note_{identity}").set_value("Test memory: favourite fruit is pear")
                next(button for button in app.button if button.label == "Save changes").click().run()
                self.assertFalse(app.exception)
                self.assertEqual(memory_store.list_memories()[0][1], "Test memory: favourite fruit is pear")
                app.text_input(key="memory_search").set_value("pear").run()
                app.checkbox(key=f"confirm_delete_{identity}").check().run()
                app.button(key=f"delete_{identity}").click().run()
                self.assertFalse(app.exception)
                self.assertEqual(memory_store.list_memories(), [])

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


    def test_voice_message_sends_directly_after_consent(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "memory.db"), \
                 patch("jarvis_ai.transcribe_audio", return_value=("Can you hear me?", None)) as transcribe, \
                 patch("jarvis_ai.generate_reply", return_value="Yes, I can hear you."), \
                 patch("voice_output.speak_button"):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
                # The microphone widget requires a browser to supply audio bytes.
                # Verify the UI no longer requires a second transcript-review form.
                self.assertFalse(app.exception)
                self.assertNotIn("voice_review", str(app.session_state))
                transcribe.assert_not_called()


if __name__ == "__main__":
    unittest.main()
