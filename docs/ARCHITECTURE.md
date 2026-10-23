# Architecture and How It Works

## System hierarchy

```text
Layer 1 — Sensing
  DHT11 temperature sensor + heart-rate sensor
                 │ sensor readings
                 ▼
Layer 2 — Edge device (planned integration)
  ESP32 firmware → validate readings → Wi-Fi
  Status: firmware source is not currently checked in.
                 │ HTTPS request + HMAC signature (planned on device)
                 ▼
Layer 3 — API / trust boundary
  FastAPI
  ├── POST /api/v1/readings  — signed device writes
  ├── GET  /api/v1/readings  — bearer-token-protected history
  └── GET  /healthz          — service health check
                 │ parameterized SQL
                 ▼
Layer 4 — Storage
  SQLite readings table + replay-protection nonce table
                 │ authorized query
                 ▼
Layer 5 — Presentation
  Existing static HTML dashboard (CSV-source workflow)
  Status: not wired to the authenticated API; never put its read token in browser code.
                 │
                 ▼
Layer 6 — Verification and operations
  GitHub Actions → pytest → Bandit → pip-audit → dashboard regression tests
```

The layers are intentionally separated. The authenticated API is a security-oriented backend building block; it is not yet an end-to-end deployed product. In particular, the repository does not contain the ESP32 firmware source, device-side HMAC signing, an API-backed dashboard session, or a production deployment configuration.

## Request lifecycle

1. A device payload contains `device_id`, a timezone-aware ISO-8601 `timestamp`, `temperature`, and `bpm`.
2. The API checks required authentication headers, the timestamp freshness window, nonce syntax, and the request-body size.
3. The server calculates HMAC-SHA256 over the exact raw body together with the timestamp and nonce, then compares signatures using a constant-time comparison.
4. The API validates the schema and allowed sensor ranges. Unknown fields and naive timestamps are rejected.
5. A SQLite transaction records the nonce and reading. A previously used nonce is rejected, preventing a signed request from being accepted twice within the nonce retention window.
6. An authorized reader can query the latest records, optionally filtering by device and time range. SQL values are parameterized and the limit is bounded.
7. CI runs automated regression tests and static/dependency checks when relevant files change.

## Trust boundaries

- **Sensors → ESP32:** sensor values can be noisy, disconnected, or spoofed. Software validation cannot prove clinical accuracy.
- **ESP32 → API:** HMAC provides request authenticity only when the secret remains confidential. Use HTTPS as well; HMAC is not encryption.
- **API → SQLite:** database files contain sensitive readings. Restrict filesystem permissions, backups, and retention.
- **API → dashboard/browser:** browser code is visible to visitors. Never embed `IOT_READ_API_TOKEN` or device secrets in HTML, JavaScript, or a public CSV URL.
- **GitHub CI:** workflows execute code from the branch under test. Permissions are read-only and no production secrets are needed for these tests.

## Current versus planned

| Capability | Status |
| --- | --- |
| Static CSV dashboard and browser regression tests | Present |
| HMAC-authenticated API ingestion | Present in the Phase 2 branch |
| Read-token-protected history endpoint | Present |
| Device/time-range history filters | Added in Phase 3 |
| Unified automated security verification | Added in Phase 3; must pass on the final commit |
| ESP32 firmware and device-side signing | Not present; integration blocked on source/hardware details |
| Secure dashboard login/session and API connection | Not present |
| HTTPS reverse proxy, rate limiting, encrypted storage, retention automation | Deployment work remains |

## Design principles

- Keep secrets on the device/server side; never ship read credentials to a static browser.
- Validate inputs at the API boundary, not only in the dashboard.
- Fail closed when authentication is not configured.
- Keep test data synthetic and avoid logging health payloads.
- Treat all dashboards and threshold indicators as educational/informational, not medical diagnosis.
