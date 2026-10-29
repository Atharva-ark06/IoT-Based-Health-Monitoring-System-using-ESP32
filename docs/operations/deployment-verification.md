# Deployment Verification

Use a repeatable post-deployment check rather than relying on a successful container start.

1. Confirm the image digest and release revision.
2. Confirm the process runs as a non-root user.
3. Confirm the port is bound only to the intended interface.
4. Call `/healthz` and `/readyz`.
5. Perform a signed synthetic ingestion request.
6. Verify authenticated history access and dashboard login/logout.
7. Confirm security headers and secure cookie settings in the deployed environment.
8. Review logs for startup errors without exposing secrets.
9. Record the result and operator in the release record.
