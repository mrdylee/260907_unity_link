import assert from 'node:assert/strict';
import { simulateContactor, contactorPlaybackFrame } from '../src/contactor.ts';

assert.equal(simulateContactor('normal', 0).feedback, 'CLOSED');
assert.equal(simulateContactor('normal', .29).diagnosis, 'pending');
assert.equal(simulateContactor('normal', .3).feedback, 'OPEN');
assert.equal(simulateContactor('normal', 2).diagnosis, 'normal');
assert.equal(simulateContactor('mismatch', 1).diagnosis, 'pending');
assert.equal(simulateContactor('mismatch', 1.01).diagnosis, 'mismatch');
assert.equal(simulateContactor('mismatch', 3).feedback, 'CLOSED');
for (const time of [0, .3, 1, 3]) {
  assert.equal(simulateContactor('offline', time).feedback, 'UNKNOWN');
  assert.equal(simulateContactor('offline', time).diagnosis, 'unknown');
}
assert.equal(simulateContactor('mismatch', 2).command, 'OPEN');
assert.deepEqual(contactorPlaybackFrame('mismatch', 0), { command: 'CLOSED', feedback: 'CLOSED', diagnosis: 'ready' });
assert.equal(contactorPlaybackFrame('mismatch', .6).command, 'OPEN');
assert.equal(contactorPlaybackFrame('mismatch', 1.6).diagnosis, 'pending');
assert.equal(contactorPlaybackFrame('mismatch', 1.7).diagnosis, 'mismatch');
assert.equal(contactorPlaybackFrame('normal', 1).feedback, 'OPEN');
assert.equal(contactorPlaybackFrame('offline', 1).feedback, 'UNKNOWN');
assert.equal(contactorPlaybackFrame('normal', 0).feedback, 'CLOSED');
console.log('PASS: contactor simulation, switching delay, mismatch boundary, and unknown feedback.');
