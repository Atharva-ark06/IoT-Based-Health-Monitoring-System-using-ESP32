# Operations, Device Keys, Resilience, and Data Retention

This guide covers the software-side operational controls. It does not certify production deployment or physical sensor behavior.

## Per-device credentials and rotation

For a deployment with more than one device, prefer `IOT_DEVICE_SECRETS_JSON` over the legacy shared `IOT_DEVICE_HMAC_SECRET`. The JSON value maps each allowed device ID to its own high-entropy HMAC secret:

```json
{
  "esp32-lab-01": "replace-with-a-unique-random-secret",
  "esp32-lab-02": "replace-with-a-different-random-secret"
}
```

Configure the value through the platform's secret manager. Do not commit a populated JSON file or place secrets in the README. When the per-device map is configured, only IDs present in that map are accepted; the legacy shared secret is not used as a fallback. This supports per-device revocation by removing an ID and rotation by updating that device's secret, then securely provisioning the matching secret to the device. Plan a coordinated update because the prototype does not support overlapping old/new keys or remote enrollment.

The legacy `IOT_DEVICE_HMAC_SECRET` remains available for local demos and backward compatibility. Do not treat it as per-device isolation.

## Rate limiting

The API applies in-process request limits to dashboard login and ingestion. Defaults are 5 login attempts and 120 ingestion requests per client IP per 60 seconds; a limit response is HTTP 429 with `Retry-After`.

These buckets live in the application process. They reset on restart, are not shared between multiple workers/replicas, and trust the ASGI client address. Keep proxy-level rate limiting enabled for deployed environments and configure trusted proxy behavior carefully. The in-process limiter is a defense-in-depth guard, not a distributed rate-limiting service.

## Readiness and audit metadata

- `GET /healthz` reports that the process is responding.
- `GET /readyz` checks that the configured SQLite database can be opened and queried.
- Successful ingestion, dashboard login success/failure, and logout produce metadata-only audit events. The log deliberately excludes passwords, HMAC keys, tokens, and reading values.
- `GET /api/v1/admin/audit?limit=100` requires a separate `Authorization: Bearer ...` token matching `IOT_MAINTENANCE_TOKEN`. Leave this variable unset if the endpoint is not needed; it then fails closed. Restrict access at the reverse proxy as well.

Audit events are stored in the same SQLite database as readings. They are not tamper-proof, and database write failures do not block normal requests. Export and monitor these events before relying on them for incident response.

## Backup and retention

Run a preview first:

```powershell
python -m backend.maintenance --database data/readings.sqlite3 --retention-days 90
```

This is a dry run. It reports how many old readings, audit events, and expired replay nonces match the policy; it does not delete data.

To apply a retention policy, provide a **new backup path**. The tool creates an online SQLite backup before deleting anything:

```powershell
python -m backend.maintenance --database data/readings.sqlite3 --retention-days 90 --backup-path data/backups/pre-retention.sqlite3 --apply
```

The command refuses to overwrite an existing backup or use the source database as its own backup. Store backups in an access-controlled location, encrypt them using host/platform controls, test restores periodically, and define who authorizes deletion. Retention defaults are examples, not legal/privacy advice. Confirm the applicable policy before handling any real health data.

## Resilient simulator sends

The hardware-free simulator retries transient network errors, HTTP 429, and HTTP 5xx responses up to three attempts by default with bounded exponential backoff. Each attempt uses a fresh timestamp and nonce to satisfy the replay-protection protocol. Permanent 4xx responses are not retried.

A response can be lost after the server has committed a reading, so retries do **not** provide an exactly-once guarantee and may create a duplicate reading in that rare case. The simulator is a software test client, not a durable store-and-forward queue. The ESP32 scaffold still needs a sensor-specific offline queue, bounded retry strategy, idempotency protocol, and on-device fault testing before field use.

## Production checklist

- [ ] Use unique device credentials through a secret manager; document revocation and rotation.
- [ ] Put the service behind a trusted HTTPS reverse proxy with proxy-level rate limits.
- [ ] Restrict the maintenance audit endpoint and monitor storage/health.
- [ ] Set and test retention policy; back up before deletion and periodically verify restore.
- [ ] Encrypt and restrict access to database files and backups at the host/platform layer.
- [ ] Decide whether audit retention, export, and alerting meet operational requirements.
- [ ] Test multi-worker deployment before using it; the in-process rate limiter is not distributed.
- [ ] Confirm actual ESP32 board and heart-rate sensor, then test real device delivery and recovery.
- [ ] Use synthetic readings until privacy, authorization, and deployment reviews are complete.

This is an academic prototype, not a medical device, diagnostic service, or emergency alert system.
