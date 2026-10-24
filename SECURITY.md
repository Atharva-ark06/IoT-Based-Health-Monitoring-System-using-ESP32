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
| Existing CSV dashboard | Configured HTTPS CSV source; no embedded private token | The configured URL is public to dashboard visitors |
| Dashboard rendering | Incoming readings are rendered as text; regression tests cover key behaviors | Data displayed to a user is visible to that user |
| Device ingestion API | HMAC-SHA256 signature over timestamp, nonce, and exact request body; five-minute freshness window; replay nonce detection | per-device key mapping is supported through `IOT_DEVICE_SECRETS_JSON`, but remote enrollment and automatic rotation are not implemented |
| Firmware scaffold | HTTPS CA validation, time sync, HMAC signing, local secrets template | Heart-rate sensor adapter is unfinished; no physical hardware verification is claimed |
| Payload validation | Strict schema, allowed fields/ranges, timezone-aware timestamps, request body limit | Valid-looking readings can still be inaccurate or spoofed at the sensor |
| Trusted-client history | Separate bearer token; bounded limit; optional device/time filters | No user accounts, roles, or per-device read authorization on this endpoint |
| API dashboard | Password login, short-lived signed HttpOnly/SameSite cookie, same-origin checks for login/logout, restrictive CSP | Prototype sessions; in-process rate limiting is not distributed, and production identity management and monitoring remain external |
| Database | SQLite parameterized statements and indexes | No application-level encryption at rest; backup/retention utilities require operator policy and host-level protection |
| CI | Python tests, Node dashboard regression tests, Bandit, and pip-audit | Passing checks do not certify the full system or its deployment |

## API security boundary

Device writes require X-Device-Timestamp, X-Device-Nonce, and X-Device-Signature; the signature is HMAC-SHA256 over the timestamp, nonce, and exact raw body. Trusted-client reading retrieval requires the separate IOT_READ_API_TOKEN. When `IOT_DEVICE_SECRETS_JSON` is configured, the API resolves a unique HMAC secret by `device_id` and rejects IDs absent from the map.

The integrated browser dashboard uses IOT_DASHBOARD_PASSWORD and IOT_SESSION_SECRET to create a short-lived signed session cookie. The server-side read token is never embedded in browser JavaScript. Set IOT_DASHBOARD_ORIGIN to the exact origin serving the dashboard and keep IOT_COOKIE_SECURE enabled behind HTTPS. Disabling secure cookies is only for loopback-only local HTTP development.

HMAC authenticates a request but does **not** encrypt it. Use HTTPS or a private network. Do not expose the development server directly to the internet. Store secrets using environment configuration for local work and a secret manager for deployment.

## Before real-data use

1. Confirm the exact hardware and heart-rate sensor model; implement and validate the BPM adapter.
2. Build and flash the firmware, replace the CA placeholder, and verify certificate-validated HTTPS on the device.
3. Use `IOT_DEVICE_SECRETS_JSON` for unique device credentials and define secure provisioning, rotation, and revocation.
4. Put the API behind HTTPS, distributed proxy-level rate limiting, monitoring, and an incident-response process.
5. Define access control, retention/deletion, encrypted storage and backups, and privacy requirements. The `backend.maintenance` CLI supports dry-run retention and backup-before-delete, but does not replace a tested backup/restore process.
6. Test the complete device → API → history → authorized dashboard flow with synthetic data before any real-data use.
7. Verify data permissions in a signed-out browser and remove personal identifiers unless genuinely required.
8. Treat dashboard indicators as informational only, not medical diagnosis or a substitute for professional equipment/advice.

The simulator proves the software protocol path only. Physical pin assignments, sensor calibration, heart-rate calculations, and hardware-side behavior remain unverified.

## Reporting a vulnerability

Please report issues privately to the repository owner through a channel listed on their GitHub profile. Do not publish private health data, credentials, or exploitable details in a public issue.
