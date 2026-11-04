import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
import httpx
from google.genai import errors
from streamlit.testing.v1 import AppTest
import memory_store
from jarvis_ai import generate_reply_result, ollama_reply
from reply_status import ReplyResult


class ReliabilityTests(unittest.TestCase):
    def result_for(self, error):
        client = MagicMock()
        client.__enter__.return_value = client
        client.models.generate_content.side_effect = error
        with patch.dict(os.environ, {"GEMINI_API_KEY": "private-marker", "JARVIS_OLLAMA_FALLBACK": "off"}), patch("google.genai.Client", return_value=client), patch("jarvis_ai.time.sleep"):
            result = generate_reply_result([], [], provider="gemini")
        self.assertNotIn("private-marker", result.text)
        return result, client.models.generate_content.call_count

    def test_retry_budget_and_classification(self):
        for code, kind, attempts in [(504,"service",2),(503,"service",2),(429,"rate_limit",1),(403,"access",1),(404,"model",1)]:
            with self.subTest(code=code):
                result, calls = self.result_for(errors.APIError(code,{"message":"private-marker"}))
                self.assertFalse(result.ok)
                self.assertEqual((result.kind, result.http_status, calls),(kind,code,attempts))
        result, calls = self.result_for(httpx.ReadTimeout("private-marker"))
        self.assertEqual((result.kind,calls),("timeout",2))

    def test_success_is_not_inferred_from_model_wording(self):
        response = MagicMock(text="Gemini API error is an example phrase.")
        with patch.dict(os.environ, {"GEMINI_API_KEY":"private-marker"}), patch("jarvis_ai._gemini_content", return_value=(response,None)):
            self.assertTrue(generate_reply_result([],[],provider="gemini").ok)

    def test_low_ram_blocks_local_and_fallback_before_network(self):
        with patch("jarvis_ai.local_inference_ready",return_value=False), patch("jarvis_ai._local_urlopen") as network:
            self.assertIn("Local AI paused",ollama_reply([],[])[1])
            with patch.dict(os.environ,{"GEMINI_API_KEY":"private-marker","JARVIS_OLLAMA_FALLBACK":"on"}), patch("jarvis_ai._gemini_content",return_value=(None,("Service unavailable","service",True,503))):
                outcome=generate_reply_result([],[],provider="gemini")
                self.assertFalse(outcome.ok)
                self.assertIn("Local AI paused",outcome.text)
            network.assert_not_called()

    def test_dashboard_retry_replaces_failure_and_keeps_route(self):
        with tempfile.TemporaryDirectory() as folder, patch.object(memory_store,"DB_PATH",Path(folder)/"test.db"), patch("jarvis_ai.generate_reply_result",side_effect=[ReplyResult("Temporary failure",False,"gemini","service",True),ReplyResult("Recovered",True,"gemini")]) as reply, patch("voice_output.speak_button") as speak:
            app=AppTest.from_file(str(Path(__file__).resolve().parents[1]/"app.py"),default_timeout=15).run()
            app.chat_input[0].set_value("Nonpersonal fixture").run()
            self.assertFalse(app.exception)
            self.assertEqual(len(app.session_state["chat"]),2)
            speak.assert_not_called()
            app.session_state["provider_override"]="ollama"
            app.button(key="retry_reply").click().run()
            self.assertFalse(app.exception)
            self.assertEqual([m["content"] for m in app.session_state["chat"]],["Nonpersonal fixture","Recovered"])
            self.assertEqual(reply.call_args.kwargs["provider"],"gemini")
            self.assertEqual(reply.call_args.args[0],[{"role":"user","content":"Nonpersonal fixture"}])
