# JARVIS AI Hub — ordered delivery plan

This plan implements ARCHITECTURE.md in tested increments. The owner's pasted
historical discussion is a requirements reference, not an instruction to run old
commands, make purchases or provision hosting. Existing 6.2/7.0 installations,
private documents, .env and stored memories are protected.

## Product direction

A local-first personal AI hub with optional cloud assistance. Local inference
avoids per-request cloud quotas but remains limited by hardware, energy, model
quality and available memory. Online research still requires connectivity.
The independent personal installation and the future hosted platform are
separate products; a local Streamlit session is not a user authentication system.

## Delivery order and acceptance gates

| Order | Deliverable | Current state | Gate before moving on |
|---|---|---|---|
| 0 | Protected foundation, launcher, regression suite, private data boundaries | Working; preserve on every release | Tests pass, old versions untouched, private-file exclusions verified |
| 1 | Local AI readiness, installed-model discovery and session-only routing | Implemented; 61-test suite passed; missing-runtime browser check passed | Local inference and model switching still need an installed runtime/model benchmark |
| 2 | Install and benchmark a hardware-appropriate local runtime/model | Owner-approved isolated Ollama/model installed; live inference deferred by low RAM | Runtime/model integrity and isolation passed; await ≥2 GiB free RAM for latency/answer benchmark; no forced default change |
| 3 | Reliable model router and provider health | Partial: Gemini/Ollama adapters, timeouts and opt-in fallback | Provider health reflects real probes; no silent cloud upload from local mode; outages/quota/model errors tested |
| 4 | Voice reliability and accessible device controls | Partial: per-recording cloud consent, transcription, browser speech | Real microphone-to-reply test; audible speaker confirmation; stop/cancel/retry; preserve text input |
| 5 | Durable personal intelligence | Partial: private SQLite CRUD/search/recall | Topics, preferences, source/provenance, selective export, approved backup/restore, retrieval relevance and isolation tests |
| 6 | Research and approved knowledge library | Not built | Automatic search when useful; visible online activity; citations, timestamps, conflicting-source checks, verified/inferred/unknown labels; approval before saving findings |
| 7 | Documents and project workspaces | Not built | Only user-selected files/folders; preview data flow; no indiscriminate Documents scan; extraction and creation verified in fixtures; no automatic overwrites |
| 8 | Permissioned actions and audit trail | Not built | Typed tool allowlist, scoped paths, preview, approval for sensitive actions, cancellation, audit and recovery; model text never directly executed |
| 9 | Planning and task verification | Not built | Task graph, checkpoints, step results, retries, cancellation and independent verification; no false completion |
| 10 | Richer avatar, local speech and continuous dialogue | Partial visual shell only | Hardware-budgeted 3D fallback, actual speech-driven animation, opt-in wake word, mute, interruption and local STT/TTS tests |
| 11 | Desktop distribution and trusted updates | Partial: working Windows batch launcher | Versioned releases, rollback, migration tests, clean-install test, dependency scanning, performance measurements |
| 12 | Owner-controlled hosted platform | Planned only | Separate security design; strong authentication/MFA, tenant isolation, every account owner-approved, roles, revocation, encrypted secrets, recovery and deployment approval before any cloud spending |

Stages can share groundwork, but unverified features must remain labelled
unverified. Each completed increment gets tests, runtime evidence, release notes
and a development-branch commit. No guessed progress percentages.

## Confirmed decisions from the owner's historical blueprint

- The friend's KAVI assistant is a benchmark, not a shared installation or copied product.
- The supplied cinematic holographic reference guides the interface; telemetry is genuine.
- Prefer local models; cloud providers are optional resources, not compulsory dependencies.
- Online research may run automatically when useful and must display sources.
- Long-term knowledge/memory saves require the user's approval.
- Future account requests require owner approval. Root Owner, Administrator,
  Moderator and Standard User roles need real enforcement and recovery safeguards.
