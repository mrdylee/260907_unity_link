# Purple Network Cable Curves Implementation Plan

**Goal:** Smooth the six purple IE3500 cables while preserving their ports, duct entry positions, color and thickness.

**Architecture:** Replace each three-cylinder path with one editable Blender Bezier curve. Keep short straight connector/duct leads and a tangent-continuous curved middle span. Append replacement GLB geometry through DetailGLB so existing PBR materials and unrelated equipment remain intact.

**Tech Stack:** Blender Python, DetailGLB, Three.js model verification.

- [x] Save the current GLB as `/private/tmp/ess-before-purple-curves.glb`. Add `scripts/purple-network-curves.py`, operating on the latest `Blender/ESS_LCS_Wiring/ESS_LCS_Wiring.blend` and matching GLB. Preserve exact endpoint positions from the original cylinders, use 65 mm straight port leads and 40 mm duct leads, and align the middle Bezier handles with those leads. Save `Blender/ESS_Network_Curves/ESS_Network_Curves.blend`.
- [x] Adapt the existing purple-cable checks in `tests/verify.mjs` from cylinder endpoints to exported curve vertices. Check the original six port assignments, connector parenting, original duct endpoints, one connected curve mesh per cable and retained purple material.
- [x] Run `npm run build && npm test`; inspect both existing viewer tabs from the Switch and internal-panel views. Check smooth bends, connector continuity and duct entry visually.
- [x] Update the source pointers/routing note in `AI_START_HERE.md` and `VIEWER_GUIDELINES.md`; refresh the portable ZIP, verify its CRC and model equality, and run `git diff --check`. Keep changes local.

The alternative of just smoothing cylinder shading leaves the sharp path corners unchanged; a continuous curve meets the visual request. No equipment movement or port reassignment is needed.
