"""Regression checks for browser speech lifecycle event wiring.

These inspect the generated HTML; browser audio behavior needs separate
interactive testing with an installed local voice.
"""
import unittest

from voice_output import speech_markup


class SpeechLifecycleTests(unittest.TestCase):
    def test_native_pause_and_resume_emit_avatar_state_events(self):
        markup = speech_markup("Hello")
        pause_handler = markup.split("utterance.onpause = ", 1)[1].split("utterance.onresume = ", 1)[0]
        resume_handler = markup.split("utterance.onresume = ", 1)[1].split("utterance.onend = ", 1)[0]
        self.assertIn("stopPreview()", pause_handler)
        self.assertIn("detail:'paused'", pause_handler)
        self.assertIn("detail:'speaking'", resume_handler)
        self.assertIn("current !== utterance || stopped", pause_handler)
        self.assertIn("current !== utterance || stopped", resume_handler)

    def test_speech_text_cannot_inject_script_markup(self):
        markup = speech_markup("</script><script>alert(1)</script>")
        self.assertNotIn("</script><script>alert(1)", markup)
        self.assertIn("\\u003c", markup)


if __name__ == "__main__":
    unittest.main()
