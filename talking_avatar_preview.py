"""Opt-in original humanoid preview. Does not change the default avatar."""
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

_PREVIEW = Path(__file__).resolve().parent / "previews" / "talking_avatar_preview.html"


def render_talking_avatar_preview():
    """Embed the standalone local-only demo, without injecting chat or memory."""
    st.caption("Experimental original humanoid preview · local browser speech · approximate mouth motion")
    try:
        html = _PREVIEW.read_text(encoding="utf-8")
    except OSError:
        st.warning("Talking-avatar preview file is missing. Switch to Holographic scene.")
        return
    components.html(html, height=760, scrolling=True)
