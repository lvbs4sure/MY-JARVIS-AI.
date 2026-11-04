# JARVIS architecture and roadmap

## The ownership model
The original creator controls this starter repository. Friends can **fork or copy** it into their own repositories and run their own independent installations. Each installation uses its own local SQLite database and its own private Gemini API key. No shared hosted user accounts are assumed or implemented.

## Current modules
- `app.py`: Streamlit chat, personalization controls, memory editor, and microphone input
- `memory_store.py`: local SQLite memory create/read/update/delete
- `jarvis_ai.py`: Gemini response generation and optional audio transcription
- `.env.example`: example local configuration; actual `.env` is excluded from Git
- `tests/`: basic automated memory checks

## Privacy and boundaries
- This is a **single-user per installation** prototype. Do not expose one installation publicly for several people to use; Streamlit session isolation is not an authentication or database authorization system.
- For friends: fork/copy the code, create a separate environment, database, and API key. Never share the owner's `.env` or `jarvis_memory.db`.
- Audio submitted using the microphone is sent to Gemini for transcription. Text chat and saved notes used for context are also sent to Gemini.
- The repository is public; do not commit secrets or personal data.

## Roadmap
1. **Foundation (implemented, needs runtime validation):** text chat, local memories, edit/delete, Gemini adapter, personalization, microphone transcription.
2. **Next:** opt-in text-to-speech playback, structured subject-based memory, stronger testing and diagnostics.
3. **Distribution:** installable template and friend onboarding, individual configuration and branding.
4. **Optional hosted platform:** proper sign-in, per-user data authorization, encrypted secret management, migrations, and deployment before allowing multiple users on one server.
5. **Advanced abilities:** explicit user-approved integrations and actions with permissions and audit logs.

Voice output, hosted accounts, and autonomous computer control are **not implemented**. Decisions from earlier architecture discussions should be added here when verified, rather than guessed.
