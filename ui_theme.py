"""Reference-led holographic workspace. Decorative scene; genuine live controls."""
import html
import streamlit as st

CSS = '''<style>
:root{color-scheme:dark}
.stApp{background:#030814 url('/app/static/jarvis-scene.png') center center / cover fixed no-repeat;color:#d9e7ff}
[data-testid="stHeader"]{background:transparent;height:30px}
[data-testid="stToolbar"]{opacity:.25} [data-testid="stToolbar"]:hover{opacity:1}
.block-container{max-width:none;padding:5.5vh 4vw 2vh}
[data-testid="stSidebar"]{background:#060c1bea;border-right:1px solid #8c8de940}
h1,h2,h3,h4{color:#d9e7ff!important}
[data-testid="stVerticalBlock"]{gap:.55rem}
[data-testid="stHorizontalBlock"]{gap:1.5rem}
[data-testid="stTextInput"] input,[data-testid="stTextArea"] textarea{background:#081021dd;font-size:.8rem}
[data-testid="stPopoverBody"]{background:#070d1df5;border:1px solid #7e8dbb80}
[data-testid="stChatInput"]{background:#10162be6;border:1px solid #747bd366;border-radius:5px}
[data-testid="stChatInput"] textarea{font-size:.8rem}
[data-testid="stChatInputSubmitButton"]{background:linear-gradient(130deg,#4c2bba,#7b3eda);border-radius:4px;color:white}
[data-testid="stChatMessage"]{background:transparent;padding:8px 6px;border:0;gap:7px}
[data-testid="stChatMessage"] p{font-size:.8rem;line-height:1.6}
[data-testid="stChatMessageAvatarAssistant"],[data-testid="stChatMessageAvatarUser"]{width:20px;height:20px;min-width:20px}
[data-testid="stCode"]{background:transparent!important;border:0;font-size:.7rem}
[data-testid="stCode"] pre{background:transparent!important;padding:8px;font-size:.7rem}
.st-key-chat_window,.st-key-code_window,.st-key-shortcut_window,.st-key-research_window,.st-key-file_window{background:linear-gradient(135deg,#060c19e8,#101023da);border:1px solid #9d9cc275;border-radius:10px;padding:12px;box-shadow:0 10px 35px #0009,inset 0 0 20px #1e31511c;backdrop-filter:blur(12px);margin-bottom:10px}
.st-key-research_window{border-top:2px solid #8e79e8}.st-key-file_window{border-top:2px solid #64c9dc}
.st-key-file_window [data-testid="stFileUploader"]{border:1px dashed #6889bb66;border-radius:7px;padding:6px}
.st-key-file_window [data-testid="stTextArea"] textarea{font:11px/1.7 Consolas,monospace;color:#c6d5ee}
.hud-log em.failed{color:#ffbf91}.hud-log em.interrupted{color:#c6b4ff}
.window-title{font:600 10px system-ui;letter-spacing:.07em;color:#d5d9ef;display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;text-transform:uppercase}
.window-title span{font-size:10px;color:#6984ad;letter-spacing:5px}
.hud-panel{background:linear-gradient(130deg,#050c18eb,#0d1121de);border:1px solid #9b9ec078;border-radius:10px;padding:13px 12px;margin:0 0 14px;box-shadow:0 10px 30px #0008,inset 0 0 18px #5975ba0a;backdrop-filter:blur(12px)}
.hud-title{font:600 10px system-ui;letter-spacing:.045em;color:#d5d9ef;display:flex;justify-content:space-between;gap:8px;margin-bottom:13px;text-transform:uppercase}
.hud-title small{color:#7c8aaf;font-size:9px;font-weight:400}
.hud-gauges{display:flex;justify-content:space-between;gap:5px}.hud-gauge{text-align:center;min-width:0;flex:1}
.hud-gauge label{display:block;font:9px system-ui;color:#a7aac2;margin-bottom:6px}
.hud-ring{--value:0;--tint:#62cfe6;width:53px;height:53px;margin:auto;border-radius:50%;display:grid;place-items:center;background:conic-gradient(var(--tint) calc(var(--value)*1%),#28314655 0);position:relative;box-shadow:0 0 12px #4072a41c}
.hud-ring:before{content:'';position:absolute;inset:3px;border-radius:50%;background:#080e1b}
.hud-ring b{font:12px system-ui;color:#e5ecff;z-index:1;font-variant-numeric:tabular-nums}
.hud-detail{font:9px system-ui;color:#8c9bb7;margin-top:9px;line-height:1.6}
.hud-terminal{font:11px/1.9 ui-monospace,Consolas,monospace;color:#a29bcb;white-space:pre-wrap;overflow-wrap:anywhere;margin:0}
.hud-terminal strong{color:#7edeea;font-weight:500}.hud-rule{border:0;border-top:1px solid #66729b30;margin:10px 0}
.hud-log{font:10px/1.9 Consolas,monospace;color:#91a0ba;margin:0}.hud-log time{color:#6f9ec0}.hud-log em{color:#79cdbb;font-style:normal}
.holo-stage{height:620px;position:relative;pointer-events:none;isolation:isolate}
.holo-state{position:absolute;bottom:5%;left:0;right:0;text-align:center;font:9px Consolas,monospace;letter-spacing:.18em;color:#b8e8ff;text-shadow:0 0 10px #50cfff}
.holo-scan{position:absolute;top:6%;left:12%;right:12%;height:1px;background:linear-gradient(90deg,transparent,#9aebff8c,transparent);box-shadow:0 0 10px #75dcff80;animation:holo-scan 12s linear infinite;opacity:.3}
.holo-glow{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 40%,#54aaff0a,transparent 65%);animation:holo-breathe 5s ease-in-out infinite}
.state-thinking .holo-glow{background:radial-gradient(ellipse at 50% 40%,#a467ff35,transparent 65%);animation-duration:1.4s}
.state-error .holo-state{color:#ffd2a4}.motion-off *{animation:none!important}
.shortcut-caption{font:9px system-ui;color:#8fa2c4;margin:0 0 4px}
.st-key-shortcut_window [data-testid="stHorizontalBlock"]{gap:5px}
.st-key-shortcut_window button{font-size:10px!important;min-height:42px;padding:4px!important;background:#0b1227aa;border:1px solid #5d65a84d;border-radius:6px}
.st-key-shortcut_window button:hover{border-color:#a58aeb;color:#dcceff}
.st-key-shortcut_window button [data-has-shortcut]{display:flex;flex-direction:column;align-items:center;gap:4px}
.st-key-shortcut_window button>div{justify-content:center}
.st-key-shortcut_window button>div>div[aria-hidden="true"]{display:none}
.st-key-shortcut_window .stMarkdownEllipsis{overflow:visible;white-space:nowrap}
.st-key-shortcut_window .stMarkdownEllipsis p{font-size:9px}
@keyframes holo-scan{to{top:78%}}@keyframes holo-breathe{50%{opacity:.3}}
@media(prefers-reduced-motion:reduce){.holo-stage *{animation:none!important}}
@media(max-width:900px){.block-container{padding:45px 3vw 20px}.hud-ring{width:44px;height:44px}.hud-ring b{font-size:10px}.hud-title{font-size:9px}}
@media(max-width:640px){.stApp{background-position:center top;background-size:auto 100vh}.block-container{padding:45px 16px 20px}.holo-stage{height:320px}.hud-panel{background:#060c1bef}.st-key-chat_window,.st-key-code_window,.st-key-shortcut_window,.st-key-research_window,.st-key-file_window{background:#080d1cf2}.hud-ring{width:55px;height:55px}.hud-title{font-size:10px}}
</style>'''


