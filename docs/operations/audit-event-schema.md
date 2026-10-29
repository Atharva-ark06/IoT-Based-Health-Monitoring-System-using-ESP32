# Audit Event Schema

Keep audit records metadata-only and version the schema when fields change.

Recommended fields:
- `event_id`: unique event identifier.
- `event_time`: timezone-aware timestamp.
- `event_type`: controlled event category.
- `actor_type`: service, operator, or device.
- `actor_ref`: non-secret identifier with limited disclosure.
- `outcome`: success or failure category.
- `request_id`: correlation identifier when available.

Never include passwords, cookies, HMAC keys, bearer tokens, or full readings. Define retention, access, and integrity protections before treating audit events as compliance evidence.
