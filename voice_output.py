"""Opt-in browser text-to-speech. The user clicks Speak; no auto-play."""
import json
import streamlit.components.v1 as components


def speak_button(text: str, label: str = "🔊 Speak reply"):
    # JSON string encoding prevents assistant text from becoming executable JavaScript.
    text_json = json.dumps(text[:12000]).replace("<", "\\u003c").replace(">", "\\u003e")
    label_json = json.dumps(label)
    html = f"""<!doctype html><html><body style="margin:0">
<button id="speak" style="font:inherit;padding:9px 14px;border-radius:9px;cursor:pointer">{label_json[1:-1]}</button>
<button id="stop" style="font:inherit;padding:9px 14px;border-radius:9px;cursor:pointer">Stop</button>
<script>
const message = {text_json};
document.getElementById('speak').onclick = () => {{
  if (!('speechSynthesis' in window)) return;
  speechSynthesis.cancel();
  const utterance = new SpeechSynthesisUtterance(message);
  utterance.rate = 1;
  speechSynthesis.speak(utterance);
}};
document.getElementById('stop').onclick = () => speechSynthesis.cancel();
</script></body></html>"""
    components.html(html, height=55)
