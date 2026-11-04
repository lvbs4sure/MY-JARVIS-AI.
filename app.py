"""JARVIS: a local holographic workspace with real, private controls."""
from pathlib import Path
import hashlib
import os
import re
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
from memory_store import add_memory, list_memories, search_memories, count_memories, update_memory, delete_memory
from jarvis_ai import generate_reply_result, transcribe_audio
from voice_output import speak_button
from ui_theme import render_command_centre, render_avatar, render_side_panels, window_title
from dashboard_panels import render_system_monitor
from activity_log import record_activity
from local_ai import inspect_local_ai, hardware_readiness
from local_runtime import start as start_isolated_ai, benchmark as benchmark_isolated_ai


def reset_voice_capture():
    st.session_state.voice_epoch = st.session_state.get("voice_epoch", 0) + 1


def render_memory_controls():
    st.header("Private memory")
    memory_search = st.text_input("Search memories", max_chars=200, key="memory_search", placeholder="Find a saved note")
    with st.form("remember", clear_on_submit=True):
        note = st.text_area("What should I remember?", max_chars=2000)
        if st.form_submit_button("Save memory"):
            try:
                add_memory(note)
                record_activity(st.session_state, "Memory saved")
                st.success("Memory saved.")
            except ValueError as exc:
                st.warning(str(exc))
    visible_memories = search_memories(memory_search, limit=100) if memory_search.strip() else list_memories()
    st.caption(f"{len(visible_memories)} saved notes shown. Saving is always your choice.")
    if memory_search.strip() and not visible_memories:
        st.info("No matching memories.")
    for memory_id, saved_note, created_at in visible_memories:
        with st.expander(f"#{memory_id}: {saved_note[:48]}"):
            with st.form(f"edit_{memory_id}"):
                edited = st.text_area("Edit memory", saved_note, max_chars=2000, key=f"note_{memory_id}")
                if st.form_submit_button("Save changes"):
                    try:
                        update_memory(memory_id, edited)
                        record_activity(st.session_state, "Memory updated")
                        st.rerun()
                    except ValueError as exc:
                        st.warning(str(exc))
            if st.checkbox("I want to delete this memory", key=f"confirm_delete_{memory_id}"):
                if st.button("Confirm delete memory", key=f"delete_{memory_id}"):
                    delete_memory(memory_id)
                    record_activity(st.session_state, "Memory deleted")
                    st.rerun()

