# Security Notes

This repository is an educational IoT health-monitoring prototype, not a production medical system.

## Data classification

Temperature and heart-rate readings can be sensitive personal data.

- Use synthetic readings for demos, screenshots, tests, and public examples.
- Do not publish spreadsheets containing real readings or personal identifiers.
- A spreadsheet ID or URL is not authentication. Anyone with access to a public export can retrieve its data.
- Use only an HTTPS CSV source intentionally accessible to its audience.
- Never commit Wi-Fi passwords, API keys, bearer tokens, device secrets, or private credentials.

## Current protections

| Area | Control | Limit |
| --- | --- | --- |
| Dashboard source | Configured HTTPS CSV source; no embedded private token | The configured URL is public to dashboard visitors |
| Dashboard rendering | Imported timestamps are escaped; regression tests cover key behaviors | Browser code and data displayed to users are not private from those users |
| Device ingestion API | HMAC-SHA256 signature over timestamp, nonce, and exact request body; five-minute freshness window; replay nonce detection | Device-side signing, provisioning, and per-device keys are not implemented in the repository |
| Payload validation | Strict schema, allowed fields/ranges, timezone-aware timestamps, request body limit | Valid-looking readings can still be inaccurate or spoofed at the sensor |
| Reading retrieval | Separate bearer token; bounded limit; optional device and time filters | No user accounts, roles, or per-device read authorization |
| Database | SQLite parameterized statements and indexes | No application-level encryption at rest, retention automation, or managed backup plan |
| CI | API tests, dashboard regression tests, Bandit, and pip-audit workflow | Passing checks do not certify the full system or its deployment |

## API security boundary

The optional API in `backend/app.py` is a backend building block. Device writes require `X-Device-Timestamp`, `X-Device-Nonce`, and `X-Device-Signature`; the signature is HMAC-SHA256 over the timestamp, nonce, and exact raw body. Reading retrieval requires a separate `IOT_READ_API_TOKEN`.

HMAC authenticates a request but does **not** encrypt it. Use HTTPS or a private network. Do not expose the development server directly to the internet. Never embed the read token in the static dashboard or a public CSV URL. Store secrets using environment configuration for local work and a secret manager for deployment.

## Before real-data use

1. Add and review firmware source, device-side signing, secure key provisioning, and TLS certificate validation.
2. Use unique device credentials and define rotation/revocation.
3. Put the API behind HTTPS, rate limiting, and monitoring.
4. Define access control, retention/deletion, encrypted storage and backups, and incident response.
5. Use an authenticated server-side dashboard integration; never expose a private bearer token to browser JavaScript.
6. Test the complete device → API → history → authorized dashboard flow with synthetic data.
7. Verify data permissions in a signed-out browser and remove personal identifiers unless genuinely required.
8. Treat dashboard indicators as informational only, not medical diagnosis or a substitute for professional equipment/advice.

The checked-in repository currently has no ESP32 `.ino` firmware source. Pin assignments, device signing, sensor calibration, and end-to-end behavior therefore cannot yet be verified from this repository.

## Reporting a vulnerability

Please report issues privately to the repository owner through a channel listed on their GitHub profile. Do not publish private health data, credentials, or exploitable details in a public issue.
