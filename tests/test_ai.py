import json
import os
import unittest
from unittest.mock import patch, MagicMock
from jarvis_ai import generate_reply, transcribe_audio, ollama_reply


class AITests(unittest.TestCase):
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
            with patch("jarvis_ai.request.urlopen", return_value=mock_response) as urlopen:
                self.assertEqual(generate_reply([{"role": "user", "content": "hi"}], []), "Hello!")
                self.assertEqual(urlopen.call_args.args[0].full_url, "http://127.0.0.1:11434/api/chat")


if __name__ == "__main__":
    unittest.main()
