# JARVIS identity-matched rig integration contract

This is the **implementation interface** for an eventual original, owner-reviewed
animated version of `static/jarvis-scene.png`. It does not create a rig or
alter the current holographic image. No cloud uploads are authorized.

## Required shape bindings

The `face_motion.rig_controls(FacePose)` adapter emits five bounded controls:

| Control | Range | Rig behavior |
|---|---|---|
| `blink_left` | 0–1 | Close the left eyelid, 1 = fully closed |
| `blink_right` | 0–1 | Close the right eyelid, 1 = fully closed |
| `gaze_horizontal` | -1–1 | Eye gaze left/right relative to neutral |
| `gaze_vertical` | -1–1 | Eye gaze down/up relative to neutral |
| `mouth_open` | 0–1 | Open speech mouth shape, 0 = neutral |

A real VRM/glTF implementation must map these portable names to the rig's
actual expression and bone channels. The character must have independently
controllable eyelids, gaze and mouth. Unsupported channels must be reported,
not silently presented as working.

## Frame update

1. Read the actual playback clock from the same clip that supplied viseme cues.
2. Sample `LipTimeline` with that position and current playing/interrupted state.
3. Sample `FaceMotionController` using a monotonic elapsed time and state.
4. Convert the resulting pose with `rig_controls` and apply it to a reviewed
   rig in an isolated preview. Never mutate the original background image.
5. On pause, stop, end, interrupted, lost playback or reduced motion, restore
   neutral mouth; do not continue timing from wall-clock guesses.

## Acceptance test

- Side-by-side owner review confirms the same recognizable face, hair, proportions
  and blue/violet holographic appearance.
- Real eyelid geometry/blendshape visibly blinks; eyes visibly track a subtle
  gaze target; neither is faked by moving a whole flat picture.
- Actual synthesized speech and same-run viseme cues drive the mouth.
- Stop/pause/seek/cancel tests show neutral mouth without stale frames.
- Browser/Windows tests verify audio audibility, GPU frame rate, RAM headroom,
  reduced-motion mode and original dashboard fallback.
- Do not activate this preview as the default until those checks pass.

**Status:** portable signal generation and mapping implemented; reviewed
identity-matched rig, playback renderer and Windows hardware tests pending.
