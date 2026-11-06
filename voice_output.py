"""Opt-in browser speech playback with HTML-safe text rendering."""
import html
import json
import re
import streamlit.components.v1 as components


def speech_text(text):
    text = re.sub(r"```.*?```", " Code block omitted from speech. ", str(text), flags=re.S)
    text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"(?m)^\s{0,3}#{1,6}\s+", "", text)
    text = re.sub(r"[*_`]+", "", text)
    # Do not read executable or styling content aloud. Preserve encoded markup as text.
    text = re.sub(r"<(script|style|template|noscript|svg)\b[^>]*>.*?</\1\s*>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<!--.*?-->", " ", text, flags=re.S)
    # Decode entities only after removing tags so encoded markup remains spoken text.
    text = re.sub(r"</?[A-Za-z][A-Za-z0-9:-]*(?:\s[^>\n]*)?\s*/?>", " ", text)
    return html.unescape(text)[:12000]


def speech_markup(text: str, label: str = "🔊 Speak reply", *, auto_play: bool = False):
    # Escape JS string and HTML markup independently.
    safe_text = json.dumps(speech_text(text), ensure_ascii=True).replace("<", "\\u003c").replace(">", "\\u003e")
    safe_label = html.escape(str(label)[:80], quote=True)
    auto_start = "true" if auto_play else "false"
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
const autoStart = {auto_start};
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
  else {{ const lang = (navigator.language || 'en').toLowerCase().split('-')[0]; const preferred = localVoices.find(voice => voice.lang.toLowerCase().split('-')[0] === lang); if (preferred) voiceMenu.value = preferred.voiceURI; }}
  if (!localVoices.length) status.textContent = 'No local voice available. No cloud voice will be used.';
  else if (status.textContent.startsWith('No local voice')) status.textContent = 'Ready';
}}
if ('speechSynthesis' in window) {{ refreshVoices(); speechSynthesis.addEventListener?.('voiceschanged', refreshVoices); }}
let current = null;
let stopped = false;
let speechRequested = false;
let utteranceSequence = 0;
let previewTimer = null;
const mouth = document.getElementById('mouth');
const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
let active = false;
let speechState = 'ready';
function emitSpeechState(next) {{
  if (speechState === next) return;
  speechState = next;
  window.dispatchEvent(new CustomEvent('jarvis-speech',{{detail:next}}));
}}
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
  speechRequested = true;
  if (!('speechSynthesis' in window)) {{ status.textContent = 'Speech is unavailable in this browser.'; return; }}
  // Recheck the browser's current local voices before every request. A removed
  // or newly cloud-backed voice must not be trusted from a cached selection.
  refreshVoices();
  const selectedVoice = localVoices.find(voice => voice.voiceURI === voiceMenu.value);
  if (!selectedVoice) {{ status.textContent = 'Select an installed local voice first.'; return; }}
  if (!message.trim()) {{ status.textContent = 'No spoken text in this reply.'; return; }}
  // Do not cancel another page component's speech when JARVIS is idle.
  const ownedSpeech = current !== null;
  current = null;
  if (ownedSpeech) speechSynthesis.cancel();
  stopPreview();
  stopped = false;
  const utterance = new SpeechSynthesisUtterance(message);
  const utteranceId = ++utteranceSequence;
  let utteranceStartedAtMs = null;
  let lastBoundaryElapsedSeconds = -1;
  let lastBoundaryCharIndex = -1;
  current = utterance;
  utterance.voice = selectedVoice;
  utterance.lang = selectedVoice.lang;
  const requestedRate = Number(document.getElementById('rate').value);
  utterance.rate = Number.isFinite(requestedRate) ? Math.max(0.5, Math.min(2, requestedRate)) : 1;
  utterance.onstart = () => {{ if (current !== utterance || stopped) return; active = true; utteranceStartedAtMs = performance.now(); status.textContent = 'Speaking'; emitSpeechState('speaking'); }};
  utterance.onboundary = (event) => {{ if (current !== utterance || stopped || !active || !speechSynthesis.speaking || speechSynthesis.paused) return; if (!Number.isInteger(event.charIndex) || event.charIndex < 0 || event.charIndex >= message.length || event.charIndex <= lastBoundaryCharIndex) return; if (Number.isFinite(event.elapsedTime) && event.elapsedTime >= 0) {{ if (event.elapsedTime < lastBoundaryElapsedSeconds) return; lastBoundaryElapsedSeconds = event.elapsedTime; }} lastBoundaryCharIndex = event.charIndex; speechPulse(); window.dispatchEvent(new CustomEvent('jarvis-boundary', {{detail: {{utteranceId, utteranceStartedAtMs, charIndex: Number.isInteger(event.charIndex) && event.charIndex >= 0 && event.charIndex < message.length ? event.charIndex : null, charLength: Number.isInteger(event.charLength) && event.charLength >= 0 && Number.isInteger(event.charIndex) && event.charIndex >= 0 && event.charIndex < message.length && event.charIndex + event.charLength <= message.length ? event.charLength : null, boundaryName: typeof event.name === 'string' ? event.name : null, elapsedTime: Number.isFinite(event.elapsedTime) && event.elapsedTime >= 0 ? event.elapsedTime : null, speechRate: utterance.rate, textLength: message.length, observedAtMs: performance.now(), audioElapsedSeconds: Number.isFinite(event.elapsedTime) && event.elapsedTime >= 0 ? event.elapsedTime : null}}}})); }};
  utterance.onpause = () => {{ if (current !== utterance || stopped) return; stopPreview(); status.textContent = 'Paused'; emitSpeechState('paused'); }};
  utterance.onresume = () => {{ if (current !== utterance || stopped) return; active = true; status.textContent = 'Speaking'; emitSpeechState('speaking'); }};
  utterance.onend = () => {{ if (current !== utterance) return; current = null; stopPreview(); status.textContent = stopped ? 'Stopped' : 'Finished'; emitSpeechState('ready'); }};
  utterance.onerror = (event) => {{ if (current !== utterance) return; current = null; stopPreview(); status.textContent = stopped ? 'Stopped' : 'Speech error: ' + String(event.error || 'unknown'); emitSpeechState('ready'); }};
  status.textContent = 'Starting…';
  try {{ speechSynthesis.speak(utterance); }} catch (error) {{ if (current === utterance) {{ current = null; stopPreview(); status.textContent = 'Speech could not start'; emitSpeechState('ready'); }} }}
}};
if (autoStart && 'speechSynthesis' in window) {{
  let attemptedAutoStart = false;
  const tryAutoStart = () => {{
    if (attemptedAutoStart || speechRequested || stopped || current) return;
    refreshVoices();
    if (!localVoices.length) {{ status.textContent = 'Waiting for an installed local voice. You can press Speak manually.'; return; }}
    attemptedAutoStart = true;
    document.getElementById('speak').click();
  }};
  window.addEventListener('load', tryAutoStart, {{once:true}});
  speechSynthesis.addEventListener?.('voiceschanged', tryAutoStart);
}}
document.getElementById('pause').onclick = () => {{
  if ('speechSynthesis' in window && current && speechSynthesis.speaking && !speechSynthesis.paused) {{ speechSynthesis.pause(); stopPreview(); status.textContent = 'Paused'; emitSpeechState('paused'); }}
}};
document.getElementById('resume').onclick = () => {{
  if ('speechSynthesis' in window && current && !stopped && speechSynthesis.paused) {{ speechSynthesis.resume(); active = true; status.textContent = 'Speaking'; emitSpeechState('speaking'); }}
}};
window.addEventListener('pagehide', () => {{ const ownedSpeech = current !== null; current = null; stopped = true; if (ownedSpeech && 'speechSynthesis' in window) speechSynthesis.cancel(); stopPreview(); emitSpeechState('ready'); }});
document.getElementById('stop').onclick = () => {{
  const ownedSpeech = current !== null;
  stopped = true;
  current = null;
  stopPreview();
  if (ownedSpeech && 'speechSynthesis' in window) speechSynthesis.cancel();
  status.textContent = 'Stopped';
  emitSpeechState('ready');
}};
</script></body></html>"""
    return markup


def speak_button(text: str, label: str = "🔊 Speak reply", *, auto_play: bool = False):
    components.html(speech_markup(text,label,auto_play=auto_play), height=315, scrolling=True)
