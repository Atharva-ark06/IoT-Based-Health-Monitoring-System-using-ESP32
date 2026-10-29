# Rate Limit Validation Plan

Validate the existing process-local throttling and document its limits.

- Confirm excess login attempts receive HTTP 429 and a sensible `Retry-After` value.
- Confirm valid requests resume after the window expires.
- Verify unrelated clients are not accidentally blocked by a test fixture.
- Test concurrent requests and application restart behavior.
- Document that in-process counters reset on restart and are not shared across multiple workers.
- Require a reverse-proxy or distributed limiter before scaling beyond a single process.

Do not load-test a public deployment without authorization and a defined traffic ceiling.