- AWS and hardware upgrades remain proposals, not approved purchases or provisioning.
- The pasted discussion ends with a question about direct file uploads, not a
  confirmed answer. User-selected upload is the proposed safe implementation.

## Additional engineering recommendations

1. **Quality scorecard:** maintain reproducible tasks for reasoning, citations,
   memory relevance, coding and tool accuracy. Measure outcomes before claiming
   improvement; "best in the world" is an aspiration, not a test result.
2. **Provider capability registry:** record actual installed/available models,
   context limits and supported modalities. Benchmark before routing tasks.
3. **Resource governor:** low-memory warnings, bounded histories, pause controls,
   model unloading and a lightweight UI mode. Avoid competing large models on
   the current 8 GB laptop.
4. **Privacy/data-flow ledger:** show what stays local and what goes to a provider;
   never include credentials in prompts, logs or diagnostic exports.
5. **Recovery first:** dry-run imports, approved backups, restore fixtures and
   rollback before any schema migration. Never test destructive recovery on real data.
6. **Tool safety:** schema validation, path containment, bounded subprocesses,
   explicit approvals and prompt-injection fixtures before granting actions.
7. **Portable architecture:** preserve adapters and storage APIs so the shell can
   later move beyond Streamlit without rebuilding the brain or migrating blindly.
8. **Release discipline:** feature flags, dependency checks, accessible controls,
   regression tests and a capability matrix distinguishing live, simulated,
   user-reported and not-yet-tested behaviour.

## Proposed hub capabilities to add through the stages

- **Mission Control:** resumable jobs, visible dependencies, approval checkpoints
  and evidence for each completed action, rather than an opaque agent spinner.
- **Model Lab:** compare eligible local/cloud models on approved nonpersonal
  benchmark tasks; show quality, latency, memory and cost before choosing defaults.
- **Knowledge Atlas:** user-owned topic links, provenance, freshness reviews and
  correction controls, with no automatic invention or saving of personal facts.
- **Artifact Studio:** preview documents, spreadsheets, reports and code changes;
  approve destination paths and meaningful overwrites before writing.
- **Trust Centre:** a plain-language record of provider routing, data shared,
  active tool permissions, approvals and revocation. Never expose credential values.
- **Permissioned Skills:** opt-in integrations with declared capabilities and
  isolated execution. No unreviewed third-party plugin or model-generated code runs.
- **Graceful Offline Mode:** preserve local chat/memory when eligible models are
  installed; label unavailable research and stale knowledge instead of inventing results.

These are proposals, not implemented features. They enter the matching delivery
stage only after its privacy, resource and verification gates pass.

## Current next checkpoint

Stages 1 and the preparation portion of stage 2 are implemented. The owner
approved the isolated setup; do not request that same approval again. See
`LOCAL_AI_SETUP.md` for the verified runtime/model and outstanding RAM gate.
Readiness checks and session routing do not install software, download models,
change .env, read personal documents or migrate the memory database.

The live laptop check found 7.8 GiB total RAM and less than 2 GiB available at
the sampled times. Disk space was sufficient, but Ollama was not reachable.
Keep the existing working provider selected until a local model passes an actual
resource/latency/quality benchmark. No application was closed to free memory.


## MARK LIV capability parity — approved implementation backlog (2026-11-04)

Reference: publicly documented FatihMakes MARK LIV features (architecture inspiration,
not permission to copy its source, artwork, name or non-commercial licensed code).
Build independent implementations; check licenses of any separately reused assets.
The following are **requirements**, not claims of implemented or tested features.

### A. Conversation and voice — prioritize after provider stability
- Opt-in low-latency streaming conversation with visible connection status and
  explicit cloud/local routing, interrupt/barge-in and cancellation.
- User-selectable microphone and speaker, actual device validation, mute,
  push-to-talk, optional locally processed wake word and self-echo prevention.
