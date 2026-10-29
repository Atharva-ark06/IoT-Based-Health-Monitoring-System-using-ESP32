# Readiness Acceptance Checklist

Before declaring an instance ready:

- [ ] Required environment variables are present and non-empty.
- [ ] Database path is writable by the configured runtime user.
- [ ] Database schema initialization or migration completed successfully.
- [ ] The readiness endpoint returns success only when essential dependencies are usable.
- [ ] The dashboard login flow works over the intended origin.
- [ ] No secret is printed in startup logs.
- [ ] Synthetic ingestion and authenticated retrieval succeed in a test environment.

Do not use real health data as a deployment smoke test.
