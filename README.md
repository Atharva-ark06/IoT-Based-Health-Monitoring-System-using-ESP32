# IoT-Based Health Monitoring System using ESP32

An educational IoT prototype for collecting temperature and heart-rate readings, with an authenticated ingestion API, SQLite history, a session-protected browser dashboard, and a hardware-free device simulator.

> **Status:** the API → database → authenticated dashboard path can be exercised using synthetic simulator data. The firmware integration scaffold is checked in, but physical hardware has not been verified and the heart-rate sensor adapter is intentionally unfinished until the exact sensor model is known. This is not a medical device or diagnostic tool.

## What works now

- FastAPI accepts signed device readings using HMAC-SHA256.
- Requests have timestamp freshness checks, nonce replay prevention, payload validation, and a 16 KiB body limit.
- SQLite stores validated readings with parameterized queries.
- Reading history is protected by a separate bearer token for trusted clients.
- The new API dashboard (/dashboard) uses a password login and short-lived HttpOnly, SameSite=Strict session cookie; it does not embed the server read token in browser code.
- Dashboard requests are same-origin, login/logout enforce the configured Origin, and responses set restrictive security headers.
- A hardware-free simulator signs and posts synthetic readings using the same request format as the API.
- An ESP32 Arduino integration scaffold demonstrates HTTPS, CA certificate validation, NTP time synchronization, HMAC request signing, and secret separation.
- CI runs Python tests, dashboard regression tests, Bandit, pip-audit, a hardware-free ESP32 firmware compile job, and a container build/configuration check.

## Architecture

~~~text
Synthetic simulator ─┐
                     ├─ signed request ─> FastAPI ─> SQLite
ESP32 firmware* ─────┘                       │
                                             ├─ bearer-authenticated history API
Browser ─ dashboard password ─ session cookie┘
              *Firmware template is present; sensor adapter and physical validation remain.
~~~

The older health/sensor_dashboard.html is the standalone CSV dashboard. The integrated dashboard is /dashboard served by the API. Do not put server credentials in the older static dashboard or in public HTML.

## Quick start (Windows PowerShell)

Requirements: Python 3.11+, Node.js 20+ for tests, and Git.

~~~powershell
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
cd IoT-Based-Health-Monitoring-System-using-ESP32
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
~~~

Generate separate local development secrets in the same PowerShell session:

~~~powershell
$env:IOT_DEVICE_HMAC_SECRET = (python -c "import secrets; print(secrets.token_hex(32))")
$env:IOT_READ_API_TOKEN = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:IOT_DASHBOARD_PASSWORD = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:IOT_SESSION_SECRET = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:IOT_DASHBOARD_ORIGIN = "http://127.0.0.1:8000"
$env:IOT_COOKIE_SECURE = "false"
$env:IOT_DATABASE_PATH = "data/readings.sqlite3"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
~~~

IOT_COOKIE_SECURE=false is **for loopback-only local HTTP testing**. Use HTTPS and leave secure cookies enabled in a deployed environment. Do not expose the development server directly to the internet.

Open http://127.0.0.1:8000/dashboard and sign in with the generated dashboard password from the same terminal session.

In a second terminal, activate the environment and set IOT_DEVICE_HMAC_SECRET to the same generated device secret, then send synthetic readings:

~~~powershell
python -m simulator.device_simulator --count 5 --interval 1
~~~

The dashboard refreshes manually with the **Refresh** button. Simulator readings are synthetic and must never be represented as real patient measurements.

## API endpoints

| Endpoint | Authentication | Purpose |
| --- | --- | --- |
| GET /healthz | None | Minimal service health |
| POST /api/v1/readings | HMAC device signature | Validate and store a reading |
| GET /api/v1/readings | Authorization: Bearer IOT_READ_API_TOKEN | Trusted-client history with filters |
| GET /dashboard | Page is public; data requires login | Integrated browser UI |
| POST /api/v1/dashboard/login | Dashboard password + same-origin check | Create short-lived session |
| GET /api/v1/dashboard/readings | HttpOnly session cookie | Read recent dashboard history |
| POST /api/v1/dashboard/logout | HttpOnly session cookie + same-origin check | End browser session |

The device signature covers the exact request bytes: unix_timestamp + "." + nonce + "." + raw_json_body. The timestamp header must be within five minutes, and a nonce cannot be reused. Readings use timezone-aware ISO-8601 timestamps and validated ranges.

## Tests and security checks

~~~powershell
python -m pytest -q tests
node --test tests/*.test.mjs
python -m pip install bandit pip-audit
bandit -q -r backend -ll
pip-audit
~~~

GitHub Actions runs the same Python and Node test suites plus Bandit and pip-audit. Check the workflow associated with the exact commit/PR head.

## Repository layout

~~~text
backend/
  app.py
  requirements.txt
firmware/esp32_health_monitor/
  esp32_health_monitor.ino
  secrets.example.h
health/
  sensor_dashboard.html       # existing HTTPS CSV dashboard
  api_dashboard.html          # API-backed dashboard page
  api_dashboard.js            # session-cookie client; no bearer token
simulator/
  device_simulator.py         # synthetic signed readings
tests/
  test_ingestion_api.py
  test_device_simulator.py
  test_firmware_readiness.py
  test_dashboard_auth.py
  dashboard-security.test.mjs
  dashboard-integration.test.mjs
Dockerfile
compose.yaml
docs/
  DEPLOYMENT.md
  ARCHITECTURE.md
  SETUP.md
  FIRMWARE.md
  INTEGRATION-TESTING.md
  PROJECT-ANALYSIS.md
  SECURITY-VERIFICATION.md
SECURITY.md
~~~

## Hardware integration status

The firmware sketch defaults to a DHT11 temperature sensor on GPIO 4 as an example. The heart-rate adapter intentionally returns an invalid value until the actual sensor model and its library/sampling method are selected. Therefore the sketch will not upload fabricated BPM values. Review docs/FIRMWARE.md before connecting hardware. The CA certificate, Wi-Fi credentials, API URL, device ID, and device HMAC secret must be configured locally in an ignored secrets.h file.

## Documentation

- [Setup guide](docs/SETUP.md)
- [Architecture and data flow](docs/ARCHITECTURE.md)
- [Firmware integration and build readiness](docs/FIRMWARE.md)
- [Container deployment guide](docs/DEPLOYMENT.md)
- [End-to-end integration tests](docs/INTEGRATION-TESTING.md)
- [Security verification checklist](docs/SECURITY-VERIFICATION.md)
- [Threat model and reporting](SECURITY.md)
- [Project analysis and roadmap](docs/PROJECT-ANALYSIS.md)

## Limitations and safety

- This is an academic prototype, not a medical device, diagnostic service, or emergency alert system.
- Synthetic readings are for integration testing only.
- CI compiles the ESP32 sketch using placeholder configuration; physical sensor wiring, calibration, TLS certificate selection, and device-side behavior still require hardware-specific verification.
- HMAC authenticates requests; it does not encrypt traffic. Use HTTPS.
- The dashboard password/session mechanism is a prototype; add proxy-level rate limiting, monitoring, managed secret storage, backups, retention policies, and a production identity/access strategy before real deployment.
- SQLite data is not encrypted at rest by this application. Avoid using real personal health data until privacy and operational controls are reviewed.
