import { readFile } from 'node:fs/promises';
import test from 'node:test';
import assert from 'node:assert/strict';

const html = await readFile(new URL('../health/api_dashboard.html', import.meta.url), 'utf8');
const script = await readFile(new URL('../health/api_dashboard.js', import.meta.url), 'utf8');

test('API dashboard uses a same-origin script and does not embed server tokens', () => {
  assert.match(html, /<script src="\/dashboard\.js" defer><\/script>/);
  assert.doesNotMatch(html + script, /IOT_READ_API_TOKEN|Authorization\s*:\s*['"]Bearer/);
  assert.match(script, /credentials:\s*"same-origin"/);
  assert.match(script, /cache:\s*"no-store"/);
});

test('untrusted readings are inserted as text rather than HTML', () => {
  assert.match(script, /cell\.textContent\s*=\s*value/);
  assert.match(script, /body\.replaceChildren\(\)/);
  assert.doesNotMatch(script, /innerHTML\s*=/);
});

test('dashboard explicitly labels synthetic data and medical limitations', () => {
  assert.match(html, /Synthetic simulator values/);
  assert.match(html, /not medical use/);
  assert.match(html, /HttpOnly session cookie/);
});
