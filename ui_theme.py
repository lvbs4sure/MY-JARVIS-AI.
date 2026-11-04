"""Original JARVIS command-centre visual layer. No external assets or network calls."""
import streamlit as st

CSS = """
<style>
:root {color-scheme: dark;}
.stApp {background: radial-gradient(ellipse at 55% -20%,#163650 0%,#081522 37%,#050b13 85%);color:#e7f7ff;}
[data-testid="stHeader"] {background:transparent;}
[data-testid="stSidebar"] {background:linear-gradient(180deg,#091d2c,#07111d);border-right:1px solid #1a5063;}
.block-container {max-width:1450px;padding-top:1.3rem;}
h1,h2,h3 {color:#d9faff!important;letter-spacing:.035em;}
[data-testid="stMetric"] {background:#0b2030;border:1px solid #1b566a;border-radius:15px;padding:12px 18px;}
[data-testid="stMetricLabel"] {color:#89b8c9;}
[data-testid="stMetricValue"] {color:#70f4f6;}
[data-testid="stChatMessage"] {border:1px solid #194356;background:#0b1c2c;border-radius:16px;margin-bottom:12px;}
.stButton>button[kind="primary"], [data-testid="stChatInput"] {border-color:#31b8cc;}
.stButton>button:hover {border-color:#79faff;color:#a6ffff;}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea {background:#081725;}
.jarvis-brand {font-size:.73rem;letter-spacing:.33em;color:#67d5e6;font-weight:700;}
.jarvis-hero {display:flex;align-items:center;gap:24px;flex-wrap:wrap;padding:20px 26px;border:1px solid #24576a;border-radius:22px;background:linear-gradient(110deg,rgba(10,42,61,.93),rgba(6,19,32,.96));box-shadow:0 0 38px rgba(32,195,229,.08);}
.jarvis-orb {width:145px;height:145px;position:relative;flex:none;display:grid;place-items:center;}
.jarvis-orb:before,.jarvis-orb:after {content:"";position:absolute;border-radius:50%;inset:5px;border:2px solid #4ddfee;border-left-color:transparent;box-shadow:0 0 18px #1a8fb1;animation:jarvis-spin 13s linear infinite;}
.jarvis-orb:after {inset:19px;border:1px dashed #b1f9ff;border-top-color:transparent;animation-direction:reverse;animation-duration:9s;}
.jarvis-core {height:76px;width:76px;border-radius:50%;display:grid;place-items:center;color:#d7ffff;font-weight:800;font-size:26px;letter-spacing:.06em;background:radial-gradient(circle,#2ba8c0 0%,#0a4e6a 48%,#071728 75%);box-shadow:0 0 26px #158ba9, inset 0 0 15px #70ecff;animation:jarvis-pulse 3s ease-in-out infinite;}
.jarvis-title {font-size:clamp(2rem,4vw,3.6rem);font-weight:800;line-height:1.08;letter-spacing:.14em;color:#e5fdff;text-shadow:0 0 20px #16718e;margin:7px 0;}
.jarvis-sub {color:#a3c7d4;font-size:.96rem;max-width:550px;}
.jarvis-tag {display:inline-block;border:1px solid #246a79;border-radius:50px;padding:4px 10px;color:#85f0e7;font-size:.73rem;letter-spacing:.08em;margin-top:12px;}
.jarvis-section {font-size:.76rem;letter-spacing:.24em;color:#78dce9;font-weight:800;margin:20px 0 10px;}
@keyframes jarvis-spin {to {transform:rotate(360deg)}}
@keyframes jarvis-pulse {50% {filter:brightness(1.45);transform:scale(1.045)}}
@media(prefers-reduced-motion:reduce) {.jarvis-orb:before,.jarvis-orb:after,.jarvis-core {animation:none}}
@media(max-width:650px) {.jarvis-hero{padding:14px}.jarvis-orb{width:105px;height:105px}.jarvis-title{font-size:2rem}}
</style>
"""

HERO = """
<div class="jarvis-hero">
  <div class="jarvis-orb" aria-label="Animated JARVIS core"><div class="jarvis-core">J</div></div>
  <div>
    <div class="jarvis-brand">PERSONAL INTELLIGENCE SYSTEM · COMMAND CENTRE</div>
    <div class="jarvis-title">J A R V I S</div>
    <div class="jarvis-sub">Your private AI workspace. Think, speak, remember, and build — from one control centre.</div>
    <div class="jarvis-tag">● LOCAL DASHBOARD</div>
  </div>
</div>
"""


def render_command_centre():
    st.markdown(CSS, unsafe_allow_html=True)
    st.markdown(HERO, unsafe_allow_html=True)

