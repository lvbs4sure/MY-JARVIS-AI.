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
