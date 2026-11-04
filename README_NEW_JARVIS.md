# JARVIS — new Windows build

A fresh, single-user personal AI assistant. This does not modify the old Windows project.

## Start on Windows
1. Download the **jarvis-new-foundation** branch ZIP from GitHub and extract it to a **new folder**.
2. Double-click `START_JARVIS.bat`. Python 3.11+ must already be installed. The first launch installs packages and can take several minutes.
3. JARVIS opens at http://localhost:8501 (open that address manually if your browser does not open).

## Configure the AI
The new `.env` is created automatically from `.env.example` on first launch.

**Gemini (uses the internet):** If you already have a Gemini API key in your old project's private `.env`, copy only the `GEMINI_API_KEY` value into the **new** `.env` file. Set `JARVIS_PROVIDER=gemini`. Do not share or upload either `.env` file.

**Ollama (local model):** The default is `JARVIS_PROVIDER=ollama`. Install Ollama separately, then run `ollama pull llama3.2:3b` once. JARVIS communicates with local Ollama at `http://127.0.0.1:11434`.

## Features
- Chat with Gemini or a local Ollama model (when configured)
- Save, edit and delete private SQLite memories
- Personalize assistant name and conversation style
- Record voice and explicitly opt in to sending audio to Gemini for transcription
- Speak replies using the browser's speech engine (click Speak; browser support varies)
- Confirmation before deleting memories or clearing a conversation

## Limitations
This is a development build, not a finished JARVIS command centre. Voice playback and the full Windows dashboard still require end-to-end testing. There is no autonomous computer control, no multi-user account isolation, and no guarantee of offline voice transcription. Friends should each run their own copy and keep separate secrets and databases.

## Privacy
Never commit `.env`, `*.db`, passwords or API keys. Gemini requests send chat and saved memory context to Google's service. Ollama chat stays on the configured local endpoint when running locally; Gemini voice transcription uploads recordings only after explicit confirmation.
