import os
import unittest
from unittest.mock import patch
from jarvis_ai import generate_reply
from reply_status import ReplyResult


class GoogleGroundingTests(unittest.TestCase):
    def test_transcription_preserves_original_language(self):
        from jarvis_ai import transcribe_audio
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "JARVIS_VOICE_PROVIDER": "gemini"}, clear=True), patch("jarvis_ai._gemini_content") as call:
            call.return_value = (type("Response", (), {"text": "Ẹ káàárọ̀"})(), None)
            text, error = transcribe_audio(b"RIFFexample")
            self.assertIsNone(error)
            self.assertEqual(text, "Ẹ káàárọ̀")
            self.assertIn("do not translate", call.call_args.args[1][0])

    def test_multilingual_chat_instruction(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True), patch("jarvis_ai._gemini_content") as call:
            call.return_value = (type("Response", (), {"text": "Bonjour"})(), None)
            generate_reply([{"role": "user", "content": "Bonjour"}], [], provider="gemini")
            self.assertIn("Reply in the language used by the user", call.call_args.args[1])

    def test_grounding_is_off_by_default(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key"}, clear=True), patch("jarvis_ai._gemini_content") as call:
            call.return_value = (type("Response", (), {"text": "ok"})(), None)
            result = generate_reply([{"role": "user", "content": "hello"}], [], provider="gemini", _structured=True)
            self.assertTrue(result.ok)
            self.assertIsNone(call.call_args.kwargs["config"])

    def test_explicit_opt_in_supplies_google_search_tool(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": "test-key", "JARVIS_GOOGLE_SEARCH": "on"}, clear=True), patch("jarvis_ai._gemini_content") as call:
            call.return_value = (type("Response", (), {"text": "grounded"})(), None)
            result = generate_reply([{"role": "user", "content": "latest"}], [], provider="gemini", _structured=True)
            self.assertTrue(result.ok)
            config = call.call_args.kwargs["config"]
            self.assertIsNotNone(config)
            self.assertIsNotNone(config.tools[0].google_search)


if __name__ == "__main__":
    unittest.main()
