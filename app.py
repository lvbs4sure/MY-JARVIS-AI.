"""JARVIS: independent personal AI starter."""
from pathlib import Path
import hashlib
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
from memory_store import add_memory, list_memories, search_memories, update_memory, delete_memory
from jarvis_ai import generate_reply, transcribe_audio
from voice_output import speak_button
from ui_theme import render_command_centre, render_avatar, render_side_panels

st.set_page_config(page_title="JARVIS", page_icon="🤖", layout="wide")
render_command_centre()
if "chat" not in st.session_state:
    st.session_state.chat = []
if "voice_digest" not in st.session_state:
    st.session_state.voice_digest = None

with st.sidebar:
    st.markdown("### ◈ JARVIS CONTROL")
    st.caption("PERSONAL COMMAND CENTRE")
    st.header("Personalize")
    assistant_name = st.text_input("Assistant name", os.getenv("JARVIS_NAME", "JARVIS"), max_chars=50).strip() or "JARVIS"
    personality = st.selectbox("Personality", ["Helpful and concise", "Friendly and encouraging", "Professional and precise", "Curious and creative"])
    st.header("Private memory")
    memory_search = st.text_input("Search memories", max_chars=200, key="memory_search", placeholder="Find a saved note")
    with st.form("remember", clear_on_submit=True):
        note = st.text_area("What should I remember?", max_chars=2000)
        if st.form_submit_button("Save memory"):
            try:
                add_memory(note)
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
                        st.rerun()
                    except ValueError as exc:
                        st.warning(str(exc))
            if st.checkbox("I want to delete this memory", key=f"confirm_delete_{memory_id}"):
                if st.button("Confirm delete memory", key=f"delete_{memory_id}"):
                    delete_memory(memory_id)
                    st.rerun()
    with st.expander("Clear conversation"):
        st.warning("This clears chat history for this browser session only.")
        if st.button("Confirm clear conversation"):
            st.session_state.chat = []
            st.rerun()
    st.caption("Single-user local installation. Each friend should use a separate copy and database.")
    st.divider()
    st.header("AI connection")
    provider = os.getenv("JARVIS_PROVIDER", "ollama").strip().lower()
    st.write(f"Configured provider: **{provider}**")
    if provider == "ollama":
        st.caption(f"Local model: {os.getenv('OLLAMA_MODEL', 'llama3.2:3b')}. Chat stays local when Ollama runs on localhost.")
    elif provider == "gemini":
        st.caption("Cloud provider: conversation and saved memory context are sent to Gemini.")
        st.caption(f"Model: {os.getenv('GEMINI_MODEL', 'gemini-flash-lite-latest')}")
    else:
        st.error("Set JARVIS_PROVIDER to ollama or gemini in your private .env file.")

st.markdown('<div class="jarvis-section">HOLOGRAPHIC COMMAND CENTRE</div>', unsafe_allow_html=True)
left, centre, right = st.columns([1, 1.6, 1], gap="medium")
with left:
    st.markdown('<div class="jarvis-panel"><h4>QUICK ACCESS</h4><p>◈ AI CONVERSATION</p><p>◈ PRIVATE MEMORY</p><p>◈ VOICE INTERFACE</p><p>◈ PERSONAL SETTINGS</p></div>', unsafe_allow_html=True)
    st.caption("Manage memory and settings in the left sidebar.")
with centre:
    render_avatar()
with right:
    render_side_panels(provider, len(list_memories()), len(st.session_state.chat))
st.markdown('<div class="jarvis-section">AI CHAT INTERFACE</div>', unsafe_allow_html=True)
for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            speak_button(message["content"])

st.markdown('<div class="jarvis-section">VOICE INTERFACE</div>', unsafe_allow_html=True)
typed = st.chat_input(f"Ask {assistant_name}")
audio = st.audio_input("Record your message")
spoken = None
if audio is not None:
    raw = audio.getvalue()
    digest = hashlib.sha256(raw).hexdigest()
    consent = st.checkbox("Allow this recording to be uploaded to Gemini", key=f"audio_consent_{digest}")
    already_sent = digest == st.session_state.voice_digest
    if already_sent:
        st.caption("Recording already sent. Record a new message to continue.")
    if st.button("Send voice message to JARVIS", key="transcribe", disabled=not consent or already_sent):
        with st.spinner("Processing voice message..."):
            spoken, error = transcribe_audio(raw)
        if error:
            st.warning(error)
        elif spoken and spoken.strip():
            spoken = spoken.strip()
            st.session_state.voice_digest = digest
            st.caption(f"Heard: {spoken}")
        else:
            spoken = None
            st.warning("No speech recognized. Please record again.")
prompt = typed or spoken
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.spinner(f"{assistant_name} is thinking…"):
        reply = generate_reply(st.session_state.chat, list_memories(), assistant_name, personality)
    st.session_state.chat.append({"role": "assistant", "content": reply})
    # Render the completed exchange and refresh the overview counters together.
    st.rerun()
