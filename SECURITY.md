# Security Notes

This repository is an educational IoT health-monitoring prototype, not a production medical system.

## Scope and data flow

The current repository contains a browser-based dashboard at `health/sensor_dashboard.html`. The dashboard downloads CSV data directly from a configured HTTPS source and renders sensor readings in the browser. No ESP32 firmware source or server-side ingestion service is currently present in the repository, so device authentication and firmware transport controls cannot yet be verified or implemented here.

## Data classification

Temperature and heart-rate readings can be sensitive personal data. Treat real readings as confidential even when the dashboard is only used for a classroom demonstration.

- Use synthetic readings for demos, screenshots, tests, and public examples.
- Do not publish a spreadsheet containing real readings or personal identifiers.
- A spreadsheet ID or URL is not an authentication mechanism. Anyone with access to a public export can retrieve its data.
- Configure the dashboard only with an HTTPS CSV endpoint that is intentionally readable by its intended audience.
- Do not put passwords, API keys, bearer tokens, or private credentials in HTML, JavaScript, Git history, or a public repository.

## Threat model

| Threat | Example | Mitigation / current status |
| --- | --- | --- |
| Unintended data disclosure | A public spreadsheet exposes real sensor readings | Use synthetic data; restrict source sharing; verify access in a signed-out browser |
| Script injection | A timestamp in imported CSV contains HTML or script markup | Render imported values as text or HTML-escape them before inserting markup |
| Malformed or incomplete readings | Missing fields or non-numeric values skew analytics | Validate readings and calculate paired metrics only from complete pairs |
| Transport interception | Data source is fetched over cleartext HTTP | Require HTTPS for remote sources |
| Unauthorized device writes | An unauthenticated device submits forged readings | The API requires HMAC-SHA256 signatures, a five-minute timestamp window, and single-use nonces; firmware/key provisioning remains absent |
| Embedded credential exposure | Wi-Fi password or API token is committed | Keep credentials out of source control; use local configuration and server-side secrets where applicable |
| Dependency compromise | Third-party scripts change or become unavailable | Pin dependency versions, review upgrades, and consider self-hosting/integrity controls before production use |

## Dashboard source configuration

The dashboard reads its CSV source from the `sensor-data-url` meta tag in the HTML. Set its content to an HTTPS CSV URL only when you have deliberately configured the source for the intended audience. The URL is visible to every dashboard visitor; never use it to carry a secret or to grant access to private data.

If the source is not configured, the dashboard should remain idle and explain how to configure it instead of silently requesting a repository-maintained spreadsheet.

## Ingestion API security boundary

The optional API in `backend/app.py` authenticates write requests with HMAC-SHA256 over the timestamp, nonce, and exact request body. It rejects timestamps outside a five-minute window, duplicate nonces, unexpected fields, out-of-range readings, and oversized payloads. Reading retrieval requires a separate bearer token. The service does not enable CORS, and its read token must never be embedded in the static dashboard.

This does **not** replace TLS: deploy behind HTTPS or keep the service on a private network. The API does not implement device enrollment, per-device secrets, encrypted-at-rest storage, a production rate limiter, user accounts, or firmware-side HMAC signing. SQLite is not encrypted by this application. Do not use real health data until those deployment and privacy requirements are addressed.

## Before using real data

1. Confirm that the source contains no real personal or health data unless sharing is explicitly authorized.
2. Test source permissions from a signed-out/private browser session.
3. Use HTTPS and an access-controlled service for any non-public readings.
4. If adding an ingestion API, require device authentication, validate schema and ranges server-side, rate-limit requests, and avoid logging sensitive payloads.
5. Rotate any credential that was ever committed; deleting it from the latest revision does not remove it from Git history.
6. Treat dashboard indicators as informational only. They are not clinical decisions or a substitute for medical advice.

## Reporting a vulnerability

Please do not publish private health data, credentials, or an exploitable vulnerability in an issue. Contact the repository owner privately through a channel listed on their GitHub profile and include a minimal reproduction without sensitive data.
