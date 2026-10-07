# Panel layout implementation plan
Goal: update four device positions in Blender and the web viewer.
Architecture: preserve baked GLB mesh payload; change node transforms and separate expansion children, matching Blender hierarchy.
Tech stack: Blender Python, glTF, TypeScript, Three.js.
- [x] Inspect equipment hierarchy and use existing expansion mesh.
- [x] Create scripts/panel-layout.py to move three left devices to inward-facing left wall and LCS to right wall. Save Blender/ESS_Panel_Layout/ESS_Panel_Layout.blend and update public/models/ess-container.glb.
- [x] Adjust eBSC camera to view its new inward-facing ports.
- [x] Build; run model tests with assertions on side, order and facing. Inspect browser panel and eBSC.
- [x] Update viewer guideline with new layout, report local result.
