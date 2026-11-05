"""Opt-in original humanoid preview. Does not change the default avatar."""
import json
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
from voice_output import speech_text

_PREVIEW = Path(__file__).resolve().parent / "previews" / "talking_avatar_preview.html"
_MARKER = "window.JARVIS_PREVIEW_REPLY = null;"


def render_talking_avatar_preview(reply=""):
    """Embed local-only speech preview; never automatically play or transmit a reply."""
    st.caption("Experimental original humanoid preview · local browser speech · approximate mouth motion")
    try:
        html = _PREVIEW.read_text(encoding="utf-8")
    except OSError:
        st.warning("Talking-avatar preview file is missing. Switch to Holographic scene.")
        return
    if _MARKER not in html:
        st.warning("Talking-avatar preview version mismatch. Switch to Holographic scene.")
        return
    safe_reply = json.dumps(speech_text(reply or ""), ensure_ascii=True)
    safe_reply = (safe_reply.replace("<", "\\u003c").replace(">", "\\u003e")
                 .replace("&", "\\u0026"))
    html = html.replace(_MARKER, "window.JARVIS_PREVIEW_REPLY = " + safe_reply + ";", 1)
    components.html(html, height=760, scrolling=True)
