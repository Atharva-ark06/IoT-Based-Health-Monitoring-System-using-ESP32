# Observability Baseline

Define the minimum evidence needed to understand the API without collecting sensitive readings unnecessarily.

## Signals
- **Availability:** successful `/healthz` and `/readyz` responses.
- **Latency:** request duration by route and status class.
- **Errors:** validation failures, rejected signatures, database failures, and unexpected 5xx responses.
- **Saturation:** database size, disk free space, process memory, and request volume.

Do not log passwords, cookies, bearer tokens, HMAC secrets, or raw health payloads. This document is a rollout baseline; metrics export is not claimed to exist yet.