AVATAR = """
<div class="jarvis-stage" role="img" aria-label="Glowing holographic JARVIS face illustration">
<div class="jarvis-ring"></div>
<svg viewBox="0 0 300 380" class="jarvis-portrait" aria-hidden="true">
<defs><linearGradient id="jarvisSkin" x2="1" y2="1"><stop stop-color="#3de9ff" stop-opacity=".65"/><stop offset=".55" stop-color="#38348c" stop-opacity=".9"/><stop offset="1" stop-color="#a266ee" stop-opacity=".55"/></linearGradient></defs>
<path d="M55 300 Q30 315 17 365 L283 365 Q269 315 245 300 L210 280 L90 280Z" fill="url(#jarvisSkin)" stroke="#50dfff" stroke-width="2"/>
<path d="M115 258 L110 301 Q150 329 190 301 L185 258" fill="url(#jarvisSkin)" stroke="#8cdfff"/>
<path d="M75 113 Q75 33 150 31 Q225 33 225 113 L216 202 Q194 266 150 274 Q106 266 84 202Z" fill="url(#jarvisSkin)" stroke="#84eaff" stroke-width="2"/>
<path d="M70 136 Q47 65 100 29 Q150 -7 200 29 Q253 65 230 136 Q214 78 192 77 Q151 101 107 77 Q86 93 70 136Z" fill="#141d58" stroke="#78c7ff" stroke-width="3"/>
<path d="M95 153 Q115 140 137 153 M163 153 Q185 140 205 153" fill="none" stroke="#b9f5ff" stroke-width="4" stroke-linecap="round"/>
<circle cx="117" cy="154" r="5" fill="#7cffff"/><circle cx="184" cy="154" r="5" fill="#7cffff"/>
<path d="M150 160 L141 200 L157 200 M125 225 Q150 237 175 225" fill="none" stroke="#b9eaff" stroke-width="3"/>
<path d="M87 294 L150 351 L213 294 M56 327 L150 373 L244 327" fill="none" stroke="#75f5ff" stroke-width="2"/>
<circle cx="150" cy="333" r="12" fill="none" stroke="#a5ffff" stroke-width="3"/>
</svg>
<div class="jarvis-scan"></div><div class="jarvis-avatar-label">JARVIS / HOLOGRAPHIC VISUAL CORE</div>
</div>
"""
CSS += """
<style>
.jarvis-stage{height:435px;position:relative;overflow:hidden;border:1px solid #347f9d;border-radius:22px;background:radial-gradient(ellipse at 50% 40%,#17446b,#111735 53%,#070e1e);box-shadow:inset 0 0 70px #1687b130}
.jarvis-ring{position:absolute;left:50%;top:46%;transform:translate(-50%,-50%);width:300px;height:300px;border:1px solid #63eaff;border-radius:50%;box-shadow:0 0 35px #2ab7ff77,inset 0 0 30px #9457ee55;animation:jarvis-pulse 4s ease-in-out infinite}
.jarvis-portrait{position:absolute;left:50%;top:4%;transform:translateX(-50%);height:90%;width:90%;filter:drop-shadow(0 0 13px #42ceff)}
.jarvis-scan{position:absolute;left:5%;right:5%;top:8%;height:2px;background:#80efff88;box-shadow:0 0 12px #60eaff;animation:jarvis-sweep 6s linear infinite}
.jarvis-avatar-label{position:absolute;bottom:12px;left:18px;color:#9ceeff;font-size:.7rem;letter-spacing:.2em;font-weight:700}
.jarvis-panel{background:#0b2033;border:1px solid #285975;border-radius:14px;padding:16px;margin-bottom:14px}
.jarvis-panel h4{color:#78eaff;margin:0 0 12px;font-size:.8rem;letter-spacing:.2em}
.jarvis-panel p{color:#b4d9e8;margin:9px 0;font-size:.87rem}
.jarvis-panel code{color:#9be7c8;font-size:.83rem}
@keyframes jarvis-sweep{to{top:90%}}
@media(prefers-reduced-motion:reduce){.jarvis-ring,.jarvis-scan{animation:none}}
</style>
"""

def render_avatar():
    st.markdown(AVATAR, unsafe_allow_html=True)

def render_side_panels(provider, memory_count, message_count):
    import html
    provider = html.escape(str(provider).upper())
    st.markdown(f"""<div class="jarvis-panel"><h4>SYSTEM MONITOR</h4>
<p>AI ENGINE · {provider}</p><p>PRIVATE MEMORIES · {int(memory_count)}</p>
<p>SESSION MESSAGES · {int(message_count)}</p><p>STATUS · DASHBOARD ACTIVE</p></div>
<div class="jarvis-panel"><h4>TERMINAL / ACTIVITY</h4>
<code>&gt; JARVIS UI ready<br>&gt; Chat and memory available<br>&gt; Voice upload requires consent<br>&gt; Computer control not enabled</code></div>""", unsafe_allow_html=True)
