# Human face mesh audit — 2026-11-06

## Source
Owner-supplied `VEGAS AI.zip`, entry `VEGAS AI/VEGAS AI/core/face_model.obj`. Inspected as text only; **no uploaded code executed**.

## Verified facts
- OBJ header attributes geometry to Google MediaPipe canonical face model; header cites Apache License 2.0 and MediaPipe Authors 2019–2023. This is a claim in the supplied file, not independent provenance verification.
- Exactly **468 vertex (`v`) lines** and **898 face (`f`) lines**.
- OBJ uses vertex positions and triangle indices, but **has no UV texture coordinates**; file comments explicitly say texture coordinates were dropped.
- A companion `core/avatar_mesh.py` describes generated cranium, neck, jaw, eyes and lip landmark rings.
- The file alone is **not** a photorealistic, fully rigged or textured female human avatar; do not present it as one.

## Decision
Keep this mesh as a candidate *geometry/animation research reference*, not the final avatar asset. To meet the owner's acceptance criterion, independently verify rights and acquire/build a textured, rigged female human with genuine eye and facial controls. Prototype speech animation on the actual rig, benchmark on Intel UHD graphics, and obtain owner approval of the visual appearance before dashboard integration.

## Security and compatibility
Never copy credentials from the reference ZIP into repository. Avoid executing reference code. Preserve working JARVIS and SQLite memory. Any third-party 3D model must have explicit redistribution rights and a performance budget for Windows 11 / 8 GB RAM / Intel UHD.

## Next concrete engineering step
Create a small isolated model-loading/animation harness with measurable head/eye/jaw transforms, then supply a legally usable **textured human model**. No static picture overlay, mouth-only animation or stylized replacement is acceptable as the final demonstration.
