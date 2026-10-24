# Setup Guide

This guide runs the authenticated API, API-backed dashboard, and synthetic device simulator locally. It also documents the current limits of the ESP32 firmware scaffold. No physical hardware test is implied.

## Requirements

- Git
- Python 3.11 or newer
- Node.js 20+ for dashboard regression tests
- A modern browser

## 1. Clone and prepare Python

Windows PowerShell:

~~~powershell
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
cd IoT-Based-Health-Monitoring-System-using-ESP32
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
~~~

If PowerShell blocks activation, invoke the venv interpreter directly with .\.venv\Scripts\python.exe instead of weakening machine-wide execution policy.

## 2. Configure local development secrets

Generate separate values in the same PowerShell session that will run the API. Do not commit or paste these into HTML, source code, screenshots, or issue reports.

~~~powershell
$env:IOT_DEVICE_HMAC_SECRET = (python -c "import secrets; print(secrets.token_hex(32))")
$env:IOT_READ_API_TOKEN = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:IOT_DASHBOARD_PASSWORD = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:IOT_SESSION_SECRET = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:IOT_DASHBOARD_ORIGIN = "http://127.0.0.1:8000"
$env:IOT_COOKIE_SECURE = "false"
$env:IOT_DATABASE_PATH = "data/readings.sqlite3"
~~~

IOT_COOKIE_SECURE=false is allowed only for loopback-only local HTTP testing. A deployed HTTPS environment must use secure cookies, an HTTPS origin, and secrets stored in the deployment platform's secret manager.

Start the API:

~~~powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
~~~

In a second terminal, verify the health endpoint:

~~~powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
~~~

Expected response: {"status":"ok"}.

## 3. Exercise the signed ingestion path

In the second terminal, activate the venv and set IOT_DEVICE_HMAC_SECRET to the exact same device secret generated in step 2. If you generated a new value in the second terminal, the API will reject the signature.

~~~powershell
$env:IOT_DEVICE_HMAC_SECRET = "paste-the-same-local-device-secret-here"
python -m simulator.device_simulator --count 5 --interval 1
~~~

The simulator sends synthetic temperature/BPM values to the loopback API. It uses the same timestamp, nonce, and raw-body HMAC scheme expected from a device. It refuses non-HTTPS URLs except for localhost/loopback development.

## 4. View readings in the integrated dashboard

Open http://127.0.0.1:8000/dashboard. Enter the IOT_DASHBOARD_PASSWORD value generated in step 2. The browser receives a short-lived HttpOnly, SameSite=Strict session cookie. It never receives the server-side IOT_READ_API_TOKEN.

The dashboard reads recent history through /api/v1/dashboard/readings and can be refreshed manually. The separate /api/v1/readings endpoint remains available to trusted non-browser clients with the bearer token.

## 5. API authentication model

- POST /api/v1/readings requires X-Device-Timestamp, X-Device-Nonce, and X-Device-Signature.
- The HMAC-SHA256 signature covers exact bytes: unix_timestamp + "." + nonce + "." + raw_json_body.
- Requests outside the five-minute time window, repeated nonces, invalid payloads, and oversized bodies are rejected.
- GET /api/v1/readings uses the separate IOT_READ_API_TOKEN.
- Dashboard login uses IOT_DASHBOARD_PASSWORD and signs a short-lived cookie with IOT_SESSION_SECRET.
- Dashboard login/logout require the Origin header to match IOT_DASHBOARD_ORIGIN.
- Set IOT_COOKIE_SECURE=true behind HTTPS. Do not expose the development server directly to the internet.

## 6. Operations and maintenance

For per-device HMAC keys, rate limits, readiness, audit events, and backup-before-delete retention, see [OPERATIONS.md](OPERATIONS.md). The simulator retries transient responses with bounded backoff, but the prototype does not guarantee exactly-once delivery.

## 7. Run automated checks

~~~powershell
python -m pytest -q tests
node --test tests/*.test.mjs
python -m pip install bandit pip-audit
bandit -q -r backend -ll
pip-audit
~~~

GitHub Actions runs the Python tests, Node dashboard tests, Bandit, and pip-audit on pushes and pull requests. Check the run attached to the exact commit SHA.

## 8. Firmware status

The checked-in sketch demonstrates Wi-Fi, NTP, certificate-validated HTTPS, and HMAC signing. It includes a DHT11 example on GPIO 4, but the heart-rate adapter deliberately returns an invalid sample until the actual sensor model and library are confirmed. As a result, it will not submit invented BPM values. See FIRMWARE.md for the setup and remaining hardware-specific work.

## Container deployment

For the non-root container image, persistent SQLite volume, required environment variables, loopback-only port binding, and deployment limitations, follow [DEPLOYMENT.md](DEPLOYMENT.md). The container template is intended to sit behind a separately managed HTTPS reverse proxy for remote access.

## Teardown

Stop the API with Ctrl+C. Close the terminals containing environment variables when finished. Remove the local data directory if you want to discard synthetic test readings. Rotate any secret that was copied to a public location.
