"""JARVIS: independent personal AI starter."""
from pathlib import Path
import hashlib
import os
import streamlit as st
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")
from memory_store import add_memory, list_memories, update_memory, delete_memory
from jarvis_ai import generate_reply, transcribe_audio
from voice_output import speak_button

st.set_page_config(page_title="JARVIS", page_icon="🤖", layout="wide")
st.title("🤖 JARVIS — Your Personal AI")
st.caption("Your assistant, your memory, your starting point.")
if "chat" not in st.session_state:
    st.session_state.chat = []
if "voice_digest" not in st.session_state:
    st.session_state.voice_digest = None

with st.sidebar:
    st.header("Personalize")
    assistant_name = st.text_input("Assistant name", os.getenv("JARVIS_NAME", "JARVIS"), max_chars=50).strip() or "JARVIS"
    personality = st.selectbox("Personality", ["Helpful and concise", "Friendly and encouraging", "Professional and precise", "Curious and creative"])
    st.header("Private memory")
    with st.form("remember", clear_on_submit=True):
        note = st.text_area("What should I remember?", max_chars=2000)
        if st.form_submit_button("Save memory"):
            try:
                add_memory(note)
                st.success("Memory saved.")
            except ValueError as exc:
                st.warning(str(exc))
    for memory_id, saved_note, created_at in list_memories():
        with st.expander(f"#{memory_id}: {saved_note[:48]}"):
            with st.form(f"edit_{memory_id}"):
                edited = st.text_area("Edit memory", saved_note, max_chars=2000, key=f"note_{memory_id}")
                if st.form_submit_button("Save changes"):
                    try:
                        update_memory(memory_id, edited)
                        st.rerun()
                    except ValueError as exc:
                        st.warning(str(exc))
            if st.button("Delete memory", key=f"delete_{memory_id}"):
                delete_memory(memory_id)
                st.rerun()
    if st.button("Clear chat"):
        st.session_state.chat = []
        st.rerun()
    st.caption("Single-user local installation. Each friend should use a separate copy and database.")

for message in st.session_state.chat:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if message["role"] == "assistant":
            speak_button(message["content"])

typed = st.chat_input(f"Ask {assistant_name}")
audio = st.audio_input("Record voice (Gemini transcription is optional)")
spoken = None
if audio is not None:
    raw = audio.getvalue()
    digest = hashlib.sha256(raw).hexdigest()
    if st.button("Transcribe recording with Gemini (uploads audio)", key="transcribe"):
        if digest == st.session_state.voice_digest:
            st.info("This recording was already transcribed. Record another to retry.")
        else:
            with st.spinner("Transcribing…"):
                spoken, error = transcribe_audio(raw)
            if error:
                st.warning(error)
            elif spoken:
                st.session_state.voice_digest = digest
                st.info(f"You said: {spoken}")
prompt = typed or spoken
if prompt:
    st.session_state.chat.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)
    with st.spinner(f"{assistant_name} is thinking…"):
        reply = generate_reply(st.session_state.chat, list_memories(), assistant_name, personality)
    st.session_state.chat.append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)
        speak_button(reply)
