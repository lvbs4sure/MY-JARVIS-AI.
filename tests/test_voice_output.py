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
        self.assertIn("emitSpeechState('paused')", pause_handler)
        self.assertIn("emitSpeechState('speaking')", resume_handler)
        self.assertIn("current !== utterance || stopped", pause_handler)
        self.assertIn("current !== utterance || stopped", resume_handler)

    def test_failed_speech_start_resets_avatar_state(self):
        markup = speech_markup("Hello")
        failure_handler = markup.split("try { speechSynthesis.speak(utterance); } catch (error) {", 1)[1].split("};", 1)[0]
        self.assertIn("current = null", failure_handler)
        self.assertIn("stopPreview()", failure_handler)
        self.assertIn("emitSpeechState('ready')", failure_handler)

    def test_speech_state_events_are_deduplicated(self):
        markup = speech_markup('Hello')
        emitter = markup.split('function emitSpeechState(next) {', 1)[1].split('function setMouth', 1)[0]
        self.assertIn('if (speechState === next) return;', emitter)
        self.assertIn('speechState = next;', emitter)
        self.assertIn("new CustomEvent('jarvis-speech',{detail:next})", emitter)
        self.assertIn("emitSpeechState('paused')", markup)
        self.assertIn("emitSpeechState('speaking')", markup)
        self.assertIn("emitSpeechState('ready')", markup)

    def test_speech_text_cannot_inject_script_markup(self):
        markup = speech_markup("</script><script>alert(1)</script>")
        self.assertNotIn("</script><script>alert(1)", markup)
        self.assertIn("\\u003c", markup)


if __name__ == "__main__":
    unittest.main()
