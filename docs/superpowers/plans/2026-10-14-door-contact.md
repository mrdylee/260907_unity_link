# Rack Door Contact Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans inline; no delegation is needed.

**Goal:** Prevent Rack 2/3 and Rack 4/5 doors from passing through one another throughout opening and closing.

**Architecture:** Keep the Blender geometry and paired-door commands. Add kinematic collision constraints in TypeScript, using each visible mesh's oriented bounding box (including handles and vents) with a small clearance. Limit angular steps and resolve the first contact before applying a rotation. Closing holds an open neighbor at its current pose until an explicit opening request; closing and command reversals remain possible. This is visual contact simulation, not an engineering dynamics calculation.

**Tech Stack:** TypeScript, Three.js OBB, existing Node model test and local viewer.

Fixed angle stops would unnecessarily restrict a door whose neighbor is closed. A general rigid-body engine adds unnecessary mass, gravity and dependency configuration. Choose bounded mesh collision for the two requested adjacent boundaries; keep existing outer doors and cabinet doors unchanged.

- [x] Add independent mesh OBB assertions to tests/verify.mjs; reproduce interpenetration during setAll(true), not just its final angle.
- [x] Implement src/DoorContact.ts and integrate into ESSModel.update. Include reflected hinge scales, small angular substeps, contact bisection, no bounce, and requested targets retained while blocked.
- [x] Test simultaneous opening, either sequential order, closing, reversal, large time steps, vents open and container clone independence; retain existing rack/FACP checks.
- [x] Build, inspect the two browser tabs with open doors, update viewer/handoff docs and portable ZIP. Leave changes local until commit/push is requested.


## Follow-up — 2026-10-15 sequential opening

Reproduced: opening Rack 2 alone reaches approximately 59.8 degrees; requesting Rack 3 next leaves it at zero. Collision tests only verified non-penetration, so this unusable stopped state passed.

- [x] Add a failing behavioral assertion: both leaves must open after either sequential order, while retaining frame-by-frame separation.
- [x] Separate requested opening from effective target. When both neighbors request opening, sweep both poses together to find a shared safe opening, then let the existing collision-constrained motion retreat the first leaf and admit the second. Keep closed/one-door requests and paired-click behavior.
- [x] Verify both directions on 2/3 and 4/5, rapid reversals and direct paired clicks; build, inspect both tabs, refresh documentation/ZIP.

## Follow-up: closing must keep the neighbor still (2026-10-15)

Reproduced: closing Rack 2 restored Rack 3's full opening target, moving an unselected door.

- [x] Add failing per-frame tests for a stationary neighbor, both directions on 2/3 and 4/5, paired clicks, in-flight closing, unrelated commands and explicit reopening.
- [x] Change only the commanded door's target; closing holds an open neighbor at its current pose. Recalculate shared opening only for the commanded boundary when opening.
- [x] Run model regression tests and build.
- [x] Verify the visible click behavior and refresh the portable package. Rack 2 closes with its normal Rack 1 mate while Rack 3 and Rack 4 retain their poses.

## Follow-up: wider opening through aligned hinge axes (2026-10-15)

- [x] Reproduce the 25mm pivot/barrel mismatch and compare shared opening: 25.76 degrees before, 59.22 degrees with the pivot at the barrel center.
- [x] Add failing checks for all six barrel axes and both neighboring doors opening beyond 55 degrees.
- [x] Save aligned Blender and GLB transforms, assert closed child poses unchanged, retain all mesh collision checks. Build and regression tests pass.
- [x] Inspect the wider opening in both browser tabs and refresh the portable ZIP (36 matching entries).

The yellow squares are existing Door_Warning_Plate meshes using Caution_Amber, with no printed warning content. No appearance change was requested.
