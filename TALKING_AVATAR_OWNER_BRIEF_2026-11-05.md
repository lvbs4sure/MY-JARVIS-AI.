# Owner-selected talking JARVIS avatar — 2026-11-05

## Decision
The owner supplied a new preferred visual reference in the project conversation: a front-facing, youthful humanoid hologram with luminous cyan circuit lines, violet/blue skin tones, large expressive eyes, and a futuristic command centre. The owner wants **this identity direction** and a **genuinely talking** avatar, using their friend's KAVI as an interaction/layout reference, not as an asset to copy.

This reference is a raster image bearing a reelmind.ai watermark. **Do not copy or strip the watermark, distribute the reference as an owned asset, or claim that it is already an animatable 3D character.** Create an original, reviewed, rights-cleared character inspired by the general appearance. Do not upload the user-supplied reference to external generation/rigging services without separate consent.

## Non-destructive integration
- Preserve `static/jarvis-scene.png`, existing avatar options, and the live Streamlit dashboard.
- Do not replace the default avatar until the owner sees and accepts an identity-matched animated preview.
- Develop the new character in an isolated preview; retain the original scene as a selectable fallback.
- Preserve the existing `lip_sync.py` and `face_motion.py` audio-clock and rig-control contracts.

## Deliverable sequence and acceptance checks
1. **Original identity sheet:** front/three-quarter views and neutral, blink, open-mouth, closed-mouth expressions; confirm visual identity with owner. Keep all source and licenses documented.
2. **Lightweight face rig:** original 2D deformable layers or optimized VRM/glTF with independently controlled eyelids, gaze, jaw, and mouth shapes. A moving overlay or unrelated wireframe does not count.
3. **Actual speech playback:** locally installed voice preferred. Use audio and timestamped viseme cues from the same synthesis clip when available; otherwise label word-boundary motion as approximate. Do not claim phoneme-accurate synchronization from Web Speech API boundaries.
4. **Synchronization tests:** mouth opens only during active audible playback; pause, stop, interrupt, errors, seeking, and end-of-clip immediately return to neutral. Reduced-motion mode must be respected.
5. **Windows laptop gate:** benchmark on the owner's 8 GB RAM / Intel integrated graphics before enabling any 3D renderer by default; provide a low-resource fallback.
6. **Dashboard preview:** listening, thinking, speaking, paused, and error states; preserve memory privacy, no background microphone/camera access, and no unexpected cloud uploads.

## Current status
The repository already includes `animated_avatar.py`, `face_motion.py`, `lip_sync.py`, and `voice_output.py`, but the current wireframe speech activity is approximate and **does not animate the preferred humanoid image**. This document records the newly confirmed design target and verification gates, not a completed animation.

## Immediate next engineering task
Build an isolated, lightweight original face preview and its automated state-transition tests, then show the owner a real capture before changing the default dashboard. Prefer deterministic local assets and no new dependency unless strictly necessary.
