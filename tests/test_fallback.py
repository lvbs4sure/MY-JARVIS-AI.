import os
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

import httpx
from google.genai import errors

from jarvis_ai import generate_reply, _NoLocalRedirect, _local_urlopen


class FallbackTests(unittest.TestCase):
    def run_failure(self, failure, enabled="on", local=("Local answer", None)):
        client = MagicMock()
        client.models.generate_content.side_effect = failure
        with patch.dict(os.environ, {"JARVIS_PROVIDER": "gemini", "GEMINI_API_KEY": "secret-test-key", "JARVIS_OLLAMA_FALLBACK": enabled}):
            with patch("google.genai.Client", return_value=client), patch("jarvis_ai.ollama_reply", return_value=local) as fallback:
                result = generate_reply([{"role": "user", "content": "Hello"}], [])
                self.assertNotIn("secret-test-key", result)
                self.assertNotIn("secret-test-key", str(fallback.call_args))
                return result, fallback

    def test_transient_statuses_use_labelled_local_fallback(self):
        for code in (408, 429, 500, 502, 503, 504):
            with self.subTest(code=code):
                result, fallback = self.run_failure(errors.APIError(code, {"message": "secret-test-key"}))
                self.assertIn("Local Ollama fallback", result)
                self.assertIn("Local answer", result)
                fallback.assert_called_once()

    def test_transport_failure_uses_fallback(self):
        result, fallback = self.run_failure(httpx.ConnectError("secret-test-key"))
        fallback.assert_called_once()
        self.assertIn("Local answer", result)

    def test_credentials_and_model_errors_do_not_fallback(self):
        for code in (400, 401, 403, 404):
            result, fallback = self.run_failure(errors.APIError(code, {"message": "secret-test-key"}))
            self.assertIn(f"HTTP {code}", result)
            fallback.assert_not_called()

    def test_fallback_requires_opt_in(self):
        result, fallback = self.run_failure(errors.APIError(503, {}), enabled="off")
        self.assertIn("HTTP 503", result)
        fallback.assert_not_called()

    def test_unavailable_local_model_reported_truthfully(self):
        result, _ = self.run_failure(errors.APIError(503, {}), local=(None, "Local Ollama unavailable."))
        self.assertIn("Local fallback failed", result)

    def test_local_redirect_rejected(self):
        with self.assertRaises(URLError):
            _NoLocalRedirect().redirect_request(None, None, 302, "Found", {}, "https://example.com")

    def test_local_requests_disable_proxy(self):
        with patch("jarvis_ai.request.build_opener") as build:
            _local_urlopen("http://127.0.0.1:11434/api/chat", 1)
            self.assertEqual(build.call_args.args[0].proxies, {})
