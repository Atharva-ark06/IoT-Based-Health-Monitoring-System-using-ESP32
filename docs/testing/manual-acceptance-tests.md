# Manual Acceptance Tests

Use synthetic values and a local or isolated deployment.

1. Start the API with generated development secrets.
2. Confirm `/healthz` and `/readyz` behavior.
3. Send signed simulator readings and confirm the accepted count.
4. Request history without a token and confirm denial.
5. Sign in to the dashboard and confirm private history loads.
6. Sign out and confirm the prior session no longer works.
7. Send a stale or replayed request and confirm rejection.
8. Inspect response headers and ensure sensitive responses are not cached.
9. Stop the service and verify graceful failure behavior.
10. Record actual results; do not mark unexecuted steps as passed.
