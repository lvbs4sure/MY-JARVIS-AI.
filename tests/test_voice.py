import unittest
from unittest.mock import patch
from voice_output import speak_button


class VoiceTests(unittest.TestCase):
    def render(self, text, label="🔊 Speak reply"):
        with patch("voice_output.st.iframe") as render:
            speak_button(text, label)
            render.assert_called_once()
            self.assertEqual(render.call_args.kwargs["height"], 85)
            return render.call_args.args[0]

    def test_escapes_script_tags_in_reply(self):
        markup = self.render("</script><script>alert('x')</script>")
        self.assertNotIn("</script><script>alert", markup)
        self.assertIn("\\u003c/script\\u003e", markup)
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


if __name__ == "__main__":
    unittest.main()
