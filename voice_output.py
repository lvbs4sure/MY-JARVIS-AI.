"""Opt-in browser speech playback with HTML-safe text rendering."""
import html
import json
import re
import streamlit as st


def speech_text(text):
    text = re.sub(r"```.*?```", " Code block omitted from speech. ", str(text), flags=re.S)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", text)
    text = re.sub(r"[*_`]+", "", text)
    return text[:12000]


def speech_markup(text: str, label: str = "🔊 Speak reply"):
    # Escape JS string and HTML markup independently.
    safe_text = json.dumps(speech_text(text), ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e")
    safe_label = html.escape(str(label)[:80], quote=True)
    markup = f"""<!doctype html><html><head><style>button,select {{font:inherit;color:#c6dbf4;background:#101a34;border:1px solid #6972a4;padding:6px;border-radius:5px;margin:2px}} label {{display:block}} select {{max-width:calc(100% - 70px)}} </style></head><body style="margin:0;background:transparent;color:#a9bddb;font:11px system-ui">
<button id="speak" style="font:inherit;color:#c6dbf4;background:#101a34;border:1px solid #6972a4;padding:6px 8px;border-radius:5px;cursor:pointer">{safe_label}</button>
<button id="stop" style="font:inherit;color:#c6dbf4;background:#101a34;border:1px solid #6972a4;padding:6px 8px;border-radius:5px;cursor:pointer">Interrupt speech</button>
<button id="pause">Pause</button><button id="resume">Resume</button>
<div role="img" aria-label="Speech activity preview, not phoneme accurate lip synchronization" style="width:112px;height:82px;margin:8px 0 4px;position:relative;border:1px solid #497aa0;border-radius:48%;background:radial-gradient(ellipse at center,#132b50,#050c19);box-shadow:0 0 16px #216aa766">
<div style="position:absolute;top:28px;left:25px;width:14px;height:3px;background:#7ad9ff;box-shadow:47px 0 #7ad9ff"></div>
<div id="mouth" style="position:absolute;left:39px;bottom:19px;width:34px;height:3px;border-radius:50%;background:#80e4ff;box-shadow:0 0 9px #62caff;transition:height 85ms ease,bottom 85ms ease"></div></div>
<div style="font:10px system-ui;color:#87a5c5">Speech activity preview · not exact lip-sync</div>
<br><label>Local voice <select id="voice" aria-label="Local voice"></select></label>
<label>Speed <select id="rate" aria-label="Speaking speed"><option value="0.8">Slow</option><option value="1" selected>Normal</option><option value="1.2">Fast</option></select></label>
<span id="status" role="status" aria-live="polite" style="margin-left:6px">Ready</span>
<script>
const message = {safe_text};
const status = document.getElementById('status');
const voiceMenu = document.getElementById('voice');
let localVoices = [];
function refreshVoices() {{
  const previous = voiceMenu.value;
  localVoices = speechSynthesis.getVoices().filter(voice => voice.localService);
  voiceMenu.replaceChildren();
  localVoices.forEach(voice => {{
    const option = document.createElement('option');
    option.value = voice.voiceURI;
    option.textContent = voice.name + ' (' + voice.lang + ')';
    voiceMenu.append(option);
  }});
  if (localVoices.some(voice => voice.voiceURI === previous)) voiceMenu.value = previous;
  else {{ const english = localVoices.find(voice => voice.lang.startsWith('en')); if (english) voiceMenu.value = english.voiceURI; }}
  if (!localVoices.length) status.textContent = 'No local voice available. No cloud voice will be used.';
  else if (status.textContent.startsWith('No local voice')) status.textContent = 'Ready';
}}
if ('speechSynthesis' in window) {{ refreshVoices(); speechSynthesis.addEventListener('voiceschanged', refreshVoices); }}
let current;
let stopped = false;
let previewTimer = null;
const mouth = document.getElementById('mouth');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let active = false;
function setMouth(open) {{
  mouth.style.height = (!active || reducedMotion.matches || !open) ? '3px' : '13px';
  mouth.style.bottom = (!active || reducedMotion.matches || !open) ? '19px' : '14px';
}}
function stopPreview() {{
  active = false;
  if (previewTimer !== null) clearTimeout(previewTimer);
  previewTimer = null;
  setMouth(false);
}}
function speechPulse() {{
  if (!active || reducedMotion.matches) return;
  setMouth(true);
  if (previewTimer !== null) clearTimeout(previewTimer);
  previewTimer = setTimeout(() => {{ previewTimer = null; setMouth(false); }}, 140);
}}
reducedMotion.addEventListener?.('change', () => {{ if (reducedMotion.matches) setMouth(false); }});

document.getElementById('speak').onclick = () => {{
  if (!('speechSynthesis' in window)) {{ status.textContent = 'Speech is unavailable in this browser.'; return; }}
  const selectedVoice = localVoices.find(voice => voice.voiceURI === voiceMenu.value);
  if (!selectedVoice) {{ status.textContent = 'Select an installed local voice first.'; return; }}
  current = null;
  speechSynthesis.cancel();
  stopPreview();
  stopped = false;
  const utterance = new SpeechSynthesisUtterance(message);
  current = utterance;
  utterance.voice = selectedVoice;
  utterance.lang = selectedVoice.lang;
  utterance.rate = Number(document.getElementById('rate').value);
  utterance.onstart = () => {{ if (current !== utterance || stopped) return; active = true; status.textContent = 'Speaking'; window.dispatchEvent(new CustomEvent('jarvis-speech',{{detail:'speaking'}})); }};
  utterance.onboundary = () => {{ if (current !== utterance || stopped || speechSynthesis.paused) return; speechPulse(); window.dispatchEvent(new CustomEvent('jarvis-boundary')); }};
  utterance.onpause = () => {{ if (current !== utterance || stopped) return; stopPreview(); status.textContent = 'Paused'; }};
  utterance.onresume = () => {{ if (current !== utterance || stopped) return; active = true; status.textContent = 'Speaking'; }};
  utterance.onend = () => {{ if (current !== utterance) return; current = null; stopPreview(); status.textContent = stopped ? 'Stopped' : 'Finished'; window.dispatchEvent(new CustomEvent('jarvis-speech',{{detail:'ready'}})); }};
  utterance.onerror = (event) => {{ if (current !== utterance) return; current = null; stopPreview(); status.textContent = stopped ? 'Stopped' : 'Speech error: ' + event.error; window.dispatchEvent(new CustomEvent('jarvis-speech',{{detail:'ready'}})); }};
  status.textContent = 'Starting…';
  speechSynthesis.speak(utterance);
}};
document.getElementById('pause').onclick = () => {{
  if ('speechSynthesis' in window && current && speechSynthesis.speaking && !speechSynthesis.paused) {{ speechSynthesis.pause(); stopPreview(); status.textContent = 'Paused'; window.dispatchEvent(new CustomEvent('jarvis-speech',{{detail:'paused'}})); }}
}};
document.getElementById('resume').onclick = () => {{
  if ('speechSynthesis' in window && current && !stopped && speechSynthesis.paused) {{ speechSynthesis.resume(); active = true; status.textContent = 'Speaking'; window.dispatchEvent(new CustomEvent('jarvis-speech',{{detail:'speaking'}})); }}
}};
window.addEventListener('pagehide', () => {{ current = null; stopped = true; if ('speechSynthesis' in window) speechSynthesis.cancel(); stopPreview(); }});
document.getElementById('stop').onclick = () => {{
  stopped = true;
  current = null;
  stopPreview();
  if ('speechSynthesis' in window) speechSynthesis.cancel();
  status.textContent = 'Stopped';
  window.dispatchEvent(new CustomEvent('jarvis-speech',{{detail:'ready'}}));
}};
</script></body></html>"""
    return markup


def speak_button(text: str, label: str = "🔊 Speak reply"):
    st.iframe(speech_markup(text,label), height=315, alt="Speak or stop this assistant reply")
