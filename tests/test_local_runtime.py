import json
import os
from pathlib import Path
import tempfile
from unittest.mock import MagicMock
import unittest
from unittest.mock import patch

import local_runtime


class IsolatedRuntimeTests(unittest.TestCase):
    def test_child_profile_and_model_paths_stay_inside_project(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder).resolve()
            env = local_runtime.child_environment(root, {"SYSTEMROOT": r"C:\Windows", "GEMINI_API_KEY": "secret", "OPENAI_API_KEY": "secret", "HTTPS_PROXY": "private"})
            for key in ("USERPROFILE", "APPDATA", "LOCALAPPDATA", "TEMP", "TMP", "OLLAMA_MODELS"):
                self.assertTrue(Path(env[key]).is_relative_to(root))
            self.assertNotIn("GEMINI_API_KEY", env)
            self.assertNotIn("OPENAI_API_KEY", env)
            self.assertNotIn("HTTPS_PROXY", env)
            self.assertEqual(env["OLLAMA_HOST"], "127.0.0.1:11434")
            self.assertEqual(env["OLLAMA_NO_CLOUD"], "1")
            self.assertEqual(env["OLLAMA_KEEP_ALIVE"], "0")

    def test_executable_tampering_fails_before_launch(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = Path(folder) / ".local-ai"
            (runtime / "runtime").mkdir(parents=True)
            executable = runtime / "runtime" / "ollama.exe"
            executable.write_bytes(b"original binary fixture")
            (runtime / "installation.json").write_text(json.dumps({"executable_sha256": local_runtime.sha256(executable)}))
            self.assertEqual(local_runtime.verified_executable(folder), executable.resolve())
            executable.write_bytes(b"changed")
            with self.assertRaises(RuntimeError):
                local_runtime.verified_executable(folder)

    def test_existing_unknown_service_is_never_reused_or_stopped(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch("local_runtime.port_open", return_value=True), patch("local_runtime.owned_process", return_value=None), patch("local_runtime.subprocess.Popen") as launch:
                with self.assertRaisesRegex(RuntimeError, "left untouched"):
                    local_runtime.start(folder)
                launch.assert_not_called()

    def test_low_memory_benchmark_does_not_start_or_load_model(self):
        with patch("local_runtime.hardware_readiness", return_value={"ram_available_gib": 0.6}), patch("local_runtime.start") as start, patch("local_runtime._local_urlopen") as network:
            result = local_runtime.benchmark()
            self.assertEqual(result["status"], "deferred")
            start.assert_not_called()
            network.assert_not_called()

    def test_unknown_memory_is_not_treated_as_safe(self):
        with patch("local_runtime.hardware_readiness", return_value={"ram_available_gib": None}), patch("local_runtime.start") as start:
            self.assertEqual(local_runtime.benchmark()["status"], "deferred")
            start.assert_not_called()

    def test_rounded_display_value_cannot_bypass_memory_guard(self):
        with patch("local_runtime.hardware_readiness", return_value={"ram_available_gib": 2.0, "ram_available_bytes": int(1.96 * 2**30)}), patch("local_runtime.start") as start:
            self.assertEqual(local_runtime.benchmark()["status"], "deferred")
            start.assert_not_called()

    def test_download_error_report_does_not_keep_signed_urls(self):
        with tempfile.TemporaryDirectory() as folder:
            runtime = Path(folder) / ".local-ai"
            runtime.mkdir()
            response = MagicMock()
            response.__enter__.return_value = response
            response.readline.return_value = b'{"error":"Get https://example.com/file?token=private: timeout"}\n'
            with patch("local_runtime.start"), patch("local_runtime._local_urlopen", return_value=response):
                with self.assertRaises(RuntimeError):
                    local_runtime.pull(folder)
            report = (runtime / "pull-error.json").read_text()
            self.assertNotIn("token=private", report)
            self.assertIn("<download endpoint>", report)

    def test_ready_benchmark_is_bounded_local_and_secret_free(self):
        with tempfile.TemporaryDirectory() as folder:
            (Path(folder) / ".local-ai").mkdir()
            response = MagicMock()
            response.__enter__.return_value = response
            response.read.return_value = b'{"message":{"content":"LOCAL_JARVIS_READY"}}'
            with patch.dict(os.environ, {"GEMINI_API_KEY": "secret-test-key", "JARVIS_PROVIDER": "gemini"}), patch("local_runtime.hardware_readiness", return_value={"ram_available_gib": 2.5, "ram_available_bytes": int(2.5 * 2**30)}), patch("local_runtime.start"), patch("local_runtime._local_urlopen", return_value=response) as network:
                result = local_runtime.benchmark(folder)
                self.assertEqual(result["status"], "passed")
                req = network.call_args.args[0]
                payload = json.loads(req.data)
                self.assertEqual(payload["options"], {"num_ctx": 1024, "num_predict": 32, "num_thread": 2})
                self.assertEqual(payload["keep_alive"], 0)
                self.assertFalse(payload["think"])
                self.assertNotIn("secret-test-key", str(req.headers) + req.data.decode())
                self.assertEqual(os.environ["JARVIS_PROVIDER"], "gemini")
