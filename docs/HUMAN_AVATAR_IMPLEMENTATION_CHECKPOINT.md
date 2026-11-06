# JARVIS human-avatar implementation checkpoint — 2026-11-06

## Owner-approved target
A photorealistic-looking **female human digital avatar**, similar to the blue/cyan futuristic JARVIS concept the owner approved. The character must genuinely animate (eyes, eyelids, face, head and speech mouth shapes); a static image with a mouth overlay or a cartoon substitute is explicitly unacceptable.

## Current verified state
- The Streamlit/Chrome dashboard exists on branch `jarvis-new-foundation`. The interface simplification commit `72e3937` passed GitHub JARVIS checks.
- Existing talking-avatar HTML is a stylized preview, **not** a photorealistic digital human.
- Owner uploaded `VEGAS AI.zip` as technical reference. Inspection revealed `core/face_model.obj` (MediaPipe canonical face mesh, 468 vertices / 898 triangles, source comment states Apache-2.0) and `core/avatar_mesh.py` (NumPy mesh assembly with cranium, neck, lip and eye landmark rings and jaw rig). This is **measured facial geometry**, but not a textured, fully rigged photorealistic human.
- The archive also contains an API key configuration file. **Never import credentials, secrets, user data or entire archive into GitHub.** Respect licenses and attribution before reusing source.
- No working realistic avatar has yet been installed or tested on the owner's HP EliteBook 840 G7 (i5, 8 GB RAM, Intel UHD, Windows 11).

## Engineering path
1. Audit reference mesh/rig and licenses; do not execute untrusted uploaded code.
2. Select a redistributable **rigged and textured human** model with documented license and browser-friendly polycount. Verify actual mouth/eye blendshapes or bones. No substitution with 2D imagery.
3. Build an isolated local Chrome demo using WebGL/Three.js or equivalent, with visible continuous idle/head/blink movement, actual mesh deformation for jaw/lips, and opt-in browser TTS. Gracefully report WebGL/model loading failures.
4. Demonstrate and verify the *actual* moving human with the owner **before** integrating into the Streamlit dashboard. Describe limitations of speech lip-sync honestly.
5. Connect to existing JARVIS AI replies and optional microphone with explicit permission; keep credentials and local memory private.
6. Benchmark on 8 GB Intel UHD laptop, add quality fallback and preserve original JARVIS 6.2/7.0 and SQLite DB.

## Acceptance criteria
- Avatar is a genuine 3D human model (not static screenshot, CSS face or cartoon).
- Eyes blink; head and facial expression move; lip/jaw geometry changes during spoken output.
- Voice works with user interaction, without implying offline STT or perfect phoneme sync.
- Runs in Chrome on target laptop at usable frame rate; user confirms the appearance.
- No private keys committed; no destructive migration or forced paid services.

## Chat-limit continuity
If the chat ends, resume from this checkpoint and the repository branch. Do not claim the avatar is already complete. The owner wants initiative and concrete progress, with permission for destructive/costly actions only.
