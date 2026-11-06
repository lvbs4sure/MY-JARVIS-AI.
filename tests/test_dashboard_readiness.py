import unittest
from dashboard_readiness import dashboard_readiness


class DashboardReadinessTests(unittest.TestCase):
    def test_default_local_route_is_not_claimed_working(self):
        result = dashboard_readiness(environ={})
        self.assertEqual(result["chat"][0], "unchecked")
        self.assertEqual(result["avatar"][0], "static")
        self.assertEqual(result["research"][0], "disconnected")
        self.assertEqual(result["camera"][0], "local-preview")
        self.assertEqual(result["history"][0], "optional")
        self.assertEqual(result["files"][0], "local-preview")
        self.assertIn("not sent to AI", result["files"][1])
        self.assertIn("enable", result["history"][1])
        self.assertIn("Start", result["camera"][1])

    def test_low_memory_blocks_local_chat(self):
        result = dashboard_readiness("ollama", {}, free_ram_bytes=1024)
        self.assertEqual(result["chat"][0], "blocked")
        self.assertIn("2 GiB", result["chat"][1])

    def test_cloud_route_requires_key_without_exposing_it(self):
        result = dashboard_readiness("gemini", {"GEMINI_API_KEY": "private-key"})
        self.assertEqual(result["chat"][0], "configured")
        self.assertNotIn("private-key", str(result))

    def test_transcription_requires_explicit_configuration(self):
        result = dashboard_readiness("gemini", {"GEMINI_API_KEY": "private-key"})
        self.assertEqual(result["microphone"][0], "blocked")
        enabled = dashboard_readiness("gemini", {"GEMINI_API_KEY": "private-key", "JARVIS_VOICE_PROVIDER": "gemini"})
        self.assertEqual(enabled["microphone"][0], "configured")

    def test_missing_model_and_unknown_route(self):
        self.assertEqual(dashboard_readiness("ollama", {}, local_models=[])["chat"][0], "blocked")
        self.assertEqual(dashboard_readiness("unknown", {})["chat"][0], "blocked")


if __name__ == "__main__":
    unittest.main()
