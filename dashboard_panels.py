"""Real OS telemetry rendered as floating reference-style windows."""
import html
import math
import streamlit as st
from system_monitor import SystemMonitor
from ui_theme import render_side_panels


def ring(label,value,color):
    try:
        number=float(value.rstrip('%'))
        number=number if math.isfinite(number) and 0<=number<=100 else None
    except (ValueError,AttributeError):
        number=None
    shown='N/A' if number is None else f'{number:.0f}%'
    aria='aria-valuetext="Unavailable"' if number is None else f'aria-valuenow="{number}"'
    return f'<div class="hud-gauge"><label>{label}</label><div class="hud-ring" role="meter" aria-label="{label}" aria-valuemin="0" aria-valuemax="100" {aria} style="--value:{number or 0};--tint:{color}"><b>{shown}</b></div></div>'


def sparkline(history,sensor,color):
    commands=[]
    drawing=False
    for i,row in enumerate(history):
        value=row.get(sensor)
        if value is None:
            drawing=False
            continue
        x=3+i*254/max(len(history)-1,1)
        y=43-float(value)*.4
        commands.append(('L' if drawing else 'M')+f'{x:.1f},{y:.1f}')
        drawing=True
    path=' '.join(commands)
    return f'<svg viewBox="0 0 260 46" role="img" aria-label="Recent measured {sensor} percentages"><path d="M0 44H260" stroke="#60678e44"/><path d="{path}" fill="none" stroke="{color}" stroke-width="1.5"/></svg>'


@st.fragment(run_every="2s")
def render_system_monitor(enabled=True):
    if enabled:
        if 'system_monitor' not in st.session_state:
            st.session_state.system_monitor=SystemMonitor()
        sample=st.session_state.system_monitor.sample()
        st.session_state.telemetry_latest=sample
        history=st.session_state.get('telemetry_history',[])
        st.session_state.telemetry_history=(history+[{'CPU':sample['cpu_percent'],'RAM':sample['ram_percent']}])[-30:]
    else:
        sample=st.session_state.get('telemetry_latest')
    if sample is None:
        st.caption('Monitoring paused. Enable it from System in Shortcuts.')
        return
    esc=lambda key: html.escape(str(sample[key]))
    gauges=''.join(ring(label,sample[key],color) for label,key,color in [('CPU','cpu','#61cee6'),('RAM','ram','#6ed1c7'),('DISK','disk','#9b86dd'),('BATTERY','battery','#648bdf')])
    mode='LIVE / 2s' if enabled else 'PAUSED'
    st.markdown(f'<div class="hud-panel"><div class="hud-title">SYSTEM OVERVIEW <small>{mode}</small></div><div class="hud-gauges">{gauges}</div><div class="hud-detail">↓ {esc("download")} &nbsp; ↑ {esc("upload")}<br>{esc("time")} · Africa/Lagos · {esc("power")}</div></div>',unsafe_allow_html=True)
    diagnostics=f'''<div class="hud-panel"><div class="hud-title">SYSTEM MONITOR <small>READ ONLY</small></div><div class="hud-terminal"><strong>JARVIS / local diagnostics</strong><br>OS      {esc("platform")}<br>RAM     {esc("ram_detail")}<br>DISK    {esc("disk_free")}<br>LINK    {esc("network")}<br>TEMP    {esc("temperature")}</div><hr class="hud-rule"><div class="hud-detail">CPU · recent samples</div>{sparkline(st.session_state.get('telemetry_history',[]),'CPU','#4fbae1')}<div class="hud-detail">RAM · recent samples</div>{sparkline(st.session_state.get('telemetry_history',[]),'RAM','#9c73e0')}<div class="hud-detail">Unsupported sensors show N/A. Link ≠ internet access.<br>Network rates: OS totals across all adapters.</div></div>'''
    st.markdown(diagnostics,unsafe_allow_html=True)
    render_side_panels('',0,0,st.session_state.get('activity',[]))
