import unittest
from unittest.mock import patch

from activity_log import record_activity, reply_failed
from ui_theme import render_avatar, render_side_panels


class ActivityTests(unittest.TestCase):
    def test_history_is_bounded_and_records_only_action_metadata(self):
        state = {}
        for index in range(40):
            record_activity(state, f"Action {index}")
        self.assertEqual(len(state["activity"]), 30)
        self.assertEqual(state["activity"][0]["action"], "Action 10")
        self.assertEqual(set(state["activity"][0]), {"time", "action", "outcome"})

    def test_errors_not_labelled_as_successful_replies(self):
        self.assertTrue(reply_failed("Gemini API error (HTTP 503)."))
        self.assertTrue(reply_failed("Local Ollama unavailable (URLError)."))
        self.assertFalse(reply_failed("Hello from JARVIS"))
        self.assertFalse(reply_failed("[Local Ollama fallback: Gemini is temporarily unavailable.]\n\nHello"))

    def test_panels_escape_content_and_do_not_invent_activity(self):
        with patch("ui_theme.st.markdown") as render:
            render_side_panels("<script>", 0, 0, [])
        markup = render.call_args.args[0]
        self.assertNotIn("<SCRIPT>", markup)
        self.assertIn("No actions in this session", markup)

    def test_avatar_limits_states_and_honours_reduced_motion(self):
        with patch("ui_theme.st.markdown") as render:
            render_avatar('<script>', reduced_motion=True)
        markup = render.call_args.args[0]
        self.assertIn("state-ready motion-off", markup)
        self.assertNotIn("<script>", markup)
