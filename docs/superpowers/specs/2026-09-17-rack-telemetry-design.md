# Rack Telemetry Example Design

## Scope

Show clearly labeled sample telemetry for all six battery racks in the existing TypeScript viewer. This demonstrates the final UI without pretending that live Modbus TCP is connected.

## Design

`src/telemetry.ts` owns the rack data contract and a deterministic sample provider. The contract contains rack number, temperature, voltage, SOC, and status. A later Modbus/WebSocket provider can return the same contract without changing the dashboard.

The existing viewer adds a right-side ESS diagnostic panel. Six compact rack cards remain visible while the 3D model is open, followed by LCS and eBSC controller cards. Clicking a rack keeps the full rack bank visible and highlights the selection; clicking LCS or eBSC moves to the controller. Persistent 3D labels identify RACK 01 through RACK 06, LCS, and eBSC. Temperatures at or above 35 degrees are warnings; the sample includes one warning so the state is visible.

The panel is marked `SIMULATION` and `Modbus TCP not connected`. No sample value is presented as live equipment data.

## Verification

Unit checks cover six racks, deterministic values, and warning classification. The existing model tests continue to cover geometry and door behavior. The production build must pass, and the browser must visibly show all six temperature values and update the selected rack.
