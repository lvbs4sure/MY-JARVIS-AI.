import unittest
from unittest.mock import patch
from voice_output import speak_button


class VoiceTests(unittest.TestCase):
    def render(self, text, label="🔊 Speak reply"):
        with patch("voice_output.components.html") as render:
            speak_button(text, label)
            render.assert_called_once()
            self.assertEqual(render.call_args.kwargs["height"], 315)
            self.assertTrue(render.call_args.kwargs["scrolling"])
            return render.call_args.args[0]

    def test_escapes_script_tags_in_reply(self):
        markup = self.render("</script><script>alert('x')</script>")
        self.assertNotIn("</script><script>alert", markup)
        self.assertNotIn("<script>alert(", markup)
        self.assertIn("speechSynthesis", markup)

    def test_escapes_html_in_button_label(self):
        markup = self.render("Hello", '<img src=x onerror="alert(1)">')
        self.assertNotIn('<img src=x', markup)
        self.assertIn("&lt;img", markup)

    def test_escapes_quotes_and_unicode(self):
        markup = self.render('He said "hello" — JARVIS')
        self.assertIn("SpeechSynthesisUtterance", markup)
        self.assertIn("\\u2014", markup)

    def test_playback_requires_click_and_can_be_stopped(self):
        markup = self.render("Hello")
        self.assertIn("document.getElementById('speak').onclick", markup)
        self.assertIn("document.getElementById('stop').onclick", markup)
        self.assertIn("speechSynthesis.cancel()", markup)
        self.assertNotIn("autoplay", markup.lower())

    def test_caps_long_speech_text(self):
        markup = self.render("z" * 15000)
        self.assertIn("z" * 12000, markup)
        self.assertNotIn("z" * 12001, markup)

    def test_speech_status_distinguishes_stop_from_failure(self):
        markup = self.render("Hello")
        self.assertIn("stopped ? 'Stopped'", markup)
        self.assertIn("utterance.onstart", markup)
        self.assertIn("utterance.onend", markup)
        self.assertIn("aria-live", markup)

    def test_only_local_voices_and_playback_controls(self):
        markup = self.render("Hello")
        self.assertIn("voice.localService", markup)
        self.assertIn("utterance.voice = selectedVoice", markup)
        self.assertIn("speechSynthesis.pause()", markup)
        self.assertIn("speechSynthesis.resume()", markup)
        self.assertIn("Speaking speed", markup)
        self.assertNotIn("fetch(", markup)

    def test_speech_preview_stops_on_all_exit_paths(self):
        markup = self.render("Hello")
        self.assertIn("function stopPreview()", markup)
        self.assertIn("utterance.onend = () => { if (current !== utterance) return; current = null; stopPreview();", markup)
        self.assertIn("utterance.onerror = (event) => { if (current !== utterance) return; current = null; stopPreview();", markup)
        self.assertIn("speechSynthesis.pause(); stopPreview();", markup)
        self.assertIn("stopped = true;\n  current = null;\n  stopPreview();", markup)
        self.assertIn("prefers-reduced-motion: reduce", markup)
        self.assertIn("not exact lip-sync", markup)

    def test_stale_speech_callbacks_are_ignored(self):
        markup = self.render("Hello")
        self.assertIn("if (current !== utterance || stopped) return;", markup)
        self.assertIn("if (current !== utterance) return; current = null;", markup)
        self.assertIn("current = null;\n  speechSynthesis.cancel();", markup)
        self.assertIn("current = null; stopped = true;", markup)

    def test_native_pause_resume_and_paused_boundaries(self):
        markup = self.render("Hello")
        self.assertIn("utterance.onpause = () =>", markup)
        self.assertIn("utterance.onresume = () =>", markup)
        self.assertIn("stopped || !active || !speechSynthesis.speaking || speechSynthesis.paused", markup)
        self.assertIn("speechSynthesis.speaking && !speechSynthesis.paused", markup)
        self.assertIn("current && !stopped && speechSynthesis.paused", markup)

    def test_speech_startup_failure_does_not_leave_preview_active(self):
        markup = self.render("Hello")
        self.assertIn("try { speechSynthesis.speak(utterance); } catch (error)", markup)
        self.assertIn("status.textContent = 'Speech could not start'", markup)
        self.assertIn("speechSynthesis.addEventListener?.('voiceschanged'", markup)

    def test_empty_speech_and_missing_browser_error_code(self):
        markup = self.render("Hello")
        self.assertIn("if (!message.trim())", markup)
        self.assertIn("No spoken text in this reply.", markup)
        self.assertIn("String(event.error || 'unknown')", markup)

    def test_rate_is_bounded_before_browser_playback(self):
        markup = self.render("Hello")
        self.assertIn("Number.isFinite(requestedRate)", markup)
        self.assertIn("Math.max(0.5, Math.min(2, requestedRate))", markup)

    def test_invalid_browser_boundary_is_discarded_before_dispatch(self):
        markup = self.render("Hello")
        self.assertIn("event.charIndex >= message.length || event.charIndex <= lastBoundaryCharIndex) return; if (Number.isFinite(event.elapsedTime)", markup)
        self.assertIn("lastBoundaryElapsedSeconds) return; lastBoundaryElapsedSeconds = event.elapsedTime; } lastBoundaryCharIndex = event.charIndex; speechPulse(); window.dispatchEvent", markup)
        self.assertIn("if (current !== utterance || stopped || !active || !speechSynthesis.speaking || speechSynthesis.paused) return;", markup)

    def test_duplicate_speech_boundaries_are_ignored(self):
        markup = self.render("Hello")
        self.assertIn("event.charIndex <= lastBoundaryCharIndex) return;", markup)
        self.assertIn("lastBoundaryCharIndex = event.charIndex; speechPulse();", markup)

    def test_boundary_exposes_observation_and_audio_elapsed_times(self):
        markup = self.render("Hello")
        self.assertIn("observedAtMs: performance.now()", markup)
        self.assertIn("audioElapsedSeconds: Number.isFinite(event.elapsedTime)", markup)
        self.assertIn("event.elapsedTime >= 0 ? event.elapsedTime : null", markup)

    def test_manual_speech_disables_late_autostart(self):
        from voice_output import speech_markup
        markup = speech_markup("Hello", auto_play=True)
        self.assertIn("let speechRequested = false;", markup)
        self.assertIn("document.getElementById('speak').onclick = () => {\n  speechRequested = true;", markup)
        self.assertIn("attemptedAutoStart || speechRequested || stopped || current", markup)

    def test_speech_removes_markup_without_losing_image_description(self):
        from voice_output import speech_text
        self.assertEqual(
            speech_text("See ![blue avatar](https://example.com/a.png) &amp; <b>listen</b>"),
            "See blue avatar &  listen ",
        )
        self.assertEqual(speech_text("&lt;safe&gt;"), "<safe>")

    def test_comparison_symbols_are_spoken_not_mistaken_for_html(self):
        from voice_output import speech_text
        self.assertEqual(speech_text("2 < 3 and 5 > 4"), "2 < 3 and 5 > 4")
        self.assertEqual(speech_text("A < B > C"), "A < B > C")
        self.assertEqual(speech_text("<b>Hi</b> <script>alert(1)</script>"), " Hi   ")

    def test_hidden_html_is_not_spoken(self):
        from voice_output import speech_text
        spoken = speech_text("Hello <script>steal()</script><style>body{display:none}</style><!-- secret --> world")
        self.assertNotIn("steal()", spoken)
        self.assertNotIn("display:none", spoken)
        self.assertNotIn("secret", spoken)
        self.assertIn("Hello", spoken)
        self.assertIn("world", spoken)

    def test_hidden_template_svg_and_noscript_are_not_spoken(self):
        from voice_output import speech_text
        spoken = speech_text(
            "Hello <template>private draft</template>"
            "<svg><text>internal label</text></svg>"
            "<noscript>fallback code</noscript> world"
        )
        self.assertNotIn("private draft", spoken)
        self.assertNotIn("internal label", spoken)
        self.assertNotIn("fallback code", spoken)
        self.assertIn("Hello", spoken)
        self.assertIn("world", spoken)

    def test_markdown_is_natural_speech(self):
        from voice_output import speech_text
        self.assertEqual(speech_text("## Hello **friend** [guide](https://example.com)"), "Hello friend guide")
        self.assertNotIn("dangerous()", speech_text("```python\ndangerous()\n```"))


if __name__ == "__main__":
    unittest.main()
