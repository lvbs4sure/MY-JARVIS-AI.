import unittest
from unittest.mock import patch
from voice_output import speak_button


class VoiceTests(unittest.TestCase):
    def test_escapes_script_tags_in_reply(self):
        with patch("voice_output.components.html") as render:
            speak_button("</script><script>alert('x')</script>")
            html = render.call_args.args[0]
            self.assertNotIn("</script><script>alert", html)
            self.assertIn("speechSynthesis", html)


if __name__ == "__main__":
    unittest.main()
