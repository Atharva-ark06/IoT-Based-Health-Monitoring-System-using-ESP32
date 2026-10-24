# Container deployment guide

This phase packages the FastAPI API and integrated dashboard in a small Python image. It is a deployment starting point, not a claim of production certification or hardware verification.

## Included controls

- Runs as an unprivileged `app` user.
- Keeps SQLite in a named persistent volume at `/app/data`.
- Exposes port 8000 on loopback only by default; it is not directly internet-facing.
- Requires device, read API, dashboard, session, and external-origin configuration instead of silently supplying defaults.
- Keeps dashboard cookies secure by default.
- Drops Linux capabilities, enables `no-new-privileges`, uses a read-only container root filesystem, and provides a small writable `/tmp`.
- Includes a health check for `/healthz`.
- Excludes local environment files, SQLite data, tests, and ESP32 `secrets.h` from the Docker build context.

## Prerequisites

Install Docker Engine/Desktop with Docker Compose v2. For remote use, configure a trusted HTTPS reverse proxy and a valid certificate before exposing the service. The application itself does not terminate TLS.

## Configure secrets

Create a local `.env` file in the repository root. Do not commit it. Generate unique values rather than reusing the examples below:

```dotenv
IOT_DEVICE_HMAC_SECRET=replace-with-a-random-device-secret
IOT_READ_API_TOKEN=replace-with-a-different-random-read-token
IOT_DASHBOARD_PASSWORD=replace-with-a-strong-dashboard-password
IOT_SESSION_SECRET=replace-with-at-least-32-random-characters
IOT_DASHBOARD_ORIGIN=https://your-real-dashboard-host.example
```

For example, use a password manager or a trusted local secret generator. Use separate values for each setting. The placeholder values above are documentation only and must not be used as deployment credentials.

## Build and start

```sh
docker compose config
docker compose build --no-cache
docker compose up -d
docker compose ps
docker compose logs --tail=100 api
```

Verify health from the same host:

```sh
curl --fail http://127.0.0.1:8000/healthz
```

Open the dashboard through the configured HTTPS reverse proxy, not through a public plain-HTTP port. `IOT_DASHBOARD_ORIGIN` must match the browser's origin exactly. The compose file deliberately binds the application to `127.0.0.1:8000` so a separately managed proxy can forward traffic to it.

## Update and stop

```sh
docker compose up -d --build
docker compose down
```

The named `iot-data` volume survives `docker compose down`. Removing it explicitly destroys local stored readings; make a backup and establish a retention policy before handling any non-synthetic data.

## Operational limitations

- Do not expose port 8000 directly to the internet. Configure and test HTTPS, proxy request-size/time limits, login rate limiting, monitoring, and firewall policy separately.
- The compose template injects environment variables; for production, prefer the platform's managed secret store or Docker secrets integration and define a rotation process.
- SQLite is not encrypted at rest by this application. Protect the volume and backups with host-level access controls and encryption.
- A successful image build and `/healthz` response do not validate end-to-end authorization, external TLS configuration, backups, load handling, or real sensor data.
- The firmware still requires the correct board, sensor-specific BPM adapter, CA certificate, and hardware acceptance testing.
- This is an educational prototype, not a medical device or diagnostic service.
