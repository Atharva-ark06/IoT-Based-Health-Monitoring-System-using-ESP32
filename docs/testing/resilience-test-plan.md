# Resilience Test Plan

Test failure modes using isolated fixtures and synthetic data.

- Database path unavailable or read-only.
- Database locked or disk full.
- Missing or malformed runtime secrets.
- Expired timestamp and repeated nonce.
- Unknown or revoked device identity.
- Network timeout, HTTP 429, and HTTP 5xx during simulator delivery.
- Restart during a request and loss of client acknowledgement.
- Backup destination unavailable.

Assert safe failure, bounded retries, useful status codes, and no secret leakage. Do not claim exactly-once delivery unless idempotency is implemented and tested.
