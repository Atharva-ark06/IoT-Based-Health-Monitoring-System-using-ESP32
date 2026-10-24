# IoT-Based Health Monitoring System using ESP32

An academic IoT prototype for signed sensor ingestion, SQLite history, an authenticated dashboard, and ESP32 integration.

> **Current status:** the simulator → API → database → dashboard software path is testable. The ESP32 sketch compiles in CI, but the physical device and heart-rate sensor adapter are **not hardware-verified**. Synthetic readings are not patient measurements. This project is not a medical device or diagnostic service.

## Capabilities

- **Authenticated ingestion:** HMAC-SHA256 request signing, timestamp freshness, nonce replay prevention, strict schema/range checks, and a 16 KiB body limit.
- **Device key isolation:** optional per-device secret mapping via `IOT_DEVICE_SECRETS_JSON`; unknown device IDs fail closed when the map is configured.
- **Protected history:** separate bearer token for trusted API clients and a password/session-protected browser dashboard.
- **Browser protections:** HttpOnly/SameSite session cookie, same-origin checks, restrictive CSP, no-store responses, and text-only rendering.
- **Operational controls:** login/ingestion rate limits, `/healthz` and `/readyz`, metadata-only audit events, and a separately protected audit endpoint.
- **Resilience utilities:** simulator retries transient errors with bounded exponential backoff; SQLite maintenance supports dry-run retention and backup-before-delete.
- **Deployment hardening:** non-root Docker image, loopback-only Compose binding, read-only root filesystem, dropped capabilities, persistent SQLite volume, and container CI.
- **Firmware readiness:** ESP32 Arduino scaffold with NTP, CA-validated HTTPS, and HMAC signing; automated generic-target compile check.

## Architecture

```text
ESP32 firmware* ─┐
                 ├─ HMAC-signed JSON ─> FastAPI ─> SQLite
Synthetic client ┘                         │
                                           ├─ bearer-authenticated history API
Browser ─ password login ─ session cookie ┘
```

`health/sensor_dashboard.html` is the legacy standalone CSV dashboard. The integrated dashboard is served at `/dashboard` and reads the API database. Never put server tokens or device secrets in browser code.

## Quick start — Windows PowerShell

Requirements: Python 3.11+, Node.js 20+ for dashboard tests, and Git.

```powershell
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
cd IoT-Based-Health-Monitoring-System-using-ESP32
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

Create separate local development secrets in the same PowerShell session:

```powershell
$env:IOT_DEVICE_HMAC_SECRET = (python -c "import secrets; print(secrets.token_hex(32))")
$env:IOT_READ_API_TOKEN = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:IOT_DASHBOARD_PASSWORD = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:IOT_SESSION_SECRET = (python -c "import secrets; print(secrets.token_urlsafe(48))")
$env:IOT_DASHBOARD_ORIGIN = "http://127.0.0.1:8000"
$env:IOT_COOKIE_SECURE = "false"
$env:IOT_DATABASE_PATH = "data/readings.sqlite3"
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

`IOT_COOKIE_SECURE=false` is only for loopback-only HTTP development. Use HTTPS and secure cookies in deployment. Do not expose the development server directly to the internet.

