# JARVIS runtime architecture — implementation contracts

Status: **design and integration contract**, not a claim that all components exist.
This document refines [ARCHITECTURE.md](ARCHITECTURE.md) without replacing the
working Streamlit prototype or changing the owner's local configuration.

## Operating constraints

- Single-user, loopback-bound Windows installation; no shared account security.
- Keep old JARVIS installations, private SQLite memory, `.env`, recordings and
  local uncommitted files untouched. Never use model output as a shell command.
- On the 8 GiB integrated-GPU laptop, prefer lightweight rendering and bounded
  work queues. Local model execution is conditional on measured free RAM.
- Network use, camera, microphone, installations, destructive operations and
  external messages require their own explicit permissions.
- Existing `app.py`, `jarvis_ai.py`, `memory_store.py`, `voice_output.py`
  and `lip_sync.py` remain the compatibility boundary until adapters are tested.

## Layered component boundaries

```text
                   JARVIS Desktop / Streamlit UI
       chat | hologram | status | approvals | activity log
                            |
                 Session / Event Coordinator
           state transitions, job IDs, cancellation
          /             |              |             \
  Conversation      Speech         Avatar         Tool Gateway
  Router            Pipeline       Renderer       (deny by default)
  Ollama/Gemini      mic/STT/TTS    rig/visemes    approvals/audit
          \             |              |             /
                 Verified Event Journal
                            |
           User-owned Memory / Project Store
                     (local SQLite)
```

The coordinator owns **session state** but never stores API credentials in events.
Adapters own provider-specific calls; the UI does not import provider internals.
A renderer receives approved motion data, not unrestricted model instructions.

## Event envelope (proposed v1)

All events use a session-scoped monotonic sequence and a job ID to reject
out-of-order replies and stale callbacks. Example shape:

```json
{
  "version": 1,
  "session_id": "opaque-local-session-id",
  "job_id": "opaque-request-id",
  "sequence": 12,
  "kind": "speech.started",
  "origin": "local_browser",
  "created_at_utc": "2026-11-04T00:00:00Z",
  "payload": {"playback_id": "opaque-audio-id"}
}
```

Allowed event families: `conversation.*`, `speech.*`, `avatar.*`,
`memory.*`, `research.*`, `tool.*`, `system.*`. Validate each payload
against an explicit schema; reject unknown versions, oversized payloads and
unexpected fields. Event journal records metadata and outcomes by default,
**not** raw audio, prompts, personal notes or provider credentials.

## Conversation and cancellation contract

1. A new user turn receives a unique job ID and immutable provider routing
   decision (local or explicitly permitted cloud).
2. Provider responses are accepted only while the job is active. Cancellation
   invalidates the job before signaling the adapter.
3. A stale response cannot overwrite a newer reply, voice state or activity
   status. Timeouts and rate limits produce distinguishable outcomes.
4. Persist a chat turn only according to the user's history preference;
   persistent personal facts require separate approval.
5. Any fallback from local processing to Gemini must be visible and approved
   before private content is sent to the cloud.

## Speech and embodiment contract

```text
user gesture -> microphone permission -> captured audio
    -> local STT or separately approved cloud transcription
    -> conversation job -> reply text -> selected TTS engine
    -> audio clip + same-run viseme events -> playback clock
    -> approved character rig (blink/gaze/mouth/gesture)
```

The existing browser `speechSynthesis` is an accessible fallback and supplies
word boundaries on some browsers; those boundaries **are not** genuine visemes.
The small speaking preview is not the main character's face.

For real lip sync, `lip_sync.LipTimeline` consumes validated same-clip viseme
cues; the renderer samples actual playback time and closes the mouth on pause,
stop, seek beyond clip end, cancellation, and loss of playback. Never synthesize
mouth timings from arbitrary text length and call them accurate.

The original approved blue/violet character remains the default identity.
Real facial movement requires an owner-reviewed, original/licensed rig with
eyelid and speech shapes. CSS glow or moving overlays do not animate the
photographic character itself. No asset uploads or new heavyweight renderer
without permission and resource checks.

## Avatar state machine

```text
ready -> listening -> transcribing -> thinking -> speaking -> ready
  |         |             |             |          |
  +---------+-------------+-------------+----------+--> error
```

`interrupted` is a transition outcome, not a permanent visual state.
The UI must distinguish **ready**, **recording**, **cloud upload pending**,
**transcribing**, **thinking**, **speaking**, **paused**, **interrupted** and
**error**. Do not infer microphone listening from decorative animations.
Reduced-motion preference disables nonessential motion without hiding state.

## Tool and research trust boundary

Model text is **untrusted input**. The tool gateway uses named allowlisted
operations with typed parameters, scoped user-selected paths, bounded timeouts,
previews and explicit approvals for sensitive actions. Never execute arbitrary
shell strings or let model text self-approve. Journal the requested operation,
approval, actual outcome and reversible undo reference where applicable.

Research results carry URL, retrieval time, quoted evidence and confidence
labels (verified / inferred / unknown). Web content is untrusted and cannot
override user instructions or trigger tools. Saving findings to long-term
memory requires a separate user confirmation.

## Delivery sequence and verification gates

| Order | Increment | Evidence needed |
|---|---|---|
| 1 | Provider health, bounded job coordinator and stale-result protection | Timeout/cancel/retry tests; no silent cloud fallback |
| 2 | Voice device state, pause/interrupt, browser lifecycle | Windows microphone-to-speaker test and browser tests |
| 3 | Same-audio viseme adapter and lightweight isolated rig preview | Playback-clock sync, seek/stop, RAM/FPS measurements |
| 4 | Identity-preserving eyelids, gaze, head and gestures | Owner-reviewed rig and observed animation, reduced-motion |
| 5 | Memory provenance, topic recall and export | Approved save, correction, deletion and restart tests |
| 6 | Research and document pipelines | Citations, user-selected files, approval and offline cases |
| 7 | Permissioned tools and resumable jobs | Path traversal, prompt injection, audit and rollback tests |
| 8 | Packaging and release gate | Clean Windows install, regression suite, privacy review |

Do not mark a stage complete based on unit tests alone. GitHub CI proves
repository-level behavior, not speaker audibility, GPU performance or a rigged
character moving on the user's laptop.

## Migration rule

Introduce coordinator/event interfaces behind feature flags. Preserve the
existing UI and storage APIs, test with synthetic nonpersonal fixtures, and
switch one adapter at a time. Avoid schema migration until a backup/restore
fixture is demonstrated. A failed feature must fall back to the working text
chat and static approved identity, with honest status labels.
