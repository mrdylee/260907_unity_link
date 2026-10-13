# Touching Rack Pairs Implementation Plan

**Goal:** Widen R1/R2, R3/R4 and R5/R6 so each pair touches, retaining height, depth and the pair's existing outer edges.

**Architecture:** Change only the six rack parent X positions/scales in the Blender and GLB sources. Derive the local rack-frame width from the base mesh bounds; split the existing gap at its midpoint. Each rack grows inward by half the gap. Packs, BPU and frame follow their parent.

- [x] Preserve the pre-change GLB; add `scripts/touch-rack-pairs.py` and run on `Blender/ESS_Clear_Rack_Openings/ESS_Clear_Rack_Openings.blend`. Save `Blender/ESS_Touching_Racks/ESS_Touching_Racks.blend` and update the GLB.
- [x] Compare exported before/after geometry: three zero-width pair gaps, unchanged pair outer edges and unchanged height/depth. Run the existing build/model tests and inspect both rack views with doors open.
- [x] Update the latest-source pointers and dimensions note, refresh/validate the portable ZIP, and check the final diff. This follow-up remains local unless publication is requested again.
