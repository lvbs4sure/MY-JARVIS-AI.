"""JARVIS: a local holographic workspace with real, private controls."""
from pathlib import Path
import hashlib
import os
import re
import sqlite3
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
from memory_store import add_memory, list_memories, search_memories, count_memories, update_memory, delete_memory
from jarvis_ai import generate_reply_result, transcribe_audio
from voice_output import speak_button
from animated_avatar import render_moving_face
from file_preview import preview_upload
from camera_preview import render_camera_preview
import chat_history
from request_jobs import RequestJob
from conversation_flow import finish_request
from ui_theme import render_command_centre, render_avatar, window_title, render_session_strip
from dashboard_panels import render_system_monitor
from dashboard_readiness import dashboard_readiness
from activity_log import record_activity
from local_ai import inspect_local_ai, hardware_readiness
from local_runtime import start as start_isolated_ai, benchmark as benchmark_isolated_ai


def reset_voice_capture():
    if st.session_state.get("microphone_muted"):
        st.session_state.pop("pending_spoken",None)
        st.session_state.pop("spoken_route",None)
        job = st.session_state.get("request_job")
        if job is not None and job.kind == "voice":
            job.cancel()
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

def render_history_controls(busy):
    st.toggle("Save chat history on this device",key="save_chat_history")
    st.caption("Off by default. Saves chat text locally in this new installation only; never audio, camera images or files. Configured API keys are masked. Saved chats are not sent to AI until you send another message.")
    try:
        chat_history.sync_history(st.session_state)
        saved_chats=chat_history.list_conversations()
        if st.button("New conversation",key="new_conversation",disabled=busy):
            st.session_state.chat=[]
            for history_key in ("history_id","history_snapshot","last_request","voice_error"):
                st.session_state.pop(history_key,None)
            st.session_state.assistant_state="ready"
            record_activity(st.session_state,"New conversation")
            st.rerun()
        if saved_chats:
            titles={row[0]:f"{row[1]} · {row[2][:10]}" for row in saved_chats}
            selected_chat=st.selectbox("Saved conversations",list(titles),format_func=titles.get,key="selected_history")
            if st.button("Open saved conversation",key="open_history",disabled=busy):
                restored=chat_history.load_conversation(selected_chat)
                if restored is None:
                    st.warning("That saved conversation is no longer available.")
                else:
                    st.session_state.chat=restored
                    st.session_state.history_id=selected_chat
                    st.session_state.history_snapshot=None
                    st.session_state.assistant_state="ready"
                    st.session_state.pop("last_request",None)
                    record_activity(st.session_state,"Saved conversation opened")
                    st.rerun()
        else:
            st.caption("No saved conversations. Enable local saving to keep new chats after restarting.")
    except (ValueError,OSError,sqlite3.Error):
        st.warning("Chat history could not be saved or opened. This session and existing saved history remain available. History is limited to 1,000 messages and 2 MB per conversation.")


@st.fragment(run_every="500ms")
def request_controls():
    job = st.session_state.get("request_job")
    if job is None:
        return
    if finish_request(st.session_state):
        st.rerun()
    if job.cancel_event.is_set():
        st.caption("Interrupted. Discarding the result and waiting for the current connection to finish.")
    else:
        st.caption("Transcribing with Gemini…" if job.kind == "voice" else f"Waiting for {job.metadata['provider'].upper()}…")
    if st.button("Interrupt request", key="interrupt_request", disabled=job.cancel_event.is_set(), icon=":material/stop_circle:"):
        job.cancel()
        st.session_state.assistant_state = "ready"
        st.rerun()
    st.caption("Interrupt stops retries and discards late results. It cannot recall data already sent. New requests wait until this one finishes.")


st.set_page_config(page_title="JARVIS", page_icon="◈", layout="wide", initial_sidebar_state="collapsed")
avatar_style=st.session_state.get("avatar_style", "Holographic scene")
render_command_centre()
st.session_state.setdefault("chat", [])
st.session_state.setdefault("voice_digest", None)
st.session_state.setdefault("assistant_state", "ready")
finish_request(st.session_state)
spoken=st.session_state.pop("pending_spoken", None)
if st.session_state.get("microphone_muted"):
    spoken=None
    st.session_state.pop("spoken_route",None)
busy=st.session_state.get("request_job") is not None
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
    st.caption("The tool dock opens memory, voice, history, files, research, camera, system and settings.")
    st.caption("This installation is private and single-user. Gemini chat sends conversation and saved context to Google; telemetry stays local.")

