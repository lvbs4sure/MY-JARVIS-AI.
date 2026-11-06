"""Regression contract for the standalone, original talking-avatar preview.

This checks shipped HTML and JS structure without requiring a browser, audio
device, external API, or user data. Real Windows speech tests remain necessary.
"""
from html.parser import HTMLParser
from pathlib import Path
import unittest

PREVIEW = Path(__file__).resolve().parents[1] / "previews" / "talking_avatar_preview.html"


class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = {}
        self.scripts = []
        self._script = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if "id" in attributes:
            self.ids[attributes["id"]] = (tag, attributes)
        if tag == "script":
            self._script = True

    def handle_endtag(self, tag):
        if tag == "script":
            self._script = False

    def handle_data(self, data):
        if self._script:
            self.scripts.append(data)


class TalkingAvatarPreviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = PREVIEW.read_text(encoding="utf-8")
        cls.document = Elements()
        cls.document.feed(cls.source)
        cls.script = "\n".join(cls.document.scripts)

    def test_standalone_avatar_and_accessible_status(self):
        self.assertIn('viewBox="0 0 480 510"', self.source)
        self.assertIn('aria-label="Original cyan and violet holographic humanoid bust', self.source)
        self.assertEqual(self.document.ids["status"][0], "div")
        self.assertEqual(self.document.ids["status"][1].get("aria-live"), "polite")
        for control in ("speak", "pause", "resume", "stop", "voice"):
            self.assertIn(control, self.document.ids)

    def test_opt_in_speech_and_local_voice_only(self):
        self.assertIn("speak.onclick=", self.script)
        self.assertIn("new SpeechSynthesisUtterance(", self.script)
        self.assertIn("v.localService===true", self.script)
        self.assertIn("if(!selected)", self.script)
        self.assertNotIn("speechSynthesis.speak(", self.script.split("speak.onclick=")[0])
        for prohibited in ("getUserMedia(", "fetch(", "XMLHttpRequest", "WebSocket("):
            self.assertNotIn(prohibited, self.script)

    def test_speech_state_cleanup_and_reduced_motion(self):
        for marker in (
            "utterance.onboundary=", "utterance.onend=", "utterance.onerror=",
            "pause.onclick=", "resume.onclick=", "stop.onclick=",
            "closeMouth()", "speechSynthesis.cancel()",
            "prefers-reduced-motion: reduce", "document.hidden",
        ):
            self.assertIn(marker, self.source)
        self.assertIn("if(token===run", self.script)

    def test_no_remote_runtime_assets(self):
        for prohibited in ("<iframe", "<img", "<audio", "<video", "<link", "src=\"http", "href=\"http"):
            self.assertNotIn(prohibited, self.source.lower())


if __name__ == "__main__":
    unittest.main()
