# Architecture and How It Works

## Integrated flow

~~~text
Layer 1 — Data source
  Synthetic simulator (available now) OR ESP32 firmware scaffold
                 │ HMAC-signed JSON over HTTPS
                 ▼
Layer 2 — API trust boundary
  FastAPI
  ├── POST /api/v1/readings             device signature + freshness + nonce
  ├── GET  /api/v1/readings             separate bearer token for trusted clients
  ├── POST /api/v1/dashboard/login      password + same-origin validation
  ├── GET  /api/v1/dashboard/readings   short-lived HttpOnly session cookie
  ├── POST /api/v1/dashboard/logout     session + same-origin validation
  └── GET  /healthz                     minimal health check
                 │ validated fields + parameterized SQL
                 ▼
Layer 3 — Storage
  SQLite readings table + replay nonce table
                 │ session-protected same-origin API
                 ▼
Layer 4 — User interface
  /dashboard + /dashboard.js
  No server bearer token or device secret in browser JavaScript
~~~

The existing health/sensor_dashboard.html is a separate static dashboard that reads a configured HTTPS CSV source. The new /dashboard page is served by FastAPI and reads the API database through a browser session. The two dashboards are intentionally distinct.

## Request signing

For a request with Unix timestamp T, nonce N, and exact request-body bytes B, the signature is:

~~~text
HMAC-SHA256(device_secret, ASCII(T + "." + N + ".") + B)
~~~

The API verifies the timestamp is within five minutes, validates the nonce syntax, verifies the signature with a constant-time comparison, validates the payload, and atomically stores the nonce and reading. Reusing a nonce results in a conflict. The HMAC authenticates the message; TLS is still required to protect transport.

## Dashboard authentication

The user enters the dashboard password into the same-origin page. The server checks the configured Origin and password, then sets a short-lived signed session cookie marked HttpOnly and SameSite=Strict. Secure is enabled by default and should remain enabled over HTTPS. Local loopback testing may explicitly disable Secure because the local server uses HTTP.

The dashboard fetches history using the cookie; it never reads or stores IOT_READ_API_TOKEN. Login/logout Origin checks and same-site cookie policy reduce cross-site request risks. This is a prototype authentication layer, not a replacement for a production identity provider, rate limiting, monitoring, or session revocation infrastructure.

## Database

- readings stores device_id, sensor timestamp, temperature, BPM, and server received_at time.
- used_nonces tracks accepted nonces and removes expired entries during later ingestion.
- SQL parameters are bound; request fields are not interpolated into SQL.
- SQLite files are local prototype data and are not encrypted at rest by this application.

## Hardware boundary

The firmware sketch uses a DHT11 example on GPIO 4 and requires a real CA certificate, Wi-Fi settings, endpoint, device ID, and device HMAC secret in a local ignored secrets.h file. The heart-rate adapter is a deliberate TODO until the actual sensor model is known; it returns NAN so the firmware fails closed rather than uploading fabricated BPM. Physical compilation, wiring, sensor calibration, and TLS configuration remain unverified.

## Trust boundaries and production gaps

- The device and browser are untrusted clients; the API validates all incoming readings.
- The browser receives only a session cookie, never the server bearer token.
- The API does not terminate TLS. Use a trusted HTTPS reverse proxy or private network.
- Use unique per-device secrets, secure provisioning, rotation/revocation, rate limiting, audit events, encrypted storage/backups, data retention, and monitoring before any real health data is processed.
- Synthetic test data must be identified as synthetic. This is not a medical or diagnostic system.
