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