- De-duplicate partial transcripts and replies; reconnect without losing
  session history; display latency and helpful errors for 504/429/offline cases.
- Never record or upload when muted; cloud audio needs informed permission.
- Gate: physical Windows mic → transcript → answer → audible playback, plus
  unplug/reconnect, interruption and no-duplicate tests.

### B. Avatar and HUD — staged, resource-aware
- Real listening/thinking/speaking/error/sleep states, audio-linked mouth
  animation, blink/gaze, expression, theming, and a reactor-core alternative.
- Lip movement must follow audible speech timing, not fake/random animation.
- Start with lightweight rendering on the current 8 GiB integrated-GPU laptop;
  evaluate a separate desktop shell only after voice is reliable.
- Gate: frame-rate/RAM measurements, accessibility and synchronized playback.

### C. Memory and personal context
- Durable facts with categories, provenance, timestamps, edit/delete and
  explicit user-approved saves; bounded prompt core plus searchable index and
  on-demand recall rather than dumping all memories into every model call.
- Session continuity, optional summaries, reminders and user-controlled
  exports/backups; no silent deletion or private-data migration.
- Gate: recall of old facts, corrected facts and revoked facts across restarts.

### D. Skills, research and productivity
- Capability registry that accurately describes available tools and limits;
  schema-validated, allowlisted skills with per-skill permissions.
- Research/news/weather with source URLs, timestamps, conflict checks and
  clear network-use indicators; never invent live data.
- Selected-file reading, document review, code helper, quiz, clipboard tools,
  project workspace, reminders and scheduled topic monitoring.
- Optional calendar, messaging, browser and media integrations through explicit
  connections and per-action consent. Flight/game/home/3D-printer features are
  separate opt-in integrations, not baseline installation requirements.
- Gate: fixture-based tool tests, source attribution and permission checks.

### E. Computer control, recovery and mobile access
- Previewable file/window/settings actions with scoped permissions, activity
  journal, cancellation and truthful execution verification.
- Reversible operations should have a tested undo journal; destructive,
  external or irreversible actions require direct user confirmation.
- Never allow a model response to self-approve an action or execute raw shell.
- Optional paired phone dashboard only after authentication, transport
  security, revocation and local-network threat review.
- Gate: path traversal/prompt-injection tests, rollback tests and real Windows
  integration tests in a disposable test workspace.

### F. Quality, release and ownership
- Hardware governor for RAM/CPU/battery; no local inference when memory is
  insufficient. Graceful Gemini fallback requires explicit cloud permission.
- Real feature-status matrix (planned / implemented / Windows-verified);
  benchmark quality, latency, RAM, voice and failure recovery on every release.
- Signed/versioned Windows packaging, rollback, clean install and migrations.
- Hosted multiuser product remains a separate later security project, with
  owner-controlled access and no deployment or spend without approval.

### Immediate execution order

1. Stabilize Gemini timeout/retry classification and user-visible retry.
2. Implement and verify voice/device/streaming foundations in small commits.
3. Improve indexed, consent-based memory retrieval.
4. Add a secure skill registry, then research and document actions.
5. Implement preview/approval/undo before computer-control features.
6. Add measured avatar lip-sync and desktop packaging.
7. Expand opt-in integrations and only then consider hosted accounts.

**Do not install or run MARK LIV code wholesale.** Its repository advertises a
CC BY-NC 4.0 non-commercial license; independent development avoids accidental
license conflicts, especially for a future commercial or hosted AI hub.

### Reliability increment — 2026-11-04
- Implemented typed request outcomes, bounded transient retries (two attempts, 15 s per attempt), explicit 429/access/model errors and credential-safe error text.
- Dashboard retry replaces a failed reply, preserves its provider, excludes failures from future prompts, and displays provider/latency/status.
- Local inference and fallback now enforce the 2 GiB RAM gate in the provider adapter as well as the UI.
- Windows verification: 75 automated tests passed; production dashboard reloaded at port 8501 with Gemini still selected. Simulated 504/429/offline, retry/no-duplicate and low-RAM gates passed.
- Live Gemini and new audio upload checks pending explicit cloud-test permission. Provider stability gate remains partially verified, not complete.

