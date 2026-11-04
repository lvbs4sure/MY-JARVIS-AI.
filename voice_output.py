"""Opt-in browser speech playback with HTML-safe text rendering."""
import html
import json
import streamlit as st


def speak_button(text: str, label: str = "🔊 Speak reply"):
    # Escape JS string and HTML markup independently.
    safe_text = json.dumps(str(text)[:12000], ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e")
    safe_label = html.escape(str(label)[:80], quote=True)
    markup = f"""<!doctype html><html><body style="margin:0">
<button id="speak" style="font:inherit;padding:9px 14px;border-radius:9px;cursor:pointer">{safe_label}</button>
<button id="stop" style="font:inherit;padding:9px 14px;border-radius:9px;cursor:pointer">Stop</button>
<span id="status" role="status" aria-live="polite" style="font:14px sans-serif;margin-left:8px">Ready</span>
<script>
const message = {safe_text};
const status = document.getElementById('status');
let current;
let stopped = false;
document.getElementById('speak').onclick = () => {{
  if (!('speechSynthesis' in window)) {{ status.textContent = 'Speech is unavailable in this browser.'; return; }}
  speechSynthesis.cancel();
  stopped = false;
  const utterance = new SpeechSynthesisUtterance(message);
  current = utterance;
  utterance.rate = 1;
  utterance.onstart = () => {{ status.textContent = 'Speaking'; }};
  utterance.onend = () => {{ status.textContent = stopped ? 'Stopped' : 'Finished'; }};
  utterance.onerror = (event) => {{ status.textContent = stopped ? 'Stopped' : 'Speech error: ' + event.error; }};
  status.textContent = 'Starting…';
  speechSynthesis.speak(utterance);
}};
document.getElementById('stop').onclick = () => {{
  stopped = true;
  if ('speechSynthesis' in window) speechSynthesis.cancel();
  status.textContent = 'Stopped';
}};
</script></body></html>"""
    st.iframe(markup, height=85, alt="Speak or stop this assistant reply")
