# Project Analysis — Phase 3

## Project summary

The project is an academic IoT health-monitoring prototype built around an ESP32, temperature and heart-rate sensors, a static browser dashboard, and a proposed secure API layer. The security phases are improving the repository from a dashboard-oriented demonstration toward a layered system with authenticated ingestion and controlled history access.

**Important boundary:** the checked-in firmware and the full device-to-dashboard integration are missing. The API and security controls can be tested in isolation, but this is not yet a verified end-to-end health-monitoring deployment.

## Functional and security review

| Area | Current implementation | Remaining concern |
| --- | --- | --- |
| Sensor/edge layer | Hardware design described in project material | Firmware source, calibration, secure Wi-Fi setup, and device-side HMAC are unavailable |
| Dashboard | Static HTML/CSS/JavaScript; configured HTTPS CSV source | Does not consume authenticated API history; CSV source must be deliberately public to its audience |
| API write path | HMAC-SHA256, freshness window, nonce replay prevention, strict schema/ranges, body-size cap | Shared secret model; no enrollment or per-device authorization |
| API read path | Separate bearer token; bounded result limit; optional device/time filters | One service-level token, no user accounts/roles or device-specific authorization |
| Database | SQLite, parameterized statements, timestamp/device indexes | Not encrypted at rest; backup, retention, migration, and concurrency plan are limited |
| Browser security | Avoids hard-coded source URL; protects imported values; regression tests | Third-party CDN dependencies and browser-side data remain visible to dashboard users |
| Automation | GitHub Actions tests; Phase 3 adds Bandit and pip-audit | A clean scan cannot prove deployment safety; results must be checked on the exact head commit |
| Operations | Health endpoint and environment-based secrets | No production TLS termination, rate limiting, monitoring, alerting, or secret rotation process |

## Pros

- **Clear separation of concerns:** dashboard, API, storage, tests, and workflows are distinct.
- **Better write integrity:** signed requests help prevent unauthorized payload changes and replayed requests.
- **Input validation at the server:** the API rejects unexpected fields, invalid ranges, stale signatures, and oversized bodies.
- **Reduced accidental exposure:** the dashboard does not need a private API read token.
- **Repeatable verification:** automated tests and static/dependency checks can catch regressions before merge.
- **Useful learning value:** the code illustrates API authentication, threat modeling, parameterized SQL, test automation, and security boundaries.

## Cons and trade-offs

- **Not production-ready:** health data needs stronger privacy, availability, and operational controls than this educational prototype currently supplies.
- **Shared secret limitations:** one shared device secret is hard to revoke per device; secure provisioning and storage on the ESP32 are not implemented.
- **No end-to-end integration:** the API and dashboard are separate flows until the firmware and a safe dashboard access model are added.
- **SQLite constraints:** simple for a local demo, but requires deliberate backup, permissions, retention, and concurrency decisions for deployment.
- **No encrypted-at-rest guarantee:** file-system or database encryption must be supplied separately.
- **Static dashboard visibility:** anything in client-side HTML/JavaScript is public to viewers; private readings cannot safely be protected by hiding a URL.
- **Sensor limitations:** low-cost sensors and classroom calibration are not diagnostic-grade; threshold alerts can be inaccurate.

## Recommended implementation order

1. **Close Phase 3 verification:** confirm tests, Bandit, pip-audit, and dashboard tests pass on the latest commit.
2. **Restore/confirm the firmware source:** identify exact sensor models, pins, libraries, sampling rate, and current transmission protocol.
3. **Implement device-side signing:** use a vetted HMAC implementation, unique device identity, secure provisioning, a nonce source, and TLS certificate validation.
4. **Create a private dashboard access pattern:** use a server-side session or authenticated backend-for-frontend; never place the read token in browser code.
5. **Harden deployment:** HTTPS, rate limiting, encrypted storage/backups, retention/deletion policy, monitoring, and secret rotation.
6. **Validate with synthetic end-to-end tests:** device simulator → API → history query → authorized dashboard; verify that unauthenticated reads fail.
7. **Review privacy and medical claims:** minimize stored identifiers, document consent/access rules, and label readings as informational rather than diagnostic.

## Acceptance checklist

- [ ] All tests pass on the final pull-request head.
- [ ] Bandit and pip-audit finish successfully with findings reviewed.
- [ ] Read endpoint returns 401 without a valid token.
- [ ] Invalid signatures, stale timestamps, replayed nonces, malformed payloads, and out-of-range values are rejected.
- [ ] Device/time filters return only matching readings.
- [ ] No real health data, credentials, tokens, or Wi-Fi passwords are committed.
- [ ] Dashboard never contains a private bearer token.
- [ ] Missing firmware and deployment controls remain explicitly documented.
