import tempfile
import unittest
from pathlib import Path
from threading import Event
from unittest.mock import MagicMock, patch
from streamlit.testing.v1 import AppTest
from google.genai import errors
import memory_store
from conversation_flow import finish_request
from jarvis_ai import _gemini_content, transcribe_audio
from reply_status import ReplyResult
from request_jobs import RequestJob, JobFailure


class RequestTests(unittest.TestCase):
    def test_browser_app_can_interrupt_blocked_request(self):
        entered,release=Event(),Event()
        def slow(*args,**kwargs):
            entered.set()
            release.wait(5)
            return ReplyResult("late fixture response",True,"gemini")
        with tempfile.TemporaryDirectory() as folder, patch.object(memory_store,"DB_PATH",Path(folder)/"test.db"), patch("jarvis_ai.generate_reply_result",side_effect=slow):
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"),default_timeout=15).run()
            try:
                app.chat_input[0].set_value("Nonpersonal cancellation fixture").run()
                self.assertTrue(entered.wait(1))
                self.assertFalse(app.exception)
                self.assertTrue(app.chat_input[0].disabled)
                app.button(key="interrupt_request").click().run()
                self.assertTrue(app.session_state["request_job"].cancel_event.is_set())
                self.assertEqual(len(app.session_state["chat"]),1)
            finally:
                release.set()
                self.assertTrue(app.session_state["request_job"].finished.wait(2))
            app.run()
            self.assertFalse(app.exception)
            self.assertFalse(app.chat_input[0].disabled)
            self.assertTrue(app.session_state["chat"][0]["cancelled"])
            self.assertEqual(len(app.session_state["chat"]),1)

    def test_mute_cancels_pending_transcription_without_answer(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(memory_store,"DB_PATH",Path(folder)/"test.db"), patch("jarvis_ai.generate_reply_result") as reply:
            job=RequestJob("voice",lambda token:(token.wait(5) and "late speech",None),{"provider":"gemini"})
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"),default_timeout=15)
            app.session_state["request_job"]=job
            try:
                app.run()
                app.toggle(key="microphone_muted").set_value(True).run()
                self.assertTrue(job.cancel_event.is_set())
                self.assertTrue(job.finished.wait(2))
                app.run()
                self.assertEqual(app.session_state["chat"],[])
                reply.assert_not_called()
            finally:
                job.cancel()
                job.finished.wait(2)

    def test_muted_stale_transcript_never_starts_answer(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(memory_store,"DB_PATH",Path(folder)/"test.db"), patch("jarvis_ai.generate_reply_result") as reply:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"),default_timeout=15)
            app.session_state["microphone_muted"]=True
            app.session_state["pending_spoken"]="Stale transcript"
            app.session_state["spoken_route"]={"provider":"gemini"}
            app.run()
            self.assertFalse(app.exception)
            self.assertEqual(app.session_state["chat"],[])
            reply.assert_not_called()

