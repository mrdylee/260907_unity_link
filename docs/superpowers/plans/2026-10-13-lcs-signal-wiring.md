# LCS Signal Wiring Implementation Plan

**Goal:** Connect the top and bottom LCS terminal banks to the upper and lower central-panel wiring ducts with smooth visible wires.

**Architecture:** Extend the saved LCS-detail Blender/GLB pair with four red/black multi-spline curves and two merged ferrule curves. Keep the existing LCS placement, bottom Ethernet, power leads, other equipment and materials. This is a visual signal harness; HW/RS-485 pin assignments are not supplied.

**Tech Stack:** Blender Python curves, existing DetailGLB writer, TypeScript/Three.js viewer and Node model tests.

## Design

- Follow the eight existing terminal banks: top 12+12+8+8 holes, bottom 8+12+8+8 holes. These are model geometry counts, not a verified electrical pinout.
- Alternating red and black wires start inside each modeled terminal opening. Short ferrules show where they enter the terminal. Top wires leave upward; bottom wires leave downward, keeping the faceplate clear.
- In central-panel coordinates the top bundle enters the highest horizontal duct (Y=1.29); the bottom bundle enters the lower main duct (Y=0.51), which also receives the existing downward LCS Ethernet route. Endpoints sit inside the duct volume.
- Use editable Bezier splines with rounded tubing and merge each row into two web meshes, one per color. Reuse the existing red, black and metal materials.

## Execution

- [x] Add geometry checks in `tests/verify.mjs`: all eight banks connected, source points in the modeled openings, exported mesh vertices at both endpoints, top/lower routes terminate inside the matching ducts. Run `npm test` and confirm the missing-harness assertion fails.
- [x] Add `scripts/lcs-signal-wiring.py`, run once on `Blender/ESS_LCS_Detail/ESS_LCS_Detail.blend` and matching GLB; save `Blender/ESS_LCS_Wiring/ESS_LCS_Wiring.blend` plus updated `public/models/ess-container.glb`. Preserve the pre-wiring GLB in `/private/tmp` for reversible iteration.
- [x] Run `npm run build && npm test`; inspect the LCS and whole panel in both existing localhost viewer tabs. Correct any float, kink, faceplate occlusion or duct miss found in the rendered model.
- [x] Update AI_START_HERE.md and VIEWER_GUIDELINES.md with the new source and visual-only routing, refresh the existing portable ZIP, check its CRC and matching public/dist models, and run `git diff --check`. Do not commit or push without a new request.
