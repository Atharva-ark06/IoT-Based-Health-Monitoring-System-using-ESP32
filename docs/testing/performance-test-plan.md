# Performance Test Plan

Establish a baseline in an isolated environment with synthetic readings only.

- Measure normal ingestion latency at a controlled request rate.
- Measure dashboard history latency for bounded result sizes.
- Record CPU, memory, database size, and disk usage.
- Include database contention and disk-near-full scenarios.
- Define a fixed duration and stop condition before running.
- Record revision, environment, sample size, latency percentiles, and errors.

Do not publish performance numbers until the test has actually run.