def render_command_centre(reduced_motion=False):
    st.markdown(CSS, unsafe_allow_html=True)


def render_avatar(state="ready", reduced_motion=False):
    states={"ready":"JARVIS / READY", "thinking":"JARVIS / PROCESSING YOUR REQUEST", "transcribing":"JARVIS / TRANSCRIBING RECORDING", "error":"JARVIS / REQUEST NEEDS ATTENTION"}
    state=state if state in states else "ready"
    classes=f"holo-stage state-{state}"+(" motion-off" if reduced_motion else "")
    st.markdown(f'<div class="{classes}" role="img" aria-label="Photorealistic holographic JARVIS character"><div class="holo-glow"></div><div class="holo-scan"></div><div class="holo-state">{states[state]}</div></div>',unsafe_allow_html=True)


def render_side_panels(provider,memory_count,message_count,activity=()):
    entries=''.join(f'<p class="hud-log"><time>{html.escape(e["time"])}</time> {html.escape(e["action"])} · <em class="{html.escape(e["outcome"],quote=True)}">{html.escape(e["outcome"])}</em></p>' for e in list(activity)[-5:])
    entries=entries or '<p class="hud-log">No actions in this session yet.</p>'
    st.markdown(f'<div class="hud-panel"><div class="hud-title">REAL-TIME LOGS <small>SESSION ONLY</small></div>{entries}</div>',unsafe_allow_html=True)


def window_title(title):
    st.markdown(f'<div class="window-title">{html.escape(title)}<span>− ◇ ×</span></div>',unsafe_allow_html=True)
