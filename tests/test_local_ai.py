import json
import os
from types import SimpleNamespace as NS
import unittest
from unittest.mock import MagicMock, patch

from local_ai import inspect_local_ai, hardware_readiness
from jarvis_ai import generate_reply


class LocalAITests(unittest.TestCase):
    def response(self, data):
        response = MagicMock()
        response.__enter__.return_value = response
        response.read.return_value = json.dumps(data).encode()
        return response

    def test_discovery_uses_only_installed_models_and_sends_no_secrets(self):
        with patch.dict(os.environ, {"OLLAMA_URL": "http://127.0.0.1:11434", "GEMINI_API_KEY": "secret-test-key"}):
            with patch("local_ai._local_urlopen", return_value=self.response({"models": [{"name": "local-b"}, {"name": "local-a"}, {"name": "local-a"}, {"name": None}]})) as network:
                status = inspect_local_ai()
        self.assertEqual(status["models"], ["local-a", "local-b"])
        self.assertEqual(network.call_args.args, ("http://127.0.0.1:11434/api/tags",))
        self.assertNotIn("secret-test-key", str(network.call_args))
        self.assertEqual(network.call_args.kwargs["timeout"], 3)

    def test_remote_endpoint_rejected_without_network(self):
        with patch.dict(os.environ, {"OLLAMA_URL": "https://example.com"}):
            with patch("local_ai._local_urlopen") as network:
                self.assertEqual(inspect_local_ai()["status"], "invalid_configuration")
                network.assert_not_called()

    def test_missing_runtime_does_not_change_provider(self):
        with patch.dict(os.environ, {"OLLAMA_URL": "http://127.0.0.1:11434", "JARVIS_PROVIDER": "gemini"}):
            with patch("local_ai._local_urlopen", side_effect=OSError("unreachable")):
                self.assertEqual(inspect_local_ai()["status"], "unavailable")
                self.assertEqual(os.environ["JARVIS_PROVIDER"], "gemini")

    def test_empty_models_is_not_claimed_as_ready_for_generation(self):
        with patch.dict(os.environ, {"OLLAMA_URL": "http://127.0.0.1:11434"}):
            with patch("local_ai._local_urlopen", return_value=self.response({"models": []})):
                status = inspect_local_ai()
        self.assertEqual(status["models"], [])
        self.assertIn("no installed models", status["message"])

    def test_malformed_or_oversized_models_reported(self):
        with patch.dict(os.environ, {"OLLAMA_URL": "http://127.0.0.1:11434"}):
            for payload in (b"bad json", b'{}', b'x' * 1_000_001):
                response = self.response({})
                response.read.return_value = payload
                with patch("local_ai._local_urlopen", return_value=response):
                    self.assertEqual(inspect_local_ai()["status"], "invalid_response")

    def test_resource_advice_uses_available_ram(self):
        with patch("psutil.virtual_memory", return_value=NS(total=8 * 2**30, available=512 * 2**20)), patch("local_ai.shutil.disk_usage", return_value=NS(free=100 * 2**30)):
            result = hardware_readiness()
        self.assertEqual(result["ram_available_gib"], 0.5)
        self.assertIn("Free RAM is low", result["advice"])

    def test_session_local_routing_does_not_use_key_or_change_environment(self):
        with patch.dict(os.environ, {"JARVIS_PROVIDER": "gemini", "GEMINI_API_KEY": "secret-test-key", "OLLAMA_URL": "http://127.0.0.1:11434"}):
            with patch("jarvis_ai._local_urlopen", return_value=self.response({"message": {"content": "Local reply"}})) as network:
                result = generate_reply([{"role": "user", "content": "Hi"}], [], provider="ollama", local_model="installed-model")
                self.assertEqual(result, "Local reply")
                req = network.call_args.args[0]
                self.assertEqual(json.loads(req.data)["model"], "installed-model")
                self.assertNotIn("secret-test-key", str(req.headers) + req.data.decode())
                self.assertEqual(os.environ["JARVIS_PROVIDER"], "gemini")
