# JARVIS architecture and roadmap

## The ownership model
The original creator controls this starter repository. Friends can **fork or copy** it into their own repositories and run their own independent installations. Each installation uses its own local SQLite database. Ollama runs locally by default; Gemini is optional and requires that person's private API key. No shared hosted user accounts are assumed or implemented.

## Current modules
- `app.py`: Streamlit chat, personalization controls, memory editor, and microphone input
- `memory_store.py`: local SQLite memory create/read/update/delete
- `jarvis_ai.py`: local Ollama chat, optional Gemini chat, and opt-in Gemini audio transcription
- `.env.example`: example local configuration; actual `.env` is excluded from Git
- `tests/`: basic automated memory checks

## Privacy and boundaries
- This is a **single-user per installation** prototype. Do not expose one installation publicly for several people to use; Streamlit session isolation is not an authentication or database authorization system.
- For friends: fork/copy the code, create a separate environment, database, and API key. Never share the owner's `.env` or `jarvis_memory.db`.
- Audio is sent to Gemini only after explicit transcription consent and opt-in configuration. Text chat and saved notes remain on the device with local Ollama; Gemini chat sends those to Gemini when explicitly configured.
- The repository is public; do not commit secrets or personal data.

## Roadmap
1. **Foundation (implemented, needs runtime validation):** text chat, local memories, edit/delete, Gemini adapter, personalization, microphone transcription.
2. **Next:** structured subject-based memory, stronger integration testing, diagnostics, and accessibility improvements.
3. **Distribution:** installable template and friend onboarding, individual configuration and branding.
4. **Optional hosted platform:** proper sign-in, per-user data authorization, encrypted secret management, migrations, and deployment before allowing multiple users on one server.
5. **Advanced abilities:** explicit user-approved integrations and actions with permissions and audit logs.

Voice output is implemented via browser speech synthesis but not yet browser-validated. Hosted accounts and autonomous computer control are **not implemented**. Decisions from earlier architecture discussions should be added here when verified, rather than guessed.

## Voice privacy decision (2026-11-04)
Recording in the browser does **not** trigger a network transcription request by itself. The user must press **Transcribe recording with Gemini (uploads audio)**. Transcription also requires `JARVIS_VOICE_PROVIDER=gemini` and a private Gemini key. Spoken replies use the browser speech synthesis feature and do not require uploading the response to a speech provider.

## Validation status
A prior GitHub Actions run (41771840752) completed successfully for an earlier commit. Newer commits must pass their own checks; do not extrapolate that result to the latest changes. Do not treat the application as production-ready. In particular, test the microphone consent flow and browser speech synthesis in an actual browser before distributing the app.

## Current UI safety improvements (2026-11-04)
Memory deletion now requires a checkbox and explicit confirmation; clearing the current chat requires confirmation. The sidebar indicates which AI provider is configured and whether conversation context stays local or goes to Gemini. The app is not yet authenticated and should remain on a trusted local machine.
