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


## Restored original vision and scope (2026-11-04)

This section records the owner's earlier project blueprint. **Planned does not mean implemented or approved for deployment.** The current Streamlit app is only a local prototype, not the finished JARVIS.

### Design benchmark
The owner's friend's KAVI – MARK IV is a **reference to surpass**, not a product to copy and not the same as the separate idea of giving friends independent starter copies. Aim for an original, more advanced visual command centre: expressive animated 3D avatar, listening/speaking waveform, live clock and weather, system monitoring (CPU, RAM, storage, battery, network and available temperature), activity history, research centre, file/project centre and multiple customizable workspaces.

### AI, speech and action architecture
- **Local-first brain:** Ollama and hardware-appropriate downloaded models; optional cloud models, model routing and provider fallback. Avoid compulsory single-provider quota dependence; do not promise unlimited compute.
- **Personal intelligence:** persistent, user-controlled memory, preferences, contextual recall, planning and task verification.
- **Voice:** wake word, continuous dialogue, natural speech, interruption and voice personalities. These advanced functions are goals, not current capabilities.
- **Research:** automatically look up external/current information when needed; show sources, compare conflicting claims, separate verified facts from uncertainty, and suggest useful findings for saving. **Require the user's approval before saving research to long-term knowledge.**
- **Files and actions:** document analysis and creation, approved application/file control, programming and multi-step automation. Require permission before sensitive changes (deletion, installation, sending messages, irreversible changes). Maintain an audit trail.

### Two distinct distribution models
1. **Independent friend starter (current direction):** each person forks/copies code into a separate installation with their own keys, database and customizations. No central account system or shared personal data.
2. **Future owner-controlled hosted platform (not built):** planned managed AWS hosting and potential scale to thousands of users, invitation-only access and **owner approval for every account request**, independent user data, Windows/mobile clients, authentication, permission roles (Root Owner, Administrator, Moderator, Standard User), session revocation, audit logs, backups, recovery, service monitoring and a Root Owner dashboard. Root ownership requires technical and operational safeguards, not merely UI labels. No AWS resources or accounts have been provisioned by this prototype.

### Historical hardware assessment
The supplied earlier discussion records: HP EliteBook 840 G7, Windows 11, Intel Core i5-10310U, 8 GB RAM (2x4 GB), Intel UHD graphics, 256 GB SK hynix SC401 SATA SSD, about 144 GB free at that time. Proposed, **not purchased or compatibility-verified**: up to 64 GB RAM, a compatible 2 TB NVMe SSD, and eventually a separate NVIDIA GPU workstation while keeping the laptop as a control terminal. Recheck hardware and compatibility before purchases or model installation.

### Protected prior versions
Preserve the user's existing JARVIS 6.2, JARVIS 7.0 and old memory database. Work only on the new isolated project; back up before migration. Never commit keys, private memories, recordings or local databases.

### Original nine-phase delivery plan
1. Hardware assessment, backups and foundation
2. Independent local AI brain and routing
3. Advanced custom command-centre interface (beyond Streamlit starter UI)
4. Long-term memory and personal intelligence
5. Advanced voice and wake word
6. Research, document understanding and knowledge
7. Permissioned computer control
8. Planning, multi-step execution and recovery
9. Integration, performance, security and release testing

### Release gates and non-goals
- Keep the existing prototype usable while adding features in isolated, tested increments.
- Automated tests do not prove microphone hardware, browser speech playback, live research or real computer control.
- Never deploy the current single-user Streamlit app as an authenticated multi-user service.
- Avoid unnecessary purchases or paid hosting before a validated architecture and explicit authorization.
- Keep a clear distinction between owner-confirmed decisions, historical proposals and verified implementations.

## Today’s isolated Windows increment (2026-11-04)

The foundation dashboard now exposes private memory search, requires explicit
per-recording upload consent, and lets the user review/edit a transcript before
sending it as chat. Browser speech reports completion, stop, and failure. The
launcher reuses the installation’s environment, preserves private configuration,
skips repeated dependency installation, and binds to loopback. Gemini uses one
bounded retry for transient connection/service failures. These changes extend
the usable foundation; they do not implement the advanced command-centre roadmap.

See `tests/WINDOWS_VALIDATION_2026-11-04.md` for observed browser and automated
results, including pending microphone/audibility checks and intermittent network
failures. No old installation or private memory database was migrated.


## Approved comprehensive design baseline — holographic command centre (2026-11-04)

**Owner direction:** Build the complete JARVIS vision into the architecture first; use the shared LISA holographic desktop image as a **visual benchmark**, not copied artwork, branding or fake telemetry. Implement progressively and review refinements afterward. This document is the source of truth for the target design; items labeled *planned* are not working features.

### Target experience and visual composition
- **Central identity:** original JARVIS humanlike holographic character (not LISA), blue/cyan/violet light, responsive facial expressions, eye focus, mouth movement, and listening/thinking/speaking/idle/error states. A lightweight animated fallback must run on the owner's current integrated-GPU laptop; heavier 3D is optional and must degrade gracefully.
- **Left workspace:** live CPU/RAM/disk/network/battery metrics with clear units and unavailable states; searchable terminal/diagnostics with approved commands only; time-stamped activity logs.
- **Centre workspace:** holographic avatar, reactive audio visualizer, live clock, optional weather with source and freshness, assistant state, wake/mute controls, and accessibility alternatives.
- **Right workspace:** AI conversation with voice and text, code snippets, verified research citations, action cards with explicit approvals, shortcut tiles, project and document status.
- **Navigation:** Home, Chat, Research, Documents, Projects, Automations, Memory, System, Settings, and Owner Console (Owner Console visible only in future authenticated hosted deployment). Customizable layout, keyboard navigation, reduced-motion mode, responsive small-screen layout, readable contrast, and honest system status.
- **Visual direction:** cinematic cyberpunk night scene, luminous glass panels, crisp typography, fine cyan outlines, violet highlights, restrained animation. Do not present decorative figures as live measurements.