Open [http://127.0.0.1:8000/dashboard](http://127.0.0.1:8000/dashboard), then sign in with the generated dashboard password.

In a second terminal, set the same `IOT_DEVICE_HMAC_SECRET` value and run the synthetic client:

```powershell
python -m simulator.device_simulator --count 5 --interval 1
```

The simulator uses synthetic example values only. Its bounded retry behavior does not guarantee exactly-once delivery if a response is lost after the server commits a reading.

## API endpoints

| Endpoint | Access | Purpose |
|---|---|---|
| `GET /healthz` | Public | Process health |
| `GET /readyz` | Public | Database readiness |
| `POST /api/v1/readings` | HMAC device signature | Validate and store a reading |
| `GET /api/v1/readings` | Bearer `IOT_READ_API_TOKEN` | Bounded history with device/time filters |
| `GET /dashboard` | Page public; data requires login | Integrated dashboard |
| `POST /api/v1/dashboard/login` | Password + same-origin Origin | Start browser session |
| `GET /api/v1/dashboard/readings` | HttpOnly session cookie | Recent dashboard history |
| `POST /api/v1/dashboard/logout` | Session + same-origin Origin | End browser session |
| `GET /api/v1/admin/audit` | Bearer `IOT_MAINTENANCE_TOKEN` | Read metadata-only audit events |

The device HMAC covers the exact request bytes: `unix_timestamp + "." + nonce + "." + raw_json_body`. Requests older than five minutes and reused nonces are rejected.

## Operations and maintenance

For multiple devices, prefer `IOT_DEVICE_SECRETS_JSON`, a secret-managed JSON map from device ID to a unique secret. When configured, only listed devices are accepted; the legacy shared secret is not used as a fallback. Removing a device from the map revokes it after configuration reload/restart. This prototype does not implement remote enrollment or overlapping-key rotation.

The in-process rate limiter defaults to 5 dashboard login attempts and 120 ingestion requests per client IP per 60 seconds. It is not distributed across workers; retain proxy-level rate limiting in deployment.

Preview retention first (no deletion):

```powershell
python -m backend.maintenance --database data/readings.sqlite3 --retention-days 90
```

Apply deletion only after creating a new backup:

```powershell
python -m backend.maintenance --database data/readings.sqlite3 --retention-days 90 --backup-path data/backups/pre-retention.sqlite3 --apply
```

The maintenance command refuses to overwrite an existing backup. Protect and encrypt database files/backups at the host or platform layer, and test restoration before relying on them.

See [Operations guide](docs/OPERATIONS.md) and [Deployment guide](docs/DEPLOYMENT.md) for details.

## Verification

```powershell
python -m pytest -q tests
node --test tests/*.test.mjs
python -m pip install bandit pip-audit
bandit -q -r backend -ll
pip-audit
```

GitHub Actions runs Python tests, dashboard regression tests, Bandit, pip-audit, a hardware-free ESP32 compile, and a Docker build/Compose configuration check. Always inspect the checks for the exact PR head SHA; passing CI is not production certification.

## Repository structure

```text
backend/
  app.py                  # API, authentication, rate limits and audit
  maintenance.py          # backup + dry-run/opt-in retention
firmware/esp32_health_monitor/
  esp32_health_monitor.ino
  secrets.example.h
health/
  api_dashboard.html      # session-protected API dashboard
  api_dashboard.js
  sensor_dashboard.html   # legacy HTTPS CSV dashboard
simulator/
  device_simulator.py     # signed synthetic readings + retry/backoff
tests/
  test_ingestion_api.py
  test_device_simulator.py
  test_dashboard_auth.py
  test_operational_resilience.py
  test_firmware_readiness.py
  test_deployment_config.py
  dashboard-security.test.mjs
  dashboard-integration.test.mjs
docs/
  ARCHITECTURE.md
  SETUP.md
  FIRMWARE.md
  INTEGRATION-TESTING.md
  DEPLOYMENT.md
  OPERATIONS.md
  SECURITY-VERIFICATION.md
  PROJECT-ANALYSIS.md
SECURITY.md
Dockerfile
compose.yaml
```

## Remaining verification

- [ ] Confirm the exact ESP32 board and heart-rate sensor model.
- [ ] Implement the correct BPM adapter; never upload fabricated heart-rate values.
- [ ] Provision a real CA certificate and device-specific secret securely.
- [ ] Verify physical sensor wiring, calibration, HTTPS, reconnects, and signed delivery on hardware.
- [ ] Configure and test an external HTTPS proxy, distributed rate limiting, secret manager, backup restore, monitoring, and retention policy before any real-data use.

HMAC authenticates requests; it does not encrypt traffic. Use HTTPS. SQLite is not encrypted at rest by this application. Use synthetic data for demos and tests, and do not use this prototype for diagnosis, emergency decisions, or treatment.
