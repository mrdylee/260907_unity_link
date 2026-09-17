import assert from 'node:assert/strict';
import { formatRackLabel, SampleTelemetryProvider, telemetryStatus } from '../src/telemetry.ts';

const provider = new SampleTelemetryProvider();
const snapshot = await provider.read();
const equipment = await provider.readEquipment();

assert.equal(provider.source, 'simulation');
assert.equal(snapshot.length, 6);
assert.deepEqual(snapshot.map(rack => rack.rackId), [1, 2, 3, 4, 5, 6]);
assert.ok(snapshot.every(rack => rack.temperatureC > 20 && rack.temperatureC < 50));
assert.ok(snapshot.every(rack => rack.voltageV > 700));
assert.ok(snapshot.every(rack => rack.socPercent >= 0 && rack.socPercent <= 100));
assert.equal(telemetryStatus(34.9), 'normal');
assert.equal(telemetryStatus(35), 'warning');
assert.equal(formatRackLabel(1), 'RACK 01');
assert.equal(formatRackLabel(6), 'RACK 06');
assert.ok(snapshot.some(rack => rack.status === 'warning'));
assert.ok(snapshot.every(rack => rack.diagnosticCode.length > 0));
assert.ok(snapshot.every(rack => rack.diagnosticMessage.length > 0));
assert.deepEqual(
  snapshot.filter(rack => rack.status === 'warning').map(rack => rack.diagnosticCode),
  ['OVER_TEMPERATURE'],
);
assert.deepEqual(equipment.map(item => item.id), ['LCS', 'eBSC']);
assert.ok(equipment.every(item => item.communication === 'ONLINE'));
assert.ok(equipment.every(item => item.diagnosticMessage.length > 0));

console.log('PASS: six deterministic simulated rack telemetry records with warning classification.');
