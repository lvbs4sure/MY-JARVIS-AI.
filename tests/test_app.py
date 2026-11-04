import tempfile
import hashlib
import io
import unittest
from pathlib import Path
from unittest.mock import patch

from streamlit.testing.v1 import AppTest

import memory_store


class AppTests(unittest.TestCase):
    def test_monitor_can_pause_without_sampling_and_preserve_private_memory(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "memory.db"), patch("dashboard_panels.SystemMonitor.sample") as sample:
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=10)
                app.session_state["live_monitoring"] = False
                app.run()
                self.assertFalse(app.exception)
                sample.assert_not_called()
                self.assertEqual(memory_store.list_memories(), [])

    def test_failed_reply_sets_avatar_state_and_actual_activity(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "memory.db"), patch("jarvis_ai.generate_reply", return_value="Gemini API error (HTTP 503)."), patch("voice_output.speak_button"):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=10).run()
                app.chat_input[0].set_value("Hello").run()
                self.assertFalse(app.exception)
                self.assertEqual(app.session_state["assistant_state"], "error")
                self.assertEqual(app.session_state["activity"][-1]["outcome"], "failed")
                self.assertTrue(any('state-error' in item.value for item in app.markdown))

    def test_voice_consent_send_and_duplicate_guard(self):
        with tempfile.TemporaryDirectory() as folder:
            sample = b"nonpersonal test recording"
            consent_key = "audio_consent_" + hashlib.sha256(sample).hexdigest()
            with patch.object(memory_store, "DB_PATH", Path(folder) / "memory.db"), \
                 patch("streamlit.audio_input", return_value=io.BytesIO(sample)), \
                 patch("jarvis_ai.transcribe_audio", return_value=("Voice test", None)) as transcribe, \
                 patch("jarvis_ai.generate_reply", return_value="Voice reply") as reply, \
                 patch("voice_output.speak_button"):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=10).run()
                self.assertTrue(app.button(key="transcribe").disabled)
                transcribe.assert_not_called()
                app.checkbox(key=consent_key).check().run()
                self.assertFalse(app.button(key="transcribe").disabled)
                app.button(key="transcribe").click().run()
                self.assertFalse(app.exception)
                self.assertEqual(transcribe.call_args.args,(sample,))
                self.assertIsNotNone(transcribe.call_args.kwargs["cancel_event"])
                reply.assert_called_once()
                self.assertEqual(app.session_state["chat"][-1]["content"], "Voice reply")
                self.assertEqual(app.metric[2].value, "2")
                self.assertTrue(app.button(key="transcribe").disabled)
                app.run()
                transcribe.assert_called_once()

    def test_memory_search_edit_delete_in_dashboard(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "memory.db"):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=10).run()
                app.text_area[0].set_value("Test memory: favourite fruit is mango")
                app.button[0].click().run()
                self.assertFalse(app.exception)
                identity = memory_store.list_memories()[0][0]
                app.text_input(key="memory_search").set_value("mango").run()
                self.assertEqual(len([item for item in app.expander if item.label.startswith("#")]), 1)
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
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=10)
                app.run()
                self.assertEqual(len(app.exception), 0)
                app.chat_input[0].set_value("Hello").run()
                self.assertEqual(len(app.exception), 0)
                self.assertEqual(app.session_state["chat"][-1]["content"], "Hello from JARVIS")
                self.assertEqual(app.metric[2].value, "2")
                speak.assert_any_call("Hello from JARVIS")


    def test_voice_message_sends_directly_after_consent(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(memory_store, "DB_PATH", Path(folder) / "memory.db"), \
                 patch("jarvis_ai.transcribe_audio", return_value=("Can you hear me?", None)) as transcribe, \
                 patch("jarvis_ai.generate_reply", return_value="Yes, I can hear you."), \
                 patch("voice_output.speak_button"):
                app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"), default_timeout=10).run()
                # The microphone widget requires a browser to supply audio bytes.
                # Verify the UI no longer requires a second transcript-review form.
                self.assertFalse(app.exception)
                self.assertNotIn("voice_review", str(app.session_state))
                transcribe.assert_not_called()


if __name__ == "__main__":
    unittest.main()
