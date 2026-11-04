"""Opt-in browser speech playback with HTML-safe text rendering."""
import html
import json
import streamlit.components.v1 as components


def speak_button(text: str, label: str = "🔊 Speak reply"):
    # Escape JS string and HTML markup independently.
    safe_text = json.dumps(str(text)[:12000], ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e")
    safe_label = html.escape(str(label)[:80], quote=True)
    markup = f"""<!doctype html><html><body style="margin:0">
<button id="speak" style="font:inherit;padding:9px 14px;border-radius:9px;cursor:pointer">{safe_label}</button>
<button id="stop" style="font:inherit;padding:9px 14px;border-radius:9px;cursor:pointer">Stop</button>
<script>
const message = {safe_text};
document.getElementById('speak').onclick = () => {{
  if (!('speechSynthesis' in window)) return;
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(message);
  utterance.rate = 1;
  speechSynthesis.speak(utterance);
}};
document.getElementById('stop').onclick = () => speechSynthesis.cancel();
</script></body></html>"""
    components.html(markup, height=55)
