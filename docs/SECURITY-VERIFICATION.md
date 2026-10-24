# Security Verification Guide

A green workflow means the listed automated checks completed; it is not a certification or proof that a deployment is secure.

## Automated checks

From the repository root:

~~~powershell
python -m pip install -r backend/requirements.txt
python -m pytest -q tests
node --test tests/*.test.mjs
python -m pip install bandit pip-audit
bandit -q -r backend -ll
pip-audit
~~~

GitHub Actions runs the Python API/session/integration tests, Node dashboard regression tests, Bandit, and pip-audit. Review the workflow for the exact pull-request head SHA.

## API/device tests

- Valid HMAC signature accepted and stored.
- Missing headers, invalid signatures, stale timestamps, replayed nonces, malformed payloads, extra fields, invalid ranges, naive timestamps, and oversized bodies rejected.
- Separate bearer-token access is required for the trusted-client history route.
- The hardware-free simulator generates the same signed request shape and is tested against the FastAPI TestClient.

## Dashboard tests

- History endpoint rejects requests without a valid session.
- Correct password sets an HttpOnly, SameSite=Strict cookie.
- Wrong password and mismatched Origin are rejected.
- Logout expires the browser cookie.
- Login fails closed if dashboard secrets are missing.
- Dashboard HTML includes a restrictive Content Security Policy and no-store headers.
- Browser code does not embed the server bearer token and inserts readings with textContent, not HTML parsing.

## Firmware checks still required

- Select the exact ESP32 board and heart-rate sensor model.
- Confirm pinout, sensor libraries, voltage requirements, and BPM calculation.
- Replace the placeholder CA certificate with the real trust chain for the API host.
- Provision a unique device secret without committing it.
- Build with the Arduino toolchain and run on hardware.
- Confirm HTTPS certificate validation, time synchronization, signed ingestion, reconnect behavior, and duplicate/replay rejection on the live device.

## Manual production review

- Confirm the API is behind HTTPS and the dev server is not exposed directly.
- Set IOT_COOKIE_SECURE=true and IOT_DASHBOARD_ORIGIN to the exact HTTPS origin.
- Use strong, unique values for IOT_DASHBOARD_PASSWORD, IOT_SESSION_SECRET, IOT_DEVICE_HMAC_SECRET, and IOT_READ_API_TOKEN.
- Add login rate limiting and security monitoring at the reverse proxy or application layer.
- Review storage access, encryption at rest, backups, retention, privacy, and authorized access before real personal data is used.
- Verify that no secrets or real sensor readings are present in Git history, logs, screenshots, or CI artifacts.
