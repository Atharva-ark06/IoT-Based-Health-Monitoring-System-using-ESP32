# Security Test Matrix

| Control | Test idea | Expected outcome |
|---|---|---|
| HMAC signing | Alter one request byte | Reject request |
| Freshness | Use stale timestamp | Reject request |
| Replay defense | Reuse nonce | Reject duplicate |
| Read authorization | Omit bearer token | Deny history request |
| Dashboard session | Use invalid cookie | Deny private history |
| Origin check | Send untrusted origin | Reject state-changing action |
| Body limit | Exceed configured size | Reject safely |
| Rate limit | Exceed threshold | Return 429 |
| Secret hygiene | Scan logs/fixtures | No real credentials |

Run tests on the exact PR head and retain the result link.
