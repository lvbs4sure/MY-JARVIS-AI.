"""Regression checks for lightweight holographic motion and accessibility."""
import unittest
from unittest.mock import patch

from ui_theme import CSS, render_avatar
from animated_avatar import moving_face_markup, render_moving_face


class AvatarMotionTests(unittest.TestCase):
    def test_talking_face_uses_speech_events_and_opt_in_playback(self):
        markup = moving_face_markup("Hello", auto_play=True)
        self.assertIn("const autoStart = true;", markup)
        self.assertIn("jarvis-boundary", markup)
        self.assertIn("jarvis-speech", markup)
        self.assertIn("face.dataset.mouth", markup)
        self.assertIn("const autoStart = false;", moving_face_markup("Hello"))
        with patch("animated_avatar.components.html") as html:
            render_moving_face("Hello", auto_play=True)
            self.assertEqual(html.call_args.kwargs["height"], 580)

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
