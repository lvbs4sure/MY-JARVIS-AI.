# JARVIS — new Windows build

A fresh, single-user personal AI assistant. This does not modify the old Windows project.

## Start on Windows
1. Download the **jarvis-new-foundation** branch ZIP from GitHub and extract it to a **new folder**.
2. Double-click `START_JARVIS.bat`. Python 3.11+ must already be installed. The first launch installs packages and can take several minutes.
3. JARVIS opens at http://localhost:8501 (open that address manually if your browser does not open).

The launcher reuses this folder's private environment, checks dependencies only
when requirements change, and binds the dashboard to `127.0.0.1`. Keep its window
open while using JARVIS; press Ctrl+C there to stop it. Double-clicking again
while it is running opens the dashboard. `START_JARVIS.bat --check` checks setup
without starting a second server. Startup never imports old JARVIS data or keys.

## Everyday use

The cinematic dashboard uses floating windows. Open **Memory**, **Voice**,
**System**, or **Settings** from the Shortcuts window at the lower right. Memory
management and personalization are now in those popovers. System can pause live
telemetry; Settings can reduce animation. The top-left arrow opens session totals.

- Type in **Ask JARVIS** and press Enter. Cloud chat needs an internet connection.
- Save notes with **What should I remember? → Save memory**. Search them with
  **Search memories**. Expand a note to edit it or confirm its deletion. Notes
  stay in this installation's local SQLite database after restarting.
- Ask about a saved note to use it in conversation. The latest 100 notes are
  included as context; the search box searches local saved notes independently.
- Press **Record**, speak, then stop. Allow microphone access in the browser if
  prompted. Check the explicit upload consent box, then press **Transcribe**.
  Review or edit the recognized text and press **Send transcript**. Transcription
  requires `JARVIS_VOICE_PROVIDER=gemini` in this copy's private configuration.
- Press **Speak reply** for browser speech, or **Stop**. The status reports
  Starting, Speaking, Finished, Stopped, or an actual speech error. Speaker volume
  and microphone availability depend on Windows and the browser.
- **Clear conversation** removes the current session's chat after confirmation;
  it does not delete saved memories. Chat history itself does not survive restart.

Gemini requests have a 15-second per-attempt timeout and one retry for temporary
connection/service failures. If both fail, the dashboard reports the error;
an error message is not a successful AI answer.

## Configure the AI
The new `.env` is created automatically from `.env.example` on first launch.

**Gemini (uses the internet):** If you already have a Gemini API key in your old project's private `.env`, copy only the `GEMINI_API_KEY` value into the **new** `.env` file. Set `JARVIS_PROVIDER=gemini`. Do not share or upload either `.env` file.

**Ollama (local model):** The default is `JARVIS_PROVIDER=ollama`. Install Ollama separately, then run `ollama pull llama3.2:3b` once. JARVIS communicates with local Ollama at `http://127.0.0.1:11434`.

## Features

For temporary Gemini transport errors, rate limits, and HTTP 5xx outages, set
`JARVIS_OLLAMA_FALLBACK=on` in the new `.env` to try the configured local Ollama
model. Install and start Ollama and pull that model first. Fallback replies are
labelled, and an unavailable local service produces an explicit error. Invalid
keys and model access errors do not trigger fallback. The Gemini key is never
included in Ollama requests.
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
