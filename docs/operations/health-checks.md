# Health Check Semantics

Use liveness and readiness checks for different questions.

- `/healthz` should indicate that the process can answer requests.
- `/readyz` should indicate that essential dependencies, especially the configured database, can serve requests.
- A failed readiness check should remove the instance from service where the deployment platform supports that behavior.
- Avoid returning exception text, file paths, credentials, or database contents in health responses.
- Test checks with a missing or unavailable database and verify the response is deterministic.

The current API exposes both endpoints; deployment-specific probe wiring must still be verified.
