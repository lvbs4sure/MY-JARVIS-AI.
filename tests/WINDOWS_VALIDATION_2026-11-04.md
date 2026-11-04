# New JARVIS Windows validation — 2026-11-04

Scope: isolated `jarvis-workspace`, branch `jarvis-new-foundation`.
No previous JARVIS 6.2/7.0 files or databases were migrated or modified.

## Observed passes

- Latest upstream changes pulled with fast-forward only.
- 33 automated tests passed, including dashboard memory operations, literal
  memory search, launcher setup preservation, speech escaping/status, transcription
  empty-result handling, private fallback, and recovery after a simulated DNS failure.
- The actual Windows batch launcher started the dashboard on 127.0.0.1:8501.
  Running its setup check again skipped dependency installation.
- Browser memory save/search/edit succeeded with a disposable verification note.
- Gemini returned the edited note's colour, `amber`, in the actual dashboard.
- The edited note persisted across a full server restart and was displayed in the
  browser afterward. Confirmed deletion removed the disposable note.
- Gemini transcribed generated local test audio and recognized `turquoise`.
  This verifies the audio API, not microphone hardware.
- Browser speech reached `Finished`. Initial Stop test incorrectly displayed
  `Speech error: interrupted`; a fix and regression check were added.
- The corrected Stop control was retested in the actual browser and displayed
  `Stopped`. Final live dashboard chat returned `JARVIS_READY`.

## Limitations and pending hardware checks

- Some live Gemini requests failed with a transport `ConnectError`; subsequent
  requests succeeded. A single bounded retry was added and tested independently.
  Internet/provider availability cannot be guaranteed.
- Real microphone capture/transcription awaits the user's sample and any OS or
  browser microphone permission. Generated audio is not a microphone pass.
  Clicking Record in the in-app browser did not produce a captured sample.
- A final generated-audio API recheck failed with `ConnectError`, despite the
  earlier successful transcription. Audio service connectivity is intermittent.
- A browser speech completion event does not independently prove sound was
  audible through the laptop speakers; a listener must confirm it.
- Ollama is not installed/running. Fallback is tested with simulated failures,
  off by default, and cannot yet be described as live-local-model verified.
- Wake word, continuous conversation, autonomous computer control, research,
  3D command centre, and hosted accounts remain roadmap items in ARCHITECTURE.md.

No keys, recordings, logs, private configuration, or memory database belong in Git.
