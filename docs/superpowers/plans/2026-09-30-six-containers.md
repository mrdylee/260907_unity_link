# Six containers and paired doors Implementation Plan

Goal: Display six identical ESS containers and replace six same-direction rack doors with three outward-opening pairs.

Architecture: Edit a copy of the Blender source, preserve geometry world positions while moving the even-numbered door hinges to their outer edge, and export the corresponding transformations into the existing textured GLB. Clone the loaded model with shared geometry/materials into a 3-column, 2-row site. Selecting a container provides its existing diagnostic UI and close-up controls.

Alternatives: Six independent downloads waste GPU memory; six embedded viewers fragment navigation. A shared scene with six model instances preserves the existing controls and materials.

Tech stack: Blender Python, Three.js, TypeScript, Vite.

- [x] Inspect Blender hinges and matching GLB nodes; save edited source as a new blend file, preserving original.
- [x] Write regression checks for opposite opening directions, outer-edge pivots, three synchronized pairs and independent container states.
- [x] Implement paired door targets and clone support in src/ESSModel.ts.
- [x] Add six site instances, container selector and overview camera in src/main.ts. Retain scoped rack/LCS/eBSC diagnostics for the selected container.
- [x] Build and run model regression tests. Open the result, verify six instances and close-up paired doors visually, and leave it visible.

Success: Six containers visible in overview; each has 6 racks/42 packs; pairs 1–2, 3–4, 5–6 open in opposite directions from outer hinges without moving closed geometry; another container remains unchanged on individual door click. All diagnostic values remain explicitly simulated.