st.set_page_config(page_title="JARVIS", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
render_command_centre()
st.session_state.setdefault("chat", [])
st.session_state.setdefault("voice_digest", None)
st.session_state.setdefault("assistant_state", "ready")
if "activity" not in st.session_state:
    record_activity(st.session_state, "Dashboard opened")
assistant_name=st.session_state.get("assistant_name", os.getenv("JARVIS_NAME", "JARVIS"))
personality=st.session_state.get("personality", "Helpful and concise")
reduced_motion=st.session_state.get("reduced_motion", False)
live_monitoring=st.session_state.get("live_monitoring", True)
provider=st.session_state.get("provider_override") or os.getenv("JARVIS_PROVIDER", "ollama").strip().lower()
with st.sidebar:
    st.markdown("### JARVIS / SESSION")
    st.metric("AI ENGINE", provider.upper())
    st.metric("PRIVATE MEMORIES", count_memories())
    st.metric("SESSION MESSAGES", len(st.session_state.chat))
    st.caption("Use the floating Shortcuts panel for memory, voice, system and settings.")
    st.caption("This installation is private and single-user. Gemini chat sends conversation and saved context to Google; telemetry stays local.")
left, centre, right=st.columns([1, 1.15, 1], gap="large")
with left:
    render_system_monitor(live_monitoring)
with centre:
    avatar_mount=st.empty()
    with avatar_mount.container():
        render_avatar(st.session_state.assistant_state,reduced_motion)
with right:
    with st.container(key="chat_window"):
        window_title("AI chat interface")
        conversation=st.container(height=230,border=False)
        with conversation:
            if not st.session_state.chat:
                st.info("Welcome to JARVIS. Ask a question below, or open Voice to speak.")
            for message in st.session_state.chat:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if message["role"]=="assistant" and message.get("ok", True):
                        speak_button(message["content"])
        if st.session_state.get("last_request"):
            st.caption(st.session_state.last_request)
        retry = False
        if st.session_state.chat and st.session_state.chat[-1].get("retryable"):
            st.caption("The last request failed. Retry sends the same conversation to the same provider.")
            retry = st.button("Retry last message", key="retry_reply")
        typed=st.chat_input(f"Ask {assistant_name} anything…",key="chat_prompt")
    render_side_panels(provider, count_memories(), len(st.session_state.chat), st.session_state.activity)
    with st.container(key="research_window"):
        window_title("Research workspace")
        st.caption("KAVI-inspired research panel · verified results only")
        st.info("Live web research is not connected yet. JARVIS will not invent search results or sources.")
    with st.container(key="file_window"):
        window_title("Selected file preview")
        selected_file = st.file_uploader("Choose a file to inspect", type=["txt", "md", "csv"], key="kavi_file_preview")
        if selected_file is not None:
            if selected_file.size > 1_000_000:
                st.warning("File exceeds the 1 MB preview limit. Nothing was saved.")
            else:
                preview_bytes = selected_file.getvalue()
                preview_text = preview_bytes.decode("utf-8", errors="replace")
                st.caption(f"{selected_file.name} · {selected_file.size} bytes · preview only, not sent to AI or saved")
                st.text_area("File contents (read-only preview)", value=preview_text[:4000], height=130, disabled=True)
    with st.container(key="code_window"):
        window_title("Code snippet")
        last_reply=next((item["content"] for item in reversed(st.session_state.chat) if item["role"]=="assistant"), "")
        code=re.search(r"```(?:[\w+-]+)?\n(.*?)```",last_reply,re.S)
        if code:
            st.code(code.group(1)[:4000],language="text",height=140)
            st.caption("From the latest reply. Display only; never executed.")
        else:
            st.code("from system_monitor import snapshot\n\n# Read-only local diagnostics\nstatus = snapshot()\nprint(status)",language="python")
            st.caption("Example only. Ask JARVIS for code to replace this snippet.")
    with st.container(key="shortcut_window"):
        window_title("Shortcuts")
        memory_tile,voice_tile,system_tile,settings_tile=st.columns(4,gap="small")
        with memory_tile:
            with st.popover("Memory",icon=":material/neurology:",width="stretch"):
                render_memory_controls()
        with voice_tile:
            with st.popover("Voice",icon=":material/mic:",width="stretch"):
                st.markdown("### Voice message")
                st.caption("Recording stays in this session until you explicitly allow the Gemini upload.")
                muted=st.toggle("Mute microphone", key="microphone_muted", on_change=reset_voice_capture)
                st.caption("Browser/Windows settings choose the microphone and output device. No wake-word or background listening is active.")
                if muted:
                    st.info("Microphone muted. New recording and transcription are blocked.")
                    audio=None
                else:
                    audio=st.audio_input("Record your message", key=f"voice_capture_{st.session_state.get('voice_epoch', 0)}")
                with st.expander("Test local spoken replies"):
                    st.caption("Uses an installed local browser voice. Nothing is sent to a speech service.")
                    speak_button("JARVIS voice controls are ready.")
                spoken=None
                if audio is not None:
                    raw=audio.getvalue()
                    digest=hashlib.sha256(raw).hexdigest()
                    consent=st.checkbox("Allow this recording to be uploaded to Gemini",key=f"audio_consent_{digest}")
                    already_sent=digest==st.session_state.voice_digest
                    if already_sent:
                        st.caption("Recording already sent. Record a new message to continue.")
                    if st.button("Send voice message to JARVIS",key="transcribe",disabled=not consent or already_sent):
                        with st.spinner("Processing voice message…"):
                            spoken,error=transcribe_audio(raw)
                        if error:
                            st.warning(error)
                            st.session_state.assistant_state="error"
                            with avatar_mount.container():
                                render_avatar("error",reduced_motion)
                            record_activity(st.session_state,"Voice transcription","failed")
                        elif spoken and spoken.strip():
                            spoken=spoken.strip()
                            st.session_state.voice_digest=digest
                            record_activity(st.session_state,"Voice transcribed")
                        else:
                            spoken=None
                            st.warning("No speech recognized. Please record again.")
        with system_tile:
            with st.popover("System",icon=":material/monitor_heart:",width="stretch"):
                st.markdown("### Live system readings")
                st.toggle("Live monitoring",value=True,key="live_monitoring")
                st.caption("CPU, RAM, storage, battery and adapter counters are read locally every two seconds. Network link is not an internet availability test. Temperature is N/A when Windows exposes no sensor.")
                st.caption("Current AI provider: "+provider+". This setting is not a connection-health guarantee.")
                st.caption("Gemini model: "+os.getenv("GEMINI_MODEL","gemini-flash-lite-latest"))
                st.divider()
                st.markdown("#### Local AI readiness")
                isolated_folder = Path(__file__).resolve().parent / ".local-ai"
                if (isolated_folder / "installation.json").exists():
                    if st.button("Start isolated local AI"):
                        try:
                            result = start_isolated_ai()
                            st.success("Isolated Ollama is running. The selected chat provider is unchanged.")
                            st.session_state.local_ai_status = inspect_local_ai()
                            st.session_state.local_hardware = hardware_readiness()
                            record_activity(st.session_state, "Isolated local AI", result["status"])
                        except (OSError, ValueError, RuntimeError) as exc:
                            st.warning(str(exc))
                    if (isolated_folder / "model-receipt.json").exists():
                        if st.button("Benchmark approved local model"):
                            try:
                                with st.spinner("Checking RAM and running a nonpersonal local test…"):
                                    result = benchmark_isolated_ai()
                                if result["status"] == "deferred":
                                    st.info(result["reason"])
                                elif result["status"] == "passed":
                                    st.success(f"Local baseline passed in {result['seconds']} seconds. Chat provider unchanged.")
                                else:
                                    st.warning("The local baseline did not return the expected answer. Chat provider unchanged.")
                                record_activity(st.session_state, "Local baseline", result["status"])
                            except (OSError, ValueError, RuntimeError):
                                st.warning("The local test could not complete. The working provider is unchanged.")
                if st.button("Check local AI", key="check_local_ai"):
                    st.session_state.local_ai_status = inspect_local_ai()
                    st.session_state.local_hardware = hardware_readiness()
                    record_activity(st.session_state, "Local AI checked")
                status = st.session_state.get("local_ai_status")
                if status:
                    st.info(status["message"])
                    hardware = st.session_state.get("local_hardware", {})
                    st.caption(f"RAM available: {hardware.get('ram_available_gib', 'N/A')} GiB · Storage free: {hardware.get('disk_free_gib', 'N/A')} GiB")
                    st.caption(hardware.get("advice", ""))
                    if status["models"]:
                        selected_model = st.selectbox("Installed local model", status["models"], key="local_model_choice")
                        if st.button("Use local AI for this session"):
                            fresh_hardware = hardware_readiness()
                            free_bytes = fresh_hardware.get("ram_available_bytes")
                            if not isinstance(free_bytes, int) or free_bytes < 2 * 2**30:
                                st.warning("Local chat needs at least 2 GiB free RAM for this setup. The working provider is unchanged.")
                            else:
                                st.session_state.provider_override = "ollama"
                                st.session_state.local_model_override = selected_model
                                record_activity(st.session_state, "Session provider changed", "local")
                                st.rerun()
                if st.session_state.get("provider_override"):
                    st.caption("Session override active. Your .env has not changed.")
                    if st.button("Return to configured provider"):
                        st.session_state.pop("provider_override", None)
                        st.session_state.pop("local_model_override", None)
                        record_activity(st.session_state, "Session provider restored")
                        st.rerun()
        with settings_tile:
            with st.popover("Settings",icon=":material/settings:",width="stretch"):
                st.markdown("### Personal settings")
                assistant_name=st.text_input("Assistant name",os.getenv("JARVIS_NAME","JARVIS"),key="assistant_name",max_chars=50).strip() or "JARVIS"
                personality=st.selectbox("Personality",["Helpful and concise","Friendly and encouraging","Professional and precise","Curious and creative"],key="personality")
                st.toggle("Reduce animation",key="reduced_motion")
                with st.expander("Clear conversation"):
                    st.warning("Only this session's chat is cleared. Saved memories remain.")
                    if st.button("Confirm clear conversation"):
                        st.session_state.chat=[]
                        record_activity(st.session_state,"Conversation cleared")
                        st.rerun()
prompt=typed or spoken
if prompt or retry:
    if retry:
        failed_message = st.session_state.chat.pop()
        request_provider = failed_message["request_provider"]
        request_model = failed_message.get("request_model")
    else:
        st.session_state.chat.append({"role":"user","content":prompt})
        request_provider = provider
        request_model = st.session_state.get("local_model_override")
        with conversation:
            with st.chat_message("user"):
                st.write(prompt)
    with avatar_mount.container():
        render_avatar("thinking",reduced_motion)
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat if m.get("ok", True)]
    with right:
        with st.spinner(f"{assistant_name} is thinking…"):
            outcome=generate_reply_result(history,list_memories(),assistant_name,personality,provider=request_provider,local_model=request_model)
    st.session_state.chat.append({"role":"assistant","content":outcome.text,"ok":outcome.ok,"retryable":outcome.retryable,
        "request_provider":request_provider,"request_model":request_model})
    st.session_state.last_request = f"{outcome.provider.upper()} · {outcome.latency_ms} ms · {outcome.kind}"
    st.session_state.assistant_state="ready" if outcome.ok else "error"
    record_activity(st.session_state,"AI reply","received" if outcome.ok else "failed")
    st.rerun()
