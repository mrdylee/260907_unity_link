# Rack Telemetry Example Implementation Plan

> **For agentic workers:** REQUIRED EXECUTION SKILL: Use superpowers:executing-plans by default for continuous inline implementation. Use superpowers:subagent-driven-development only when the user explicitly requested subagents or parallel agent work. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a visible six-rack temperature, voltage, and SOC example to the TypeScript ESS viewer.

**Architecture:** Keep telemetry generation in `src/telemetry.ts` behind a small `TelemetryProvider` interface. Render cards in the existing viewer and connect card selection to the existing Three.js camera and door controls.

**Tech Stack:** TypeScript, Three.js, Vite, Node test runner.

---

### Task 1: Telemetry contract and sample data

**Files:**
- Create: `src/telemetry.ts`
- Create: `tests/telemetry.test.ts`

- [x] Define `RackTelemetry`, `TelemetryProvider`, and `SampleTelemetryProvider`.
- [x] Generate six deterministic rack records, including one temperature warning.
- [x] Test rack count, values, status classification, and sample source labeling.

### Task 2: Visible rack dashboard

**Files:**
- Modify: `src/main.ts`
- Modify: `src/style.css`

- [x] Add a panel explicitly labeled as simulation and disconnected from Modbus TCP.
- [x] Render six cards with temperature, voltage, SOC, and status.
- [x] Connect card selection to the rack camera view and card highlight.
- [x] Keep the panel readable on desktop and mobile layouts.
- [x] Label RACK 01 through RACK 06, LCS, and eBSC in 3D and add LCS/eBSC diagnostic cards.

### Task 3: Verification and handoff

**Files:**
- Modify: `README.md`
- Modify: `downloads/ESS-TypeScript-Portable.zip`

- [x] Run telemetry unit tests, existing 3D model tests, and the production build.
- [x] Reload the visible browser and verify all six temperatures and selection behavior.
- [x] Update the portable ZIP and README with the sample/live-data boundary.
- [ ] Commit and push the verified update to the existing repository.
