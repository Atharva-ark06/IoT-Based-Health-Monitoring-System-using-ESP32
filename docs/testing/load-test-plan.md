# Load Test Safety Plan

Load tests can exhaust resources, so keep them controlled.

- Obtain explicit authorization for the target environment.
- Use synthetic payloads and an isolated database.
- Define maximum concurrency, request rate, duration, and automatic stop conditions.
- Increase load gradually and monitor errors, latency, CPU, memory, and disk.
- Include a cooldown period and verify service recovery.
- Never load-test third-party or public production infrastructure without approval.
- Record the exact revision and test configuration.
