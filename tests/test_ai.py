"""Tests that do not need a real Gemini key or network connection."""
import os
import unittest
from unittest.mock import patch

from jarvis_ai import generate_reply, transcribe_audio


class AITests(unittest.TestCase):
    def test_missing_key_returns_setup_guidance(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            reply = generate_reply([{"role": "user", "content": "hello"}], [])
            self.assertIn("API key", reply)

    def test_voice_requires_key(self):
        with patch.dict(os.environ, {"GEMINI_API_KEY": ""}):
            text, error = transcribe_audio(b"audio")
            self.assertIsNone(text)
            self.assertIn("API key", error)


if __name__ == "__main__":
    unittest.main()
