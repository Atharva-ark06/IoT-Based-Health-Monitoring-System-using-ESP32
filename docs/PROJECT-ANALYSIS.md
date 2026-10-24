# Project Analysis — Phase 6

## Project summary

The project is an educational IoT health-monitoring prototype with a FastAPI ingestion API, SQLite storage, a session-protected API dashboard, a synthetic device simulator, and an ESP32 firmware scaffold. The simulator → signed API → database → authenticated dashboard flow is covered by automated tests. Phase 6 adds an Arduino CLI compile workflow and static firmware-readiness tests, so firmware source changes can be checked without physical hardware.

**Important boundary:** the ESP32 sketch is not hardware-verified. The heart-rate adapter intentionally remains unfinished until the exact sensor model and library are confirmed. Synthetic data verifies the software protocol path, not physical sensors or medical accuracy.

## Functional and security review

| Area | Current implementation | Remaining concern |
| --- | --- | --- |
| Simulator | HMAC-signed synthetic readings sent to the API | Synthetic values are not sensor readings; no physical device involved |
| Firmware | Wi-Fi, NTP, CA-validated HTTPS, HMAC request signing scaffold; automated generic ESP32 compile job and static readiness tests | Exact hardware, wiring, heart-rate algorithm, live certificate, and device upload need verification |
| Integrated dashboard | Same-origin page with password login and session-protected history | Prototype login; rate limiting, production identity provider, monitoring, and stronger session lifecycle controls remain |
| Existing CSV dashboard | Static HTML/CSS/JavaScript with configured HTTPS CSV source | Separate from the API-backed dashboard; the source URL is public to its intended viewers |
| API write path | HMAC-SHA256, freshness window, replay nonce prevention, strict schema/ranges, streaming body-size cap | No device enrollment, per-device authorization, or automated key rotation |
| API read paths | Separate bearer-token endpoint and session-protected browser endpoint | No roles or per-device read authorization |
| Database | SQLite, parameterized statements, indexes, bounded queries | Not encrypted at rest; backup, retention, migration, and concurrency plan are limited |
| Browser security | HttpOnly/SameSite cookie, same-origin checks, CSP, no bearer token in browser JS, text-only rendering | Browser-side data is visible to the authorized viewer; login rate limiting is not implemented here |
| Automation | Python and Node tests, Bandit, pip-audit, firmware compile job | Green CI does not certify physical hardware or deployment safety |
| Operations | Health endpoint and environment-configured secrets | HTTPS termination, rate limiting, monitoring, backups, retention, and secret rotation still need deployment work |

## Pros

- **Layered architecture:** device client, API, storage, dashboard, tests, and documentation are separated.
- **Request integrity:** HMAC authentication, freshness checks, and nonce replay prevention protect the write path.
- **Bounded input handling:** schema validation and incremental request-size limits help resist malformed or oversized requests.
- **Safer browser boundary:** the browser uses a short-lived session cookie rather than receiving the server bearer token.
- **Reproducible demo:** a simulator lets contributors exercise the complete software path without physical hardware.
- **Repeatable verification:** CI checks API behavior, dashboard rendering, Python security patterns, and dependency vulnerabilities.

## Cons and trade-offs

- **Not production-ready:** real health data requires stronger privacy, availability, and operational controls.
- **Firmware is a scaffold:** the BPM adapter, board/sensor selection, and physical validation are incomplete.
- **Prototype login:** no login throttling, identity provider, user roles, or server-side session revocation list.
- **Shared device configuration:** device enrollment, unique provisioning, rotation, and revocation need a deliberate lifecycle.
- **SQLite constraints:** backups, retention, filesystem permissions, and concurrency must be addressed for deployment.
- **No encryption-at-rest guarantee:** database/file-system encryption must be supplied separately.
- **Sensor limitations:** low-cost sensors and classroom calibration are not diagnostic-grade; thresholds and trends are informational only.

## Recommended next phases

1. **Complete physical integration:** confirm board and sensor models, implement and validate the BPM adapter, flash the firmware, and verify CA-validated HTTPS on the device.
2. **Device lifecycle security:** enrollment, unique per-device credentials, rotation/revocation, and auditable device status.
3. **Operational controls:** rate limiting, audit events, monitoring, backup/restore tests, data retention/deletion, and deployment secrets.
4. **Resilience:** offline buffering, retry/backoff, idempotent delivery, clock drift handling, and fault-injection tests.
5. **Advanced analytics:** only after collecting reliable data, add transparent sensor-quality and anomaly flags without medical claims.

## Acceptance checklist

- [x] Simulator request signing matches the API protocol and is covered by integration tests.
- [x] Dashboard history requires a session; login/logout and Origin checks are tested.
- [x] Dashboard code does not embed the server bearer token and renders readings as text.
- [x] CI runs Python tests, Node tests, Bandit, and pip-audit.
- [x] Firmware source has a hardware-free compile workflow and static readiness checks.
- [ ] The latest pull-request head has a successful full CI run.
- [ ] Exact hardware/sensor models are confirmed and firmware is built on the target toolchain.
- [ ] Physical device sends a signed HTTPS reading that appears in the authenticated dashboard.
- [ ] Production controls are reviewed before any real health data is used.
