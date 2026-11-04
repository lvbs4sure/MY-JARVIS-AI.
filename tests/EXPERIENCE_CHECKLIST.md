# JARVIS end-to-end experience acceptance checklist

This checklist distinguishes automated verification from real hardware/browser verification. Do not mark an item passed unless it was observed.

## Automated checks
- [ ] Run `python -m unittest discover -s tests -v`; record test count and exit status.
- [ ] Check that a missing Gemini key produces a helpful error without exposing secrets.
- [ ] Confirm memory database isolation and create/edit/delete tests.
- [ ] Confirm the Ollama fallback is opt-in and only contacts localhost.
- [ ] Confirm voice transcription rejects empty and oversized recordings before upload.

## Live Windows checks (require the actual running installation)
- [ ] Launch the dashboard and confirm it responds at `http://127.0.0.1:8501`.
- [ ] Submit a text prompt and verify a non-placeholder Gemini reply appears in chat.
- [ ] Save a harmless test memory, then ask JARVIS to recall it. Verify the reply and delete the test memory.
- [ ] Change the assistant name and personality; verify subsequent reply behavior.
- [ ] Record a microphone sample and explicitly consent to Gemini transcription; verify the recognized text. Do not upload private speech without user consent.
- [ ] Click Speak and Stop on a reply and verify audio playback in the browser.
- [ ] Clear the conversation after confirmation; verify saved memory is not deleted.
- [ ] Restart the application and verify memories persist.

## Privacy and release checks
- [ ] Verify `.env`, API keys, `*.db`, recordings and personal data are not tracked by Git.
- [ ] Verify only the development branch is changed; do not modify the user's old Windows project.
- [ ] Commit code changes after tests; do not claim local browser/hardware tests ran in a cloud-only environment.
- [ ] Keep friend installations independent; this is not a hosted multi-user service.

Record exact failures and environment details without including credentials.
