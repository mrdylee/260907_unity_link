# eBSC LAN Cable Curves Implementation Plan

**Goal:** Round the two white eBSC LAN cables while retaining the yellow connectors, existing switch ports and the finished purple/LCS wiring.

**Architecture:** Replace each cable's three cylinders with one tangent-continuous Bezier curve. Keep 55 mm straight leads at both connector ends; use 100 mm curve handles extending into the open compartment and a middle knot sagging by 18% of the port span. Reuse each cable's current radius and material, preserving its group and endpoint metadata.

**Tech Stack:** Blender Python, existing DetailGLB writer and model verification.

- [x] Back up the current GLB, add `scripts/ebsc-lan-curves.py`, and run it on `Blender/ESS_Network_Curves/ESS_Network_Curves.blend`. Save the complete updated source to `Blender/ESS_LAN_Curves/ESS_LAN_Curves.blend` and update the web GLB.
- [x] Adapt the existing eBSC cable checks to inspect actual curved mesh vertices at both original port centers. Run `npm run build && npm test`, then refresh both viewer tabs and visually confirm smooth bends and connector continuity.
- [x] Update source pointers and the routing note in the handoff/guidelines, refresh and validate the portable ZIP, run `git diff --check`, and leave the result local.
