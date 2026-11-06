# Windows verification — KAVI-style panels and conversation foundation

Date: 2026-11-04 (Africa/Lagos). Branch: jarvis-new-foundation.
Reference commit c6d84f7 was already present; no newer remote changes were available at the initial fetch.

## Feature status

| Feature | Tested status |
|---|---|
| Existing holographic face | Preserved; visible in the production Windows browser |
| Avatar processing/transcribing/error states | Connected to actual request lifecycle; automated UI checks |
| Avatar listening/speaking synchronization | Not implemented; no simulated claim of lip-sync or microphone activity |
| Live system monitoring | Existing real local readings visible; unsupported sensors remain N/A |
| Activity log | Session-only metadata; interruption verified in Windows browser |
| Research workspace | Styled and visible; explicitly disconnected, no invented results |
| Selected-file preview | 1 MB widget limit; validated UTF-8 TXT/MD/CSV, 4,000-character inert preview; actual browser upload verified |
| Command input | AI chat works; no system-command execution |
| Microphone controls | Consent, mute, duplicate guard and stale-transcript cancellation tested with fixtures; physical device loop unverified |
| Interrupt request | Slow simulated provider interrupted in actual browser; late answer omitted, input restored and log updated |
| Interrupt speech | Real Gemini reply playback stopped in actual browser; status Stopped |

## Live tests approved for this increment

- Background nonpersonal text request: FAILED, HTTP 504, 33.460 seconds.
- Production dashboard nonpersonal text: PASSED, JARVIS_CONVERSATION_READY, 12.496 seconds.
- One generated WAV transcription: FAILED, connection error, 0.81 seconds. No physical microphone recording uploaded. No automatic second audio upload.
- Read-only DNS resolution: PASSED. Unauthenticated HTTPS models endpoint: HTTP 403 (TLS/endpoint reachable). No proxy configured. No Windows network/security settings changed.
- Existing key/model environment values matched the private configuration without displaying either key or its contents.

## Local verification

- 94 automated Windows tests passed, including late-result races, bounded workers, consumption exactly once, mute/completed-transcript race, failed-service audio upload budget, file size spoofing, binary/encoding rejection and existing memory/privacy regressions.
- Actual browser preview used only a new nonpersonal sample. Script markup appeared as inert read-only text; sample then removed from the uploader.
- Desktop panel layout checked at 1280 x 900; temporary viewport reset. Optional panels stay below primary Shortcuts. Production dashboard retained at http://127.0.0.1:8501/.
- Disposable interruption dashboard used a separate database, simulated provider and loopback port 8511; it was closed and stopped afterward.
- No installations, purchases, private file migrations or local inference were performed.

## Open acceptance gates

Reliable Gemini transcription remains blocked by intermittent provider/connectivity failures. Physical Windows microphone to transcript to answer to audible speaker, unplug/reconnect, device selection, streaming/barge-in and synchronized avatar listening/speaking remain open. Interruption discards responses and stops future retries; it cannot recall data already sent or forcibly abort the provider's current HTTP operation. New requests wait for that operation to finish.

The existing Windows offline speech recognizer was detected (metadata query only). Its generated-sample benchmark was deferred: available RAM was 0.96 GiB, below the conservative 1 GiB gate for this prospective speech-only test. No offline engine was started for inference, integrated, or marked working. Gemini configuration remains unchanged.