### Voice foundation increment — 2026-11-04
- Implemented microphone mute that removes the recorder and blocks submission, resets capture identity on mute/unmute, and retains duplicate-upload guards. Added a defensive muted transcription argument.
- Spoken replies use explicitly selected installed local voices only, with speed, pause/resume, stop, and Markdown-to-speech cleanup. No default remote browser voice is used. Added a nonpersonal local playback test in Voice.
- Transcription now shares bounded, credential-safe Gemini error handling.
- Windows browser verified: mute removes Record; Microsoft David/Mark/Zira local voices discovered; playback reached Finished; interruption showed Paused, Resume showed Speaking, Stop showed Stopped. This is browser event verification, not physical audibility verification.
- Final Windows suite: 80 tests passed after integrating remote memory lookup and panel changes through 51f54be. Existing holographic interface preserved; desktop layout checked at 1280 x 800 and temporary viewport reset.
- Live approved tests: direct nonpersonal text failed HTTP 504 in 32.241 s; generated audio failed timeout in 32.24 s; dashboard text succeeded in 1.710 s and 10.770 s with genuine Gemini responses. No further cloud test quota was used.
- Remaining: physical mic/speaker loop, unplug/reconnect, device selection within JARVIS, streaming/cancellation/barge-in/wake word and echo prevention. No claim of MARK LIV voice parity.
- Blocker: intermittent Gemini service/timeout failures, especially audio. Do not proceed to heavier local inference with less than 2 GiB free RAM or install a new speech engine without approval.

- Integrated-panel layout correction: research/file previews remain available in a collapsed section after Shortcuts; removed the duplicate session-log panel. Main chat, code, Voice and Settings retain their original order.
- Layout correction Windows-verified at 1280 x 800; final complete suite: 81 tests passed.

### KAVI-style panels and interruptible conversation — 2026-11-04
- Latest branch checked; c6d84f7 is already integrated. Original JARVIS face/artwork and interface retained. No KAVI or MARK LIV source/artwork copied.
- Conversation engine: bounded session-owned background requests; credential-safe failures; cancellation suppresses retries and late replies; completed results consumed once. No raw shell or computer actions are enabled.
- Audio transcription uses one 30-second attempt, avoiding an automatic second audio upload. Mute cancels pending transcription and rejects stale completed transcripts before an answer can start. In-flight provider requests cannot be recalled; a new request waits for the existing connection to finish.
- Core and UI tested together on Windows: 94 automated tests passed, including cancellation races, duplicate suppression, mute, service errors, capacity limits and preview validation. Physical microphone and speaker acceptance gate remains open.
- Panels now share the holographic styling; file preview is bounded, inert and local-only. Research remains explicitly disconnected. Primary controls remain above optional workspaces.
- Windows browser verified: simulated slow-request interruption (late reply discarded, input restored, activity logged), production Gemini reply JARVIS_CONVERSATION_READY in 12.496 s, spoken-reply interruption to Stopped, and real local-only preview of a new nonpersonal sample.
- Other approved live tests failed: background text HTTP 504 in 33.460 s; generated-audio transcription connection error in 0.81 s. DNS resolved and unauthenticated HTTPS reached Gemini (403); no proxy or Windows network setting change.
- Remaining gates: reliable audio provider, physical mic/speaker loop, streaming/barge-in, device reconnection and synchronized listening/speaking avatar. See tests/KAVI_WINDOWS_VALIDATION_2026-11-04.md.
- Existing Windows offline speech recognizer detected without installation. Benchmark deferred at 0.96 GiB free RAM (below conservative 1 GiB speech-only test gate); no offline inference forced or fallback claimed. Private configuration and memory preservation checks passed.

