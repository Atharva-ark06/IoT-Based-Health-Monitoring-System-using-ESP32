import { readFile } from 'node:fs/promises';
import test from 'node:test';
import assert from 'node:assert/strict';
import vm from 'node:vm';

const dashboard = await readFile(new URL('../health/sensor_dashboard.html', import.meta.url), 'utf8');

test('dashboard does not embed the previous spreadsheet endpoint', () => {
  assert.match(dashboard, /meta\[name="sensor-data-url"\]/);
  assert.doesNotMatch(dashboard, /1vyV0RpBOaTAM0d76as9NuBuNelb2dreuvQ9dgwOCSTo/);
});

test('remote CSV sources must use HTTPS and omit credentials/referrer', () => {
  assert.match(dashboard, /parsedSource\.protocol !== 'https:'/);
  assert.match(dashboard, /credentials:\s*'omit'/);
  assert.match(dashboard, /referrerPolicy:\s*'no-referrer'/);
});

test('untrusted timestamp content is escaped before insertion into the table', () => {
  const match = dashboard.match(/function escapeHtml\(value\) \{[\s\S]*?\n        \}/);
  assert.ok(match, 'escapeHtml helper should exist');
  const escapeHtml = vm.runInNewContext(`(${match[0]})`);
  assert.equal(
    escapeHtml('<img src=x onerror="alert(1)"> & \'quoted\''),
    '&lt;img src=x onerror=&quot;alert(1)&quot;&gt; &amp; &#39;quoted&#39;'
  );
  assert.match(dashboard, /\$\{escapeHtml\(row\.timestamp\)\}/);
});

test('correlation uses temperature and BPM from the same complete rows', () => {
  assert.match(dashboard, /const pairedReadings = sensorData\.filter\(d => d\.temperature > 0 && d\.bpm > 0\)/);
  assert.match(dashboard, /calculateCorrelation\(pairedTemps, pairedBpms\)/);
  assert.match(dashboard, /generateClinicalInsights\(temps, bpms, pairedTemps, pairedBpms\)/);
  assert.match(dashboard, /const scatterData = pairedReadings\.map\(reading => \(\{/);
  assert.doesNotMatch(dashboard, /calculateCorrelation\(temps\.slice\(0, minLength\), bpms\.slice\(0, minLength\)\)/);
});

test('raw imported health readings are not logged to the browser console', () => {
  assert.doesNotMatch(dashboard, /console\.log\(['"]Processing data\.\.\.,\s*rawData/);
});
