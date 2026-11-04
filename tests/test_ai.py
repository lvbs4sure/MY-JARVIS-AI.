import json
import os
import unittest
from unittest.mock import patch, MagicMock
from jarvis_ai import generate_reply, transcribe_audio, ollama_reply


class AITests(unittest.TestCase):
    def setUp(self):
        guard = patch("jarvis_ai.local_inference_ready", return_value=True)
        guard.start()
        self.addCleanup(guard.stop)

    def test_voice_transcription_reports_silence_and_closes_client(self):
        with patch.dict(os.environ, {"JARVIS_VOICE_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key"}):
            with patch("google.genai.Client") as create:
                client = create.return_value.__enter__.return_value
                client.models.generate_content.return_value.text = "  "
                result, message = transcribe_audio(b"sample")
                self.assertIsNone(result)
                self.assertIn("No speech", message)
                create.return_value.__exit__.assert_called_once()
                self.assertEqual(create.call_args.kwargs["http_options"]["timeout"], 30000)

    def test_voice_transcription_returns_text(self):
        with patch.dict(os.environ, {"JARVIS_VOICE_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key"}):
            with patch("google.genai.Client") as create:
                create.return_value.__enter__.return_value.models.generate_content.return_value.text = " Hello "
                self.assertEqual(transcribe_audio(b"sample"), ("Hello", None))

    def test_missing_gemini_key(self):
        with patch.dict(os.environ, {"JARVIS_PROVIDER": "gemini", "GEMINI_API_KEY": ""}):
            self.assertIn("GEMINI_API_KEY", generate_reply([], []))

    def test_voice_disabled_by_default(self):
        with patch.dict(os.environ, {"JARVIS_VOICE_PROVIDER": "off"}):
            result, error = transcribe_audio(b"audio")
            self.assertIsNone(result)
            self.assertIn("disabled", error)

    def test_reject_remote_ollama_endpoint(self):
        with patch.dict(os.environ, {"OLLAMA_URL": "https://example.com"}):
            result, error = ollama_reply([], [])
            self.assertIsNone(result)
            self.assertIn("local", error)

    def test_local_chat_parses_reply(self):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"message": {"content": "Hello!"}}).encode()
        mock_response.__enter__.return_value = mock_response
        with patch.dict(os.environ, {"OLLAMA_URL": "http://127.0.0.1:11434", "JARVIS_PROVIDER": "ollama"}):
            with patch("jarvis_ai._local_urlopen", return_value=mock_response) as urlopen:
                self.assertEqual(generate_reply([{"role": "user", "content": "hi"}], []), "Hello!")
                self.assertEqual(urlopen.call_args.args[0].full_url, "http://127.0.0.1:11434/api/chat")

    def test_local_reply_cancelled_while_request_in_flight_is_discarded(self):
        from threading import Event
        from jarvis_ai import generate_reply_result

        cancelled = Event()

        def finish_after_stop(*args, **kwargs):
            cancelled.set()
            return "Stale private answer", None

        with patch("jarvis_ai.ollama_reply", side_effect=finish_after_stop):
            result = generate_reply_result(
                [{"role": "user", "content": "hello"}], [],
                provider="ollama", cancel_event=cancelled,
            )
        self.assertFalse(result.ok)
        self.assertEqual(result.kind, "cancelled")
        self.assertNotIn("Stale private answer", result.text)

    def test_cancelled_gemini_fallback_discards_local_answer(self):
        from threading import Event
        from jarvis_ai import generate_reply_result

        stopped = Event()

        def local_finishes_after_stop(*args, **kwargs):
            stopped.set()
            return "stale fallback answer", None

        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "JARVIS_OLLAMA_FALLBACK": "on"}):
            with patch("jarvis_ai._gemini_content", return_value=(None, ("temporary outage", "service", True, 503))):
                with patch("jarvis_ai.ollama_reply", side_effect=local_finishes_after_stop):
                    result = generate_reply_result([], [], provider="gemini", cancel_event=stopped)
        self.assertFalse(result.ok)
        self.assertEqual(result.kind, "cancelled")
        self.assertNotIn("stale fallback answer", result.text)

    def test_cancelled_voice_response_is_not_transcribed(self):
        from threading import Event

        stopped = Event()

        def transcription_finishes_after_stop(*args, **kwargs):
            stopped.set()
            response = MagicMock()
            response.text = "stale private transcription"
            return response, None

        with patch.dict(os.environ, {"JARVIS_VOICE_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key"}):
            with patch("jarvis_ai._gemini_content", side_effect=transcription_finishes_after_stop):
                result, message = transcribe_audio(b"sample", cancel_event=stopped)
        self.assertIsNone(result)
        self.assertIn("interrupted", message)

    def test_unknown_provider_rejected_without_network(self):
        with patch.dict(os.environ, {"JARVIS_PROVIDER": "unexpected"}):
            with patch("jarvis_ai._local_urlopen") as network:
                reply = generate_reply([], [])
                self.assertIn("Invalid JARVIS_PROVIDER", reply)
                network.assert_not_called()

    def test_ollama_request_contains_personal_context_locally(self):
        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps({"message": {"content": "Green."}}).encode()
        mock_response.__enter__.return_value = mock_response
        with patch.dict(os.environ, {"OLLAMA_URL": "http://127.0.0.1:11434", "JARVIS_PROVIDER": "ollama"}):
            with patch("jarvis_ai._local_urlopen", return_value=mock_response) as network:
                reply = generate_reply(
                    [{"role": "user", "content": "What is my colour?"}],
                    [(1, "My favourite colour is green", "now")],
                    name="My Assistant",
                )
                self.assertEqual(reply, "Green.")
                payload = json.loads(network.call_args.args[0].data)
                self.assertEqual(payload["messages"][0]["role"], "system")
                self.assertIn("My favourite colour is green", payload["messages"][0]["content"])
                self.assertIn("My Assistant", payload["messages"][0]["content"])
                self.assertEqual(payload["messages"][-1]["role"], "user")

    def test_voice_rejects_empty_and_invalid_recordings_without_upload(self):
        with patch.dict(os.environ, {"JARVIS_VOICE_PROVIDER": "gemini", "GEMINI_API_KEY": "placeholder"}):
            with patch("builtins.__import__", wraps=__import__) as importer:
                for recording in (b"", None, "not bytes", bytearray(b"audio")):
                    result, message = transcribe_audio(recording)
                    self.assertIsNone(result)
                    self.assertIn("empty or invalid", message)
                self.assertFalse(any(call.args[0] == "google" for call in importer.call_args_list))

    def test_voice_rejects_oversized_recording_before_api_call(self):
        with patch.dict(os.environ, {"JARVIS_VOICE_PROVIDER": "gemini", "GEMINI_API_KEY": "placeholder"}):
            result, message = transcribe_audio(b"x" * 8_000_001)
            self.assertIsNone(result)
            self.assertIn("too large", message)


if __name__ == "__main__":
    unittest.main()
