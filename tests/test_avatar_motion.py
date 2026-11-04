"""Regression checks for lightweight holographic motion and accessibility."""
import unittest
from unittest.mock import patch

from ui_theme import CSS, render_avatar


class AvatarMotionTests(unittest.TestCase):
    def test_idle_motion_and_thinking_state(self):
        self.assertIn("@keyframes jarvis-presence", CSS)
        self.assertIn(".state-thinking .holo-presence", CSS)
        with patch("ui_theme.st.markdown") as markdown:
            render_avatar("thinking")
            markup = markdown.call_args.args[0]
            self.assertIn("state-thinking", markup)
            self.assertIn("holo-presence", markup)
            self.assertIn("JARVIS / PROCESSING YOUR REQUEST", markup)

    def test_reduced_motion_and_invalid_state(self):
        self.assertIn(".motion-off *{animation:none!important}", CSS)
        self.assertIn("@media(prefers-reduced-motion:reduce)", CSS)
        with patch("ui_theme.st.markdown") as markdown:
            render_avatar("unknown", reduced_motion=True)
            markup = markdown.call_args.args[0]
            self.assertIn("state-ready", markup)
            self.assertIn("motion-off", markup)
            self.assertIn('aria-hidden="true"', markup)


if __name__ == "__main__":
    unittest.main()