### Human-like embodiment foundation — 2026-11-04
- New independent animated wireframe face, idle blink and gentle head motion; original holographic scene remains selectable. No KAVI or MARK LIV assets/code copied.
- Central face speech uses installed local voices only. Real speech start/end/pause/resume/interrupt events control its state; browser boundary events pulse the mouth. This is approximate word timing, not viseme-quality lip-sync or a photorealistic human.
- Windows browser verified READY to SPEAKING to READY, interruption to Stopped, an advancing rendered-frame counter and 14 real speech boundary events during a nonpersonal local demo. No new cloud request or installation.
- Reference layout now shows system/activity left, face/research centre and chat/controls/files right; code examples are collapsed. Existing private memory, consent guards and provider configuration retained.
- Added opt-in local camera preview with Start/Stop, audio disabled, pending-request guard, 20-second startup notice and stop-on-page-hide/visibility handling. No frame capture, storage or network upload path. Camera starts only on an explicit click.
- Camera hardware gate FAILED/UNVERIFIED: user approved local preview and reported selecting Allow; browser did not produce video (0 x 0, readyState 0), and startup reached the timeout notice. Stopped and unmounted camera controls (0 camera iframes remaining). No camera screenshot taken or image uploaded. JARVIS visual understanding is not implemented or claimed.
- Still required: physical microphone/speaker loop, reliable transcription, realistic lip-sync/body movement, optional visual understanding with explicit per-image cloud consent, and working source-backed research.
- Automated Windows suite: 100 tests passed after integrating remote memory-search regression d9dc842. Desktop console checked at 1280 x 900, temporary viewport reset, camera controls off and absent. User confirmed hearing JARVIS through the laptop speakers/headphones; no additional Gemini call was made.

### Restore approved appearance and add opt-in chat history — 2026-11-04
- Owner clarified that the original holographic female JARVIS is the desired face; reference projects supply feature ideas only. Restored that scene unconditionally in the running dashboard, ignoring stale experimental avatar selections. Research/file panels are compact again. Experimental face code is not active.
- Added separate per-installation local chat history, off by default. Sidebar Chat history enables saving, lists saved conversations, starts a new conversation and explicitly reopens a saved chat without a model call. No automatic audio/image/file storage. Configured provider keys are masked before persistence. The history database is ignored by Git and separate from memories.
- Existing saved conversations survive starting or clearing the current session. No auto-deletion or migration. Per-chat limits reject oversized updates while preserving the previous saved version; latest 100 conversations are shown.
- Verification: 106 Windows tests passed, including persistence through fresh database connections/app sessions, update without duplicate rows, installation isolation, key masking, opt-in/no-file default, reopen without a cloud call and clear-session preservation. Production browser showed the original face and history saving off. No production history database was created during testing.
- .env and private memory preservation checks passed. Camera remains off/unverified; no new cloud calls, installations or camera captures. Full voice conversation, visual understanding and live research remain open features.

### Compact console organisation — 2026-11-04
- Kept the approved holographic face/artwork. Reduced surrounding spacing and replaced large secondary sections with a two-row eight-tool dock, using native popovers for History, Files, Research and Camera alongside Memory, Voice, System and Settings. Code is a small collapsed section.
- Added truthful session chips for selected route, mic manual/muted mode, history preference and idle/busy state. No connection-health claim. History is now reached directly from the dock instead of the sidebar.
- Verification: all 106 automated Windows tests passed after the UI restructuring, including existing history, memory, chat, privacy, voice and cancellation checks. Actual browser verified opening History/Files/Research/Camera, unchanged original face and camera controls off. Desktop checked at 1280 x 900; narrow-screen dock checked at 390 x 844 with four 78 px buttons sharing the same row. Temporary viewport reset.
- Private .env and memories preservation checks passed. No camera activation, cloud requests, installations or new storage consent. Camera vision, live research and full voice acceptance gates retain their previous incomplete status.
