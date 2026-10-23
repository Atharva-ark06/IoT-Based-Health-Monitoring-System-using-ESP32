# IoT-Based Health Monitoring System using ESP32

An educational IoT health-monitoring prototype for collecting temperature and heart-rate readings, with a browser dashboard and an optional authenticated ingestion API.

> **Status:** the API and dashboard are independently testable, but this is not yet an end-to-end device system. The repository does not currently contain the ESP32 firmware, and the static dashboard is not connected to the authenticated API. This project is not a medical device or diagnostic tool.

## Contents

- [Project overview](#project-overview)
- [Architecture and hierarchy](#architecture-and-hierarchy)
- [Features](#features)
- [Technology stack](#technology-stack)
- [Repository layout](#repository-layout)
- [Quick start](#quick-start)
- [API security model](#api-security-model)
- [Run the verification suite](#run-the-verification-suite)
- [Documentation](#documentation)
- [Pros and limitations](#pros-and-limitations)
- [Roadmap](#roadmap)
- [Disclaimer](#disclaimer)

## Project overview

The intended system uses an ESP32 microcontroller with a temperature sensor (DHT11) and a heart-rate sensor. Readings are intended to be transmitted over Wi-Fi for viewing and historical analysis. The repository currently includes a static dashboard and a Python API prototype that can be developed and verified separately.

### Features currently present

- Static HTML/CSS/JavaScript dashboard with configurable HTTPS CSV input.
- FastAPI service for signed reading submissions.
- HMAC-SHA256 request authentication, timestamp freshness checks, and nonce replay prevention.
- Server-side payload validation, request-size limits, and parameterized SQLite operations.
- Separately authenticated reading history with device/time filters and a bounded result count.
- Dashboard regression tests and API security/regression tests.
- GitHub Actions verification with Bandit static analysis and pip-audit dependency checks.

### Not yet implemented or integrated

- Checked-in ESP32 firmware and device-side request signing.
- Secure per-device enrollment, key provisioning, rotation, and revocation.
- Connection from the static dashboard to authenticated API history.
- Production deployment controls such as TLS termination, rate limiting, encrypted storage, retention, monitoring, and managed backups.

## Architecture and hierarchy

```text
[Temperature + heart-rate sensors]
                |
                v
       [ESP32 firmware]       <- firmware source not currently checked in
                |
        Wi-Fi / HTTPS
                |
                v
 [FastAPI authenticated ingestion]
                |
                v
          [SQLite store]
                |
        authenticated API
                |
                v
 [Authorized application/dashboard] <- integration is future work

[Existing static dashboard] --> configured HTTPS CSV source
                                (separate path today)
```

**Trust boundaries:** sensors produce potentially noisy readings; the API validates and authenticates requests; the database stores readings; the dashboard must not receive server-only credentials. HMAC provides message authentication, not encryption. Use HTTPS or a private network for transport.

## Technology stack

| Layer | Technology |
| --- | --- |
| Edge hardware (planned) | ESP32, DHT11, heart-rate sensor |
| API | Python, FastAPI, Pydantic |
| Storage | SQLite |
| Dashboard | HTML, CSS, JavaScript |
| API tests | pytest, FastAPI TestClient |
| Dashboard tests | Node.js built-in test runner |
| Security automation | GitHub Actions, Bandit, pip-audit |

## Repository layout

```text
backend/
  app.py                         # ingestion and history API
  requirements.txt               # Python dependencies
health/
  sensor_dashboard.html          # static dashboard
tests/
  test_ingestion_api.py          # API/security regression tests
  dashboard-security.test.mjs    # dashboard regression tests
docs/
  ARCHITECTURE.md
  SETUP.md
  PROJECT-ANALYSIS.md
  SECURITY-VERIFICATION.md
.github/workflows/
  security-verification.yml      # consolidated CI/security checks
SECURITY.md                      # threat model and security guidance
README.md
```

Additional project reports or presentations may exist at the repository root.

## Quick start

### 1. Requirements

- Git
- Python 3.11 or newer
- Node.js 20 or newer (for dashboard tests)
- A modern browser

### 2. Clone and install (Windows PowerShell)

```powershell
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
cd IoT-Based-Health-Monitoring-System-using-ESP32

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

If PowerShell blocks virtual-environment activation, invoke ` .\.venv\Scripts\python.exe ` directly rather than weakening machine-wide execution policy.

### 3. Configure local secrets

Run in the same PowerShell session that will start the API. These generate separate random development secrets; never commit them or put them in the dashboard.

```powershell
$env:IOT_DEVICE_HMAC_SECRET = (python -c "import secrets; print(secrets.token_hex(32))")
$env:IOT_READ_API_TOKEN = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:IOT_DATABASE_PATH = "data/readings.sqlite3"

python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
$headers = @{ Authorization = "Bearer $env:IOT_READ_API_TOKEN" }
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/readings?limit=20" -Headers $headers
```

The health endpoint should return `{"status":"ok"}`. A new database returns an empty history. The write endpoint rejects unsigned requests; a production device signing client is not included yet. See the [full setup guide](docs/SETUP.md) for details and safe teardown.

### 4. Open the dashboard

Open `health/sensor_dashboard.html` in a browser or serve it from a static web server. Configure its `sensor-data-url` meta tag with an HTTPS CSV source intended to be visible to dashboard users:

```html
<meta name="sensor-data-url" content="https://example.com/readings.csv">
```

The URL is visible to visitors. Do not include credentials or a private spreadsheet URL. The current dashboard does not consume the authenticated API.

## API security model

| Endpoint | Authentication | Purpose |
| --- | --- | --- |
| `GET /healthz` | None | Minimal service health check |
| `POST /api/v1/readings` | HMAC-SHA256 device signature | Validate and store a reading |
| `GET /api/v1/readings` | Bearer token | Read bounded history; optional `device_id`, `start`, and `end` filters |

Device writes require `X-Device-Timestamp`, `X-Device-Nonce`, and `X-Device-Signature`. The signature covers the exact request body together with the timestamp and nonce. The API enforces a five-minute freshness window, rejects reused nonces, validates the schema and value ranges, and caps request size. Reading access uses the separate `IOT_READ_API_TOKEN`.

**Security boundary:** never embed `IOT_READ_API_TOKEN` in browser JavaScript, HTML, public CSV URLs, screenshots, or source control. HMAC does not encrypt traffic. Do not expose the development server directly to the internet; production use requires HTTPS, per-device credentials, rate limiting, access controls, encrypted storage/backups, retention rules, monitoring, and secret rotation. See [SECURITY.md](SECURITY.md).

## Run the verification suite

From the repository root with the Python virtual environment active:

```powershell
python -m pytest -q tests/test_ingestion_api.py
node --test tests/dashboard-security.test.mjs
```

The unified GitHub Actions workflow runs both suites plus Bandit and pip-audit. Check the workflow result for the exact commit or pull-request head you plan to merge; an earlier successful run does not prove a later commit passes.

## Documentation

- [Architecture and hierarchy](docs/ARCHITECTURE.md)
- [Setup guide](docs/SETUP.md)
- [Project analysis, pros and cons, and roadmap](docs/PROJECT-ANALYSIS.md)
- [Security verification checklist](docs/SECURITY-VERIFICATION.md)
- [Threat model and security guidance](SECURITY.md)

## Pros and limitations

**Pros**
- Separates dashboard, API, persistence, tests, and CI responsibilities.
- Demonstrates request authentication, replay prevention, input validation, parameterized SQL, and dependency scanning.
- Supports repeatable automated regression checks.
- Provides a clear foundation for learning IoT security and backend engineering.

**Limitations**
- No checked-in firmware means device-side signing and end-to-end operation cannot yet be verified.
- The dashboard and authenticated API are separate paths.
- SQLite is not encrypted at rest by the application.
- There is no device enrollment, per-device authorization, production rate limiting, or user/role management.
- Sensor accuracy and clinical suitability are not established.

## Roadmap

1. Add and review the actual ESP32 firmware and sensor configuration.
2. Implement device-side signing, TLS certificate validation, and secure per-device key provisioning.
3. Add an authenticated server-side dashboard integration without exposing private tokens.
4. Add deployment controls: rate limiting, encrypted storage/backups, retention/deletion, monitoring, and secret rotation.
5. Test the complete device → API → history → authorized dashboard flow using synthetic data.

## Disclaimer

This is an academic prototype for educational purposes. Readings are informational only and must not be used for diagnosis or as a substitute for professional medical equipment or advice.

---

Maintained by [Atharva Kulkarni](https://github.com/Atharva-ark06).
