# Incident Containment

Containment should reduce ongoing risk while preserving evidence.

- Revoke or rotate compromised credentials and device keys.
- Disable a suspected device identity if requests cannot be trusted.
- Restrict public access at the reverse proxy or deployment boundary when needed.
- Preserve relevant logs and database backups before cleanup.
- Avoid deleting records or rebuilding systems before the incident lead approves evidence preservation.
- Confirm containment through a safe test and monitor for recurrence.

Containment choices depend on deployment topology; this repository does not provide a managed incident-response service.