### Functional components and contracts
1. **Desktop shell:** a responsive multi-panel interface. Initial implementation can remain Streamlit; investigate a desktop shell/web front end when interactive 3D and continuous speech require it. Preserve existing chat and memory APIs.
2. **Telemetry:** collect Windows metrics via optional psutil and OS APIs, with bounded sampling, safe subprocess policy, no elevated privileges, and clear N/A when unavailable. No invented temperatures, throughput or CPU numbers.
3. **Voice pipeline:** microphone capture -> per-recording consent if cloud transcription -> speech recognition -> conversation -> text response -> optional speech playback. Later add local speech recognition, wake word, voice activity detection, barge-in, auto playback after explicit enablement, device selection and voice personalities. Clearly show mute and cloud-upload states.
4. **Brain/router:** Ollama local-first, optional Gemini cloud with transparent data routing, timeouts, fallback, model-health checks, prompt-injection boundaries and explicit costs/limits.
5. **Memory/knowledge:** local durable user-owned memory, topics, preferences, provenance, edit/delete/export, opt-in ingestion, retrieval, retention and backup. Research facts require user approval before long-term saving.
6. **Research:** multi-source browsing, freshness, citations, claim verification and disagreement tracking, with verified/inferred/unknown labels.
7. **Document and project centre:** user-selected files and folders only, previews, text extraction, summarization, drafting, project workspaces and versioned outputs. No indiscriminate scan or upload of Documents. Sensitive content remains local unless explicitly authorized.
8. **Computer actions:** scoped permissions for reading, writing, opening apps, browsing, code execution and automation; preview planned actions; require confirmation for deletion, external transmission, software installation and irreversible changes; audit outcomes and allow cancellation.
9. **Planning and recovery:** task graph, checkpoints, progress logs, retries, cancellation, verified outcomes and error recovery; no false completion reports.
10. **Distribution:** separate independent friend copies and a future invitation-only, owner-approved hosted system with Root Owner/Admin/Moderator/Standard roles, per-tenant isolation, authentication, encryption, audit logs, backups, revocation and recovery. AWS hosting is not authorized or provisioned.
11. **Operations/security:** least privilege, loopback binding for prototype, encrypted secrets, dependency scanning, signed releases when available, data backup/restore tests, resource budgets and user-visible diagnostics.

### Build sequence and acceptance gates
- **A — immediately:** visually faithful original multi-panel dashboard, animated lightweight avatar, responsive dark UI, genuine provider/memory/chat status; preserve current app functionality.
- **B:** real Windows telemetry and event log, with permissions and N/A fallback; verified local hardware readings.
- **C:** stable end-to-end microphone-to-reply and accessible audio controls; physical speaker validation; optional local speech.
- **D:** research, files/projects and memory management with user-approved data flow.
- **E:** safe permissioned computer operations, planner, checkpoints, and action audit trail.
- **F:** richer 3D avatar, advanced continuous voice, desktop packaging, performance profiling.
- **G:** separately designed hosted owner-controlled platform after security review and explicit provisioning approval.

**Acceptance:** tests + Windows runtime checks + human-visible verification. Passing CI alone is not proof of hardware, speaker, telemetry or hosted readiness. Do not claim a feature is complete until it is verified in its target environment. Never modify the user's old installations, private documents, memory database, or .env without the relevant scope and backup.

## Reference-led holographic revision (2026-11-04)

The owner rejected the earlier vector-face layout and supplied the cinematic
LISA reference again. The approved generated scene now supplies a realistic
JARVIS holographic character and cyberpunk workstation backdrop. Floating
functional windows follow that composition: real system overview/diagnostics
and session logs on the left, chat/code/shortcuts on the right. Memory, voice,
system settings and personalization open from shortcut controls.

The character is raster artwork with animated scan/glow effects and request-driven
ready/thinking/error status; it is not a fully rigged 3D face or lip-sync system.
The code window displays a read-only example or a fenced code block from the
latest AI reply. Nothing in it is executed automatically.

Telemetry uses psutil and filesystem counters, refreshed in a separate two-second
Streamlit fragment. CPU sampling is bounded to 0.1 seconds. Network rates require
two monotonic counter samples; counter resets and missing sensors remain N/A.
Temperature is unavailable on the tested Windows hardware. Network link status
does not imply Gemini or internet connectivity. Sensor history is bounded to 30
in-memory samples; activity stores 30 action records without prompt/note contents.

The scene is a bundled public visual asset; private files are never placed in
the static asset directory. The original .env and stored memory contents are
checked for preservation. Advanced research, file actions, continuous voice,
permissioned computer control and hosted accounts remain later architecture phases.

## Ordered implementation and additional quality gates

`DELIVERY_PLAN.md` is the ordered delivery checklist for this architecture,
including the owner's historical blueprint supplied on 2026-11-04. It records
confirmed decisions, proposals and unverified features separately. The immediate
next checkpoint is local-AI readiness and installed-model discovery, followed by
an approved hardware-appropriate local-runtime benchmark. No API provider can be
promised unlimited service, and no global-quality ranking is claimed.

New engineering gates include reproducible capability evaluations, explicit data
flow, resource budgets, approved recovery/migration tests, typed tool boundaries
and release/rollback discipline. These strengthen the design without authorizing
cloud spending, system-wide software changes or personal-data migration.
