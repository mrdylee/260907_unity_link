# LINK Four Plus Two Layout Implementation Plan

> **For agentic workers:** REQUIRED EXECUTION SKILL: Use superpowers:executing-plans for continuous inline implementation.

**Goal:** Place LINK 1–4 in a 2×2 group and LINK 5–6 in a separate pair, with 0.1524m gaps and outward E-panels.

**Architecture:** Derive placements from closed GLB bounding boxes. Rotate even containers by pi and translate their bounds so the inner X edges are at ±0.0762m. Use row centers `[-depth-3, -1, depth+3]` for 2m within-group and 4m between-group passage. Transform detail camera vectors with the selected root.

**Tech Stack:** TypeScript, Three.js, existing Node model checks and browser viewer.

---

## 1. Placement and regression checks

Create `src/ContainerLayout.ts` exporting `arrangeContainers(roots: THREE.Object3D[]): THREE.Box3`. Add real-model checks in `tests/verify.mjs`: three gaps equal 0.1524m, row alignment, 2m/4m passage, even roots rotated pi, E-panel nodes on outer ends and no container AABB intersections during all-door animation. Run `npm test` to establish failure, implement the placement function, rerun to pass.

## 2. Viewer integration

Modify only relevant paths in `src/main.ts`: load-time placement, overview camera fitting, local-to-world preset views and rotated camera offsets in rack/device focus. Add two floor outlines and group labels to the existing overview marker layer. Hide grouping in detail mode. Preserve IDs, diagnostics, selection behavior and prior door constraints. Update only group marker styles in `src/style.css`.

## 3. Verification and delivery

Run `npm run build` and `npm test`; inspect overview and even-container rack/panel focus through the current browser. Update `AI_START_HERE.md` and `VIEWER_GUIDELINES.md` with exact gap and provisional aisle widths. Refresh portable ZIP, compare every entry to working sources and build, run `git diff --check`. Remove the temporary layout-inspection script. Keep work local; no commit or push requested.

## Verified result

2026-10-22: `npm test` passes real-model gaps, outward E-panel direction, row/group passages and all-door animation separation, plus the previous door and telemetry regressions. `npm run build` passes with the existing nonfatal chunk-size advisory. Browser checks confirm overview grouping, ESS 02 data, rotated Rack 03 focus, E-panel interior and eBSC detail. Portable ZIP entries match current files. No commit or push.
