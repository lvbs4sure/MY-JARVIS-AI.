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
    def test_cancel_late_result_and_finish_once(self):
        entered,release=Event(),Event()
        def operation(token):
            entered.set()
            release.wait(3)
            return ReplyResult("must not appear",True,"gemini")
        job=RequestJob("chat",operation,{"provider":"gemini","user_index":0})
        try:
            self.assertTrue(entered.wait(1))
            self.assertTrue(job.cancel())
            self.assertFalse(job.cancel())
        finally:
            release.set()
        self.assertTrue(job.finished.wait(2))
        state={"request_job":job,"chat":[{"role":"user","content":"fixture"}]}
        self.assertTrue(finish_request(state))
        self.assertTrue(state["chat"][0]["cancelled"])
        self.assertEqual(len(state["chat"]),1)
        self.assertEqual(state["activity"][-1]["outcome"],"interrupted")
        self.assertFalse(finish_request(state))
        self.assertIsNone(job.take_result())

    def test_capacity_is_bounded_and_released(self):
        release=Event()
        jobs=[RequestJob("chat",lambda token:release.wait(3)) for _ in range(2)]
        try:
            with self.assertRaises(RuntimeError):
                RequestJob("chat",lambda token:None)
        finally:
            release.set()
            for job in jobs:self.assertTrue(job.finished.wait(2))
        next_job=RequestJob("chat",lambda token:"done")
        self.assertTrue(next_job.finished.wait(2))
        self.assertEqual(next_job.take_result(),"done")
        self.assertIsNone(next_job.take_result())

    def test_exceptions_cannot_disclose_credentials(self):
        def fail(token):raise ValueError("private-marker")
        job=RequestJob("chat",fail)
        self.assertTrue(job.finished.wait(2))
        result=job.take_result()
        self.assertIsInstance(result,JobFailure)
        self.assertNotIn("private-marker",repr(result))

    def test_cancellation_prevents_retry_and_voice_upload(self):
        token=Event()
        client=MagicMock()
        client.__enter__.return_value=client
        def fail(**kwargs):
            token.set()
            raise errors.APIError(503,{"message":"private-marker"})
        client.models.generate_content.side_effect=fail
        with patch("google.genai.Client",return_value=client):
            result,failure=_gemini_content("test-key","fixture","configured-model",token)
        self.assertEqual(failure[1],"cancelled")
        client.models.generate_content.assert_called_once()
        with patch("jarvis_ai._gemini_content") as upload:
            self.assertIn("interrupted",transcribe_audio(b"fixture",cancel_event=token)[1])
            upload.assert_not_called()

    def test_voice_completion_is_consumed_once(self):
        job=RequestJob("voice",lambda token:(" Test transcript ",None),{"provider":"gemini"})
        self.assertTrue(job.finished.wait(2))
        state={"request_job":job,"chat":[]}
        finish_request(state)
        self.assertEqual(state["pending_spoken"],"Test transcript")
        self.assertFalse(finish_request(state))
        self.assertEqual(len(state["activity"]),1)

    def test_transcription_service_failure_never_auto_reuploads(self):
        import os
        with patch.dict(os.environ,{"JARVIS_VOICE_PROVIDER":"gemini","GEMINI_API_KEY":"placeholder"}), patch("google.genai.Client") as create:
            client=create.return_value.__enter__.return_value
            client.models.generate_content.side_effect=errors.APIError(503,{})
            text,error=transcribe_audio(b"fixture")
            self.assertIsNone(text)
            self.assertIn("HTTP 503",error)
            client.models.generate_content.assert_called_once()
            self.assertEqual(create.call_args.kwargs["http_options"]["timeout"],30000)
