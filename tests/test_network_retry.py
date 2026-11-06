import os
import unittest
from unittest.mock import patch

import httpx
from google import genai

from jarvis_ai import generate_reply


class NetworkRetryTests(unittest.TestCase):
    def test_one_transient_connection_failure_recovers(self):
        calls = []

        def respond(request):
            calls.append(request)
            if len(calls) == 1:
                raise httpx.ConnectError("temporary DNS failure", request=request)
            return httpx.Response(200, json={"candidates": [{"content": {"role": "model", "parts": [{"text": "Recovered reply"}]}}]})

        real_client = genai.Client

        def create(**kwargs):
            kwargs["http_options"]["client_args"] = {"transport": httpx.MockTransport(respond)}
            return real_client(**kwargs)

        with patch.dict(os.environ, {"JARVIS_PROVIDER": "gemini", "GEMINI_API_KEY": "test-key", "JARVIS_OLLAMA_FALLBACK": "off"}):
            with patch("google.genai.Client", side_effect=create):
                self.assertEqual(generate_reply([{"role": "user", "content": "Hi"}], []), "Recovered reply")
        self.assertEqual(len(calls), 2)
