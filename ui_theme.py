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
