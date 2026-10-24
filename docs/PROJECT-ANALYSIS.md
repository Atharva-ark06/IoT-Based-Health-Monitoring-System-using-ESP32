# Project Analysis — Phases 6–10

## Project summary

The project is an educational IoT health-monitoring prototype with a FastAPI ingestion API, SQLite storage, a session-protected API dashboard, a synthetic device simulator, and an ESP32 firmware scaffold. The simulator → signed API → database → authenticated dashboard flow is covered by automated tests. Phase 6 adds an Arduino CLI compile workflow and static firmware-readiness tests. Phase 7 adds a non-root container image and hardened Compose template. Phases 8–10 add per-device HMAC key mapping, in-process rate limits, readiness checks, metadata-only audit events, an authenticated audit endpoint, bounded simulator retry/backoff, and backup-before-delete SQLite retention tooling. README and operations/security documentation are updated.

**Important boundary:** the ESP32 sketch is not hardware-verified. The heart-rate adapter intentionally remains unfinished until the exact sensor model and library are confirmed. Synthetic data verifies the software protocol path, not physical sensors or medical accuracy.

## Functional and security review

| Area | Current implementation | Remaining concern |
| --- | --- | --- |
| Simulator | HMAC-signed synthetic readings sent to the API | Synthetic values are not sensor readings; no physical device involved |
| Firmware | Wi-Fi, NTP, CA-validated HTTPS, HMAC request signing scaffold; automated generic ESP32 compile job and static readiness tests | Exact hardware, wiring, heart-rate algorithm, live certificate, and device upload need verification |
| Integrated dashboard | Same-origin page with password login, session-protected history, login rate limit, metadata-only audit events | Rate limit is per-process and IP-based; production identity provider and centralized monitoring remain external |
| Existing CSV dashboard | Static HTML/CSS/JavaScript with configured HTTPS CSV source | Separate from the API-backed dashboard; the source URL is public to its intended viewers |
| API write path | HMAC-SHA256, freshness window, replay nonce prevention, strict schema/ranges, streaming body-size cap, optional per-device key map | No remote enrollment, automated key rotation, or overlapping key rollout |
| API read paths | Separate bearer-token endpoint and session-protected browser endpoint | No roles or per-device read authorization |
| Database | SQLite, parameterized statements, indexes, bounded queries, audit events, backup and opt-in retention CLI | Not encrypted at rest; backup restore testing, migration, and multi-worker concurrency policy remain operational duties |
| Browser security | HttpOnly/SameSite cookie, same-origin checks, CSP, no bearer token in browser JS, text-only rendering | Browser-side data is visible to the authorized viewer; login rate limiting is not implemented here |
| Automation | Python and Node tests, Bandit, pip-audit, firmware compile job, container build/Compose validation | Green CI does not certify physical hardware or deployment safety |
| Operations | Health/readiness endpoints, per-device secret mapping, in-process rate limits, metadata audit, protected audit endpoint, backup-before-delete retention CLI, hardened container | HTTPS termination, distributed rate limiting, external monitoring, restore drills, managed secret rotation, encryption at rest, and deployment-specific validation remain required |

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
- **Prototype login:** local login throttling is process-local; no identity provider, user roles, or server-side session revocation list.
- **Device lifecycle:** per-device key mapping is supported, but provisioning, rotation/revocation workflow, and overlapping key rotation remain manual.
- **SQLite constraints:** backups, retention, filesystem permissions, and concurrency must be addressed for deployment.
- **No encryption-at-rest guarantee:** database/file-system encryption must be supplied separately.
- **Sensor limitations:** low-cost sensors and classroom calibration are not diagnostic-grade; thresholds and trends are informational only.

## Remaining work

1. **Physical integration (hardware-dependent):** confirm board and heart-rate sensor models, implement and validate the BPM adapter, provision a real CA certificate, flash the firmware, and verify signed HTTPS delivery on the device.
2. **Production operations:** configure a trusted HTTPS reverse proxy, distributed rate limiting, managed secrets, monitoring/alerts, encrypted storage/backups, and restore drills.
3. **Stronger device lifecycle:** build secure enrollment/provisioning workflows, managed rotation with overlap, and device-level authorization for history.
4. **Delivery guarantees:** add a versioned idempotency protocol before claiming exactly-once ingestion; implement and fault-test an ESP32 persistent offline queue after the hardware model is known.
5. **Analytics:** only after reliable sensor data is available, add transparent quality/anomaly flags without medical claims.

## Acceptance checklist

- [x] Simulator request signing matches the API protocol and is covered by integration tests.
- [x] Dashboard history requires a session; login/logout and Origin checks are tested.
- [x] Dashboard code does not embed the server bearer token and renders readings as text.
- [x] CI runs Python tests, Node tests, Bandit, and pip-audit.
- [x] Firmware source has a hardware-free compile workflow and static readiness checks.
- [x] Container image, hardened Compose template, deployment documentation, and container CI have been added.
- [x] Per-device key mapping, process-local rate limiting, readiness, audit metadata, simulator retry/backoff, and backup-before-delete retention tooling are implemented.
- [x] README and operations documentation describe the software controls and their limits.
- [ ] The latest pull-request head has a successful full CI run.
- [ ] Exact hardware/sensor models are confirmed and firmware is built on the target toolchain.
- [ ] Physical device sends a signed HTTPS reading that appears in the authenticated dashboard.
- [ ] Production controls are reviewed before any real health data is used.
