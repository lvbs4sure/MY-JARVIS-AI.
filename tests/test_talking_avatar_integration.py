"""Verify opt-in talking avatar is wired without replacing the default."""
import unittest
from pathlib import Path
from unittest.mock import patch

import talking_avatar_preview

ROOT = Path(__file__).resolve().parents[1]


class TalkingAvatarIntegrationTests(unittest.TestCase):
    def test_default_remains_original_scene(self):
        app = (ROOT / "app.py").read_text(encoding="utf-8")
        self.assertIn('st.session_state.get("avatar_style", "Holographic scene")', app)
        self.assertIn('"Talking humanoid preview"', app)
        self.assertIn('if avatar_style!="Talking humanoid preview":', app)
        self.assertIn("render_talking_avatar_preview(latest_reply)", app)

    def test_render_embeds_local_html_only(self):
        with patch("talking_avatar_preview.st.caption"), patch(
            "talking_avatar_preview.components.html"
        ) as render:
            talking_avatar_preview.render_talking_avatar_preview()
        markup = render.call_args.args[0]
        self.assertIn("SpeechSynthesisUtterance", markup)
        self.assertEqual(render.call_args.kwargs["height"], 760)

    def test_reply_is_embedded_as_escaped_data_without_autoplay(self):
        with patch("talking_avatar_preview.st.caption"), patch(
            "talking_avatar_preview.components.html"
        ) as render:
            talking_avatar_preview.render_talking_avatar_preview("</script><script>alert(1)</script>")
        markup = render.call_args.args[0]
        self.assertNotIn("</script><script>alert(1)</script>", markup)
        self.assertIn("window.JARVIS_PREVIEW_REPLY =", markup)
        self.assertIn("u003c", markup)
        self.assertIn("speak.onclick=", markup)

    def test_missing_preview_fails_safely(self):
        with patch.object(talking_avatar_preview, "_PREVIEW", ROOT / "nonexistent-preview.html"), patch(
            "talking_avatar_preview.st.caption"
        ), patch("talking_avatar_preview.st.warning") as warning, patch(
            "talking_avatar_preview.components.html"
        ) as render:
            talking_avatar_preview.render_talking_avatar_preview()
        warning.assert_called_once()
        render.assert_not_called()


if __name__ == "__main__":
    unittest.main()