left, centre, right=st.columns([0.8, 1.7, 1], gap="large")
with left:
    render_system_monitor(live_monitoring)
with centre:
    avatar_mount=st.empty()
    with avatar_mount.container():
        render_avatar(st.session_state.assistant_state,reduced_motion)
        if avatar_style=="Animated wireframe face":
            latest_reply=next((m["content"] for m in reversed(st.session_state.chat) if m["role"]=="assistant" and m.get("ok",True)), "")
            last_is_reply=bool(st.session_state.chat and st.session_state.chat[-1].get("role")=="assistant" and st.session_state.chat[-1].get("ok",True))
            render_moving_face(latest_reply,st.session_state.assistant_state,reduced_motion,auto_play=bool(st.session_state.get("auto_speak_replies",False) and last_is_reply))
with right:
    with st.container(key="chat_window"):
        window_title("AI chat interface")
        render_session_strip(provider,st.session_state.get("microphone_muted",False),st.session_state.get("save_chat_history",False),busy)
        conversation=st.container(height=230,border=False)
        with conversation:
            if not st.session_state.chat:
                st.info("Welcome to JARVIS. Ask a question below, or open Voice to speak.")
            for message in st.session_state.chat:
                with st.chat_message(message["role"]):
                    st.write(message["content"])
                    if message.get("cancelled"):
                        st.caption("Interrupted; omitted from future AI context.")
                    if message["role"]=="assistant" and message.get("ok", True) and avatar_style!="Animated wireframe face":
                        if st.session_state.get("auto_speak_replies", False) and message is st.session_state.chat[-1]:
                            speak_button(message["content"], auto_play=True)
                        else:
                            speak_button(message["content"])
        if st.session_state.get("last_request"):
            st.caption(st.session_state.last_request)
        if busy:
            request_controls()
        retry = False
        if st.session_state.chat and st.session_state.chat[-1].get("retryable"):
            st.caption("The last request failed. Retry sends the same conversation to the same provider.")
            retry = st.button("Retry last message", key="retry_reply", disabled=busy)
        typed=st.chat_input(f"Ask {assistant_name} anything…",key="chat_prompt", disabled=busy)
    with st.container(key="code_window"):
        with st.expander("Code snippet",icon=":material/code:"):
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
                st.toggle("Speak new replies automatically", key="auto_speak_replies", help="Uses an installed local browser voice. Your browser may require a click before playback.")
                st.caption("Recording stays in this session until you explicitly allow the Gemini upload.")
                muted=st.toggle("Mute microphone", key="microphone_muted", on_change=reset_voice_capture)
                st.caption("Browser/Windows settings choose the microphone and output device. No wake-word or background listening is active.")
                if muted:
                    st.info("Microphone muted. New recording and transcription are blocked.")
                    audio=None
                else:
                    audio=st.audio_input("Record your message", key=f"voice_capture_{st.session_state.get('voice_epoch', 0)}", disabled=busy)
                with st.expander("Test local spoken replies"):
                    st.caption("Uses an installed local browser voice. Nothing is sent to a speech service.")
                    if avatar_style=="Animated wireframe face":
                        st.caption("Use the speech controls beside the animated face.")
                    else:
                        speak_button("JARVIS voice controls are ready.")
                if st.session_state.get("voice_error"):
                    st.warning(st.session_state.voice_error)
                if audio is not None:
                    raw=audio.getvalue()
                    digest=hashlib.sha256(raw).hexdigest()
                    consent=st.checkbox("Allow this recording to be uploaded to Gemini",key=f"audio_consent_{digest}")
                    already_sent=digest==st.session_state.voice_digest
                    if already_sent:
                        st.caption("Recording already sent. Record a new message to continue.")
                    if st.button("Send voice message to JARVIS",key="transcribe",disabled=not consent or already_sent or busy):
                        try:
                            st.session_state.request_job=RequestJob("voice", lambda token: transcribe_audio(raw, cancel_event=token),
                                {"provider":provider,"local_model":st.session_state.get("local_model_override")})
                            st.session_state.voice_digest=digest
                            st.session_state.pop("voice_error",None)
                            st.session_state.assistant_state="transcribing"
                            st.session_state.request_job.finished.wait(0.02)
                            st.rerun()
                        except RuntimeError as exc:
                            st.warning(str(exc))
        with system_tile:
            with st.popover("System",icon=":material/monitor_heart:",width="stretch"):
                st.markdown("### Dashboard readiness")
                try:
                    import psutil
                    free_ram = psutil.virtual_memory().available
                except (ImportError, OSError, AttributeError):
                    free_ram = None
                for feature, (status, detail) in dashboard_readiness(
                    provider, free_ram_bytes=free_ram
                ).items():
                    st.caption(f"{feature.upper()} · {status.upper()} — {detail}")
                st.divider()
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
                st.selectbox("Hologram display",["Holographic scene","Animated wireframe face"],key="avatar_style",help="Animated preview adds approximate speech-linked mouth motion. Original holographic scene remains available.")
                assistant_name=st.text_input("Assistant name",os.getenv("JARVIS_NAME","JARVIS"),key="assistant_name",max_chars=50).strip() or "JARVIS"
                personality=st.selectbox("Personality",["Helpful and concise","Friendly and encouraging","Professional and precise","Curious and creative"],key="personality")
                st.caption("Your original holographic JARVIS appearance is preserved.")
                st.toggle("Reduce animation",key="reduced_motion")
                with st.expander("Clear conversation"):
                    st.warning("Only this session's chat is cleared. Saved memories remain.")
                    if st.button("Confirm clear conversation"):
                        st.session_state.chat=[]
                        st.session_state.pop("history_id",None)
                        st.session_state.pop("history_snapshot",None)
                        record_activity(st.session_state,"Conversation cleared")
                        st.rerun()
        history_tile,files_tile,research_tile,camera_tile=st.columns(4,gap="small")
        with history_tile:
            with st.popover("History",icon=":material/history:",width="stretch"):
                st.markdown("### Chat history")
                render_history_controls(busy)
        with files_tile:
            with st.popover("Files",icon=":material/folder_open:",width="stretch"):
                with st.container(key="file_window"):
                    window_title("Selected file preview")
                    selected_file = st.file_uploader("Choose a file to inspect", type=["txt", "md", "csv"], key="kavi_file_preview", max_upload_size=1)
                    if selected_file is not None:
                        try:
                            filename, preview_text, byte_count, truncated = preview_upload(selected_file)
                            st.text(f"{filename} · {byte_count:,} bytes")
                            st.caption("Local preview only. Never executed, saved to disk, or sent to AI.")
                            st.text_area("File contents (read-only preview)", value=preview_text, height=160, disabled=True)
                            if truncated:
                                st.caption("Showing the first 4,000 characters.")
                        except ValueError as exc:
                            st.warning(str(exc))
        with research_tile:
            with st.popover("Research",icon=":material/travel_explore:",width="stretch"):
                with st.container(key="research_window"):
                    window_title("Research workspace")
                    st.caption("RESEARCH / DISCONNECTED")
                    st.markdown("Research results will appear here with sources and timestamps when a research provider is connected.")
                    st.info("Live web research is not connected yet. JARVIS will not invent search results or sources.")
        with camera_tile:
            with st.popover("Camera",icon=":material/videocam:",width="stretch"):
                st.markdown("### Local camera")
                st.toggle("Show local camera controls",key="show_local_camera")
                st.caption("Off until you choose Start. Local preview only; JARVIS image understanding is not connected.")
