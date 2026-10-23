# Security Verification Guide

Use this checklist during review. A green workflow is evidence that the automated checks ran; it is not a certification or proof that the whole deployment is secure.

## Automated checks

From the repository root:

```powershell
python -m pip install -r backend/requirements.txt
python -m pytest -q tests/test_ingestion_api.py
node --test tests/dashboard-security.test.mjs
python -m pip install bandit pip-audit
bandit -q -r backend -ll
pip-audit
```

The `Security verification` GitHub Actions workflow runs these checks for relevant pushes and pull requests. Review the run associated with the exact commit SHA, not an earlier branch commit.

## API negative tests

- [ ] Missing authentication headers return 401.
- [ ] Invalid HMAC returns 401.
- [ ] Stale request timestamps return 401.
- [ ] A reused nonce returns 409.
- [ ] Oversized bodies return 413.
- [ ] Unknown fields, naive timestamps, and invalid sensor ranges are rejected.
- [ ] Reading retrieval without a valid bearer token returns 401.
- [ ] Invalid limits and malformed filter parameters are rejected.
- [ ] Device and time filters return only records inside the requested filter.
- [ ] Database errors do not disclose SQL, paths, or payloads in API responses.

## Manual review before deployment

- [ ] The API is exposed only through HTTPS or a private network.
- [ ] The reverse proxy and application enforce request-size limits and rate limits.
- [ ] Device secrets are unique per device, securely provisioned, and rotatable.
- [ ] ESP32 firmware validates TLS certificates and never logs secrets.
- [ ] The read token is stored server-side and is not embedded in HTML, JavaScript, query strings, or public CSV URLs.
- [ ] Database files and backups have restricted access and a defined retention/deletion policy.
- [ ] No real personal health readings appear in public fixtures, screenshots, logs, or CI artifacts.
- [ ] Third-party browser dependencies are reviewed and pinned or self-hosted where practical.
- [ ] Alerts and thresholds are described as informational, not diagnostic.
- [ ] Firmware and device-to-dashboard end-to-end tests are added once the firmware source is available.

## Reporting

Report vulnerabilities privately to the repository owner. Do not publish real health data, credentials, or exploitable details in a public issue.
