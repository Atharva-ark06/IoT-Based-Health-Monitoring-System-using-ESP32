# Logging Policy

Logs support troubleshooting while protecting health-related data.

## Required practices
- Prefer structured fields: timestamp, route template, status, duration, request correlation ID, and event category.
- Never include authentication secrets, session cookies, raw request bodies, or full patient-like records.
- Sanitize untrusted values before logging to prevent log injection.
- Restrict log access and set retention based on an approved policy.
- Review any new log field for privacy impact before release.

Audit events should remain metadata-only unless a documented, approved need says otherwise.
