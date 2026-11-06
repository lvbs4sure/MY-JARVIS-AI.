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

    def test_boundary_event_exposes_timing_without_claiming_phoneme_sync(self):
        markup = speech_markup("Hello")
        handler = markup.split("utterance.onboundary = ", 1)[1].split("utterance.onpause = ", 1)[0]
        self.assertIn("utterance.onboundary = (event) =>", markup)
        self.assertIn("current !== utterance || stopped || !active || !speechSynthesis.speaking || speechSynthesis.paused", handler)
        self.assertIn("if (!Number.isInteger(event.charIndex) || event.charIndex < 0 || event.charIndex >= message.length) return;", handler)
        self.assertIn("let lastBoundaryCharIndex = -1;", markup)
        self.assertIn("event.charIndex <= lastBoundaryCharIndex", handler)
        self.assertIn("lastBoundaryCharIndex = event.charIndex; speechPulse();", handler)
        self.assertIn("if (event.elapsedTime < lastBoundaryElapsedSeconds) return;", handler)
        self.assertIn("lastBoundaryElapsedSeconds = event.elapsedTime;", handler)
        # A boundary callback before onstart must not drive a mouth preview.
        self.assertIn("active = true; status.textContent = 'Speaking'", markup)
        self.assertIn("charIndex: Number.isInteger(event.charIndex) && event.charIndex >= 0 && event.charIndex < message.length ? event.charIndex : null", handler)
        self.assertIn("charLength: Number.isInteger(event.charLength) && event.charLength >= 0 && Number.isInteger(event.charIndex) && event.charIndex >= 0 && event.charIndex < message.length && event.charIndex + event.charLength <= message.length ? event.charLength : null", handler)
        self.assertIn("boundaryName: typeof event.name === 'string' ? event.name : null", handler)
        self.assertIn("elapsedTime: Number.isFinite(event.elapsedTime) && event.elapsedTime >= 0 ? event.elapsedTime : null", handler)
        self.assertIn("speechRate: utterance.rate", handler)
        self.assertIn("textLength: message.length", handler)
        self.assertIn("new CustomEvent('jarvis-boundary'", handler)
        self.assertIn("not exact lip-sync", markup)

    def test_auto_speech_requires_explicit_opt_in(self):
        self.assertIn("const autoStart = false;", speech_markup("Hello"))
        enabled = speech_markup("Hello", auto_play=True)
        self.assertIn("const autoStart = true;", enabled)
        self.assertIn("if (autoStart && 'speechSynthesis' in window)", enabled)
        self.assertIn("if (!localVoices.length)", enabled)
        self.assertIn("Select an installed local voice first.", enabled)

    def test_autoplay_waits_for_local_voice_without_cloud_fallback(self):
        markup = speech_markup("Hello", auto_play=True)
        self.assertIn("if (!localVoices.length)", markup)
        self.assertIn("attemptedAutoStart = true;", markup)
        self.assertIn("Waiting for an installed local voice", markup)
        self.assertIn("voice.localService", markup)

    def test_autoplay_does_not_register_on_unsupported_browsers(self):
        markup = speech_markup("Hello", auto_play=True)
        self.assertIn("if (autoStart && 'speechSynthesis' in window) {", markup)
        self.assertIn("if (!('speechSynthesis' in window))", markup)
        # A browser without the speechSynthesis global must not attempt
        # to register its voiceschanged callback during page initialization.
        autoplay = markup.split("if (autoStart && 'speechSynthesis' in window) {", 1)[1]
        self.assertIn("speechSynthesis.addEventListener?.('voiceschanged', tryAutoStart)", autoplay)

    def test_stop_prevents_delayed_autoplay_when_voices_arrive(self):
        markup = speech_markup("Hello", auto_play=True)
        autoplay = markup.split("const tryAutoStart = () => {", 1)[1].split("window.addEventListener('load'", 1)[0]
        self.assertIn("if (attemptedAutoStart || speechRequested || stopped || current) return;", autoplay)
        self.assertIn("speechSynthesis.addEventListener?.('voiceschanged', tryAutoStart)", markup)
        stop = markup.split("document.getElementById('stop').onclick = () => {", 1)[1]
        self.assertIn("stopped = true;", stop)

    def test_delayed_voice_discovery_does_not_restart_manual_speech(self):
        markup = speech_markup("Hello", auto_play=True)
        autoplay = markup.split("const tryAutoStart = () => {", 1)[1].split("window.addEventListener('load'", 1)[0]
        self.assertIn("if (attemptedAutoStart || speechRequested || stopped || current) return;", autoplay)
        self.assertIn("current = utterance;", markup)
        self.assertIn("speechSynthesis.addEventListener?.('voiceschanged', tryAutoStart)", markup)

    def test_manual_speech_completion_cannot_trigger_delayed_autoplay(self):
        markup = speech_markup("Hello", auto_play=True)
        speak = markup.split("document.getElementById('speak').onclick = () => {", 1)[1].split("if (!('speechSynthesis' in window))", 1)[0]
        autoplay = markup.split("const tryAutoStart = () => {", 1)[1].split("window.addEventListener('load'", 1)[0]
        self.assertIn("speechRequested = true;", speak)
        self.assertIn("if (attemptedAutoStart || speechRequested || stopped || current) return;", autoplay)
        # current is cleared on completion; the persistent request flag prevents
        # voiceschanged from unexpectedly starting another utterance.
        self.assertIn("current = null; stopPreview();", markup)

    def test_pagehide_resets_speech_state_for_avatar_listeners(self):
        markup = speech_markup("Hello")
        handler = markup.split("window.addEventListener('pagehide',", 1)[1].split("document.getElementById('stop').onclick", 1)[0]
        self.assertIn("speechSynthesis.cancel()", handler)
        self.assertIn("stopPreview()", handler)
        self.assertIn("emitSpeechState('ready')", handler)

    def test_local_voice_prefers_browser_language(self):
        markup = speech_markup("Bonjour")
        self.assertIn("navigator.language", markup)
        self.assertIn("voice.lang.toLowerCase().split", markup)
        self.assertIn("voice.localService", markup)

    def test_speech_text_cannot_inject_script_markup(self):
        markup = speech_markup("</script><script>alert(1)</script>")
        self.assertNotIn("</script><script>alert(1)", markup)
        self.assertIn('const message = "  ";', markup)


if __name__ == "__main__":
    unittest.main()
