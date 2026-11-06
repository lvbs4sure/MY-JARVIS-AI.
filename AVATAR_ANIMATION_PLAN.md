# Lifelike JARVIS animation — implementation contract

The approved photorealistic blue/violet JARVIS identity remains the live default.
The owner wants that same character to blink, speak with synchronized lips,
gesture and eventually walk. Do not substitute a wireframe face or claim a
static image is a rigged animated person.

## Owner-confirmed identity lock (2026-11-04)

The owner explicitly confirmed: **keep the exact same face and blue/violet
holographic appearance**, even if an animation-ready version must be developed
in stages. This is a design requirement, not approval to upload the artwork to
a third-party service or permission to replace the live character immediately.

- Source of visual identity: the existing approved `static/jarvis-scene.png`.
  Preserve that asset and the current live dashboard as the fallback.
- Any generated or rigged preview must match the face, hair, proportions,
  recognizable features, holographic color palette and lighting direction of
  the approved reference. Do not substitute a generic robot or wireframe.
- First validate a side-by-side neutral-pose identity comparison. Then add
  eyelid/blink and gaze controls, followed by facial expressions and
  audio-clock-driven speech shapes. Walking and body gestures come later.
- Only an actual eyelid/face rig or verified frame animation counts as facial
  movement. Moving CSS overlays, image translation, and a separate speech
  preview are **not** evidence that the character itself is animated.
- Keep preview assets isolated and opt-in. Before replacing the default,
  require owner review, real playback tests, reduced-motion behavior, and
  laptop RAM/GPU measurements. No cloud processing or new software
  installation is authorized by this identity confirmation alone.

## Required assets and capabilities

1. Identity-preserving full-body reference and facial expressions, reviewed by
   the owner before any change to the live character. No camera or personal
   photo is an input to this step. Cloud artwork processing needs consent.
2. An original or appropriately licensed rigged character with eyelid and mouth
   shapes, eyes and a full-body skeleton. A raster reference is not a 3D model.
   Proposed portable contract: VRM/glTF, with blink, gaze and speech shapes.
3. Actual speech audio plus mouth-shape timings from the same synthesis run.
   Windows System.Speech supports VisemeReached, including audio position and
   duration. Existing browser word boundaries are not phoneme-quality lip-sync.
4. Renderer clock samples the audio playback position; pause, stop, seek,
   interruption, browser visibility and reduced-motion state must be respected.
5. Body animation needs separate idle/gesture/walk clips and feet/contact tests.
   Do not slide the unchanged background picture and call it walking.

## Safe implementation order

- Current increment: pure validated audio-clock timeline, no rendering or engine.
- Next: benchmark an installed speech engine with a nonpersonal sentence and
  verify audio plus genuine viseme events; defer below the RAM safety gate.
- Isolated preview: connect genuine audio and timings to a reviewed character's
  eyelids/mouth without changing the live dashboard. Confirm audible/video sync.
- Then add natural eye/head motion and gestures, followed by full-body walking.
- Integrate only after identity review, Windows resource checks, interruption
  tests and confirmation that existing chat/memory/camera safeguards survive.

## Tested status, 2026-11-04

- lip_sync.py: pure audio-clock sampling validated with synthetic cues; pause,
  stop, silence and end-of-clip close the mouth; seeking does not accumulate
  timer drift; invalid timing data is rejected. This is infrastructure only.
- No renderer consumes this timeline yet. No claim of visible new lip-sync,
  walking, human-level expressiveness or emotion understanding.
- Laptop free RAM sampled at 0.83 GiB; no new renderer/model or speech inference
  benchmark started. Existing app and approved artwork remain unchanged.
- Permission requested for sending only the JARVIS artwork to the built-in image
  service to prepare concept references. Await approval before doing so. Never
  upload a camera frame or personal image under that permission.

## Acceptance gates

- Preserve character identity and compact console; preview does not auto-replace.
- Real audio drives the mouth; stopping audio immediately returns to neutral.
- Idle blinks do not imply camera activity, emotion detection or consciousness.
- Hardware governor and reduced-motion fallback; no forced heavy local model.
- Permission before installations, cloud uploads, purchases or camera access.
- Physical voice loop, camera understanding and live research retain their own
  independent incomplete gates; this animation work does not imply they work.

## Primary technical references

- Microsoft VisemeReached: https://learn.microsoft.com/en-us/dotnet/api/system.speech.synthesis.speechsynthesizer.visemereached
- Microsoft event offsets/duration: https://learn.microsoft.com/en-us/dotnet/api/system.speech.synthesis.visemereachedeventargs
- VRM humanoid/expression/gaze animation: https://vrm.dev/en/vrma/