if st.session_state.get("show_local_camera"):
    with right:
        with st.container(key="camera_window"):
            window_title("Local camera / preview only")
            render_camera_preview()
prompt=typed or spoken
if (prompt or retry) and not busy:
    if retry:
        failed_message = st.session_state.chat.pop()
        request_provider = failed_message["request_provider"]
        request_model = failed_message.get("request_model")
    else:
        st.session_state.chat.append({"role":"user","content":prompt})
        route=st.session_state.pop("spoken_route",{}) if spoken else {}
        request_provider = route.get("provider",provider)
        request_model = route.get("local_model",st.session_state.get("local_model_override"))
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.chat if m.get("ok", True) and not m.get("cancelled")]
    memories=list_memories()
    try:
        st.session_state.request_job=RequestJob("chat",
            lambda token: generate_reply_result(history,memories,assistant_name,personality,provider=request_provider,local_model=request_model,cancel_event=token),
            {"provider":request_provider,"local_model":request_model,"user_index":len(st.session_state.chat)-1})
        st.session_state.assistant_state="thinking"
        st.session_state.request_job.finished.wait(0.02)
        st.rerun()
    except RuntimeError as exc:
        if retry:
            st.session_state.chat.append(failed_message)
        else:
            st.session_state.chat[-1]["cancelled"]=True
        st.session_state.assistant_state="error"
        record_activity(st.session_state,"Request not started","failed")
        st.warning(str(exc))
