# Alerting Policy

Alerts should be actionable, owned, and tied to a runbook.

## Candidate alerts
- Readiness failures sustained across multiple checks.
- Elevated 5xx rate or repeated database write errors.
- Disk usage approaching the operator-defined threshold.
- Repeated login throttling or signature failures above normal baseline.
- Backup job failure or overdue restore drill.

Set thresholds only after observing a representative baseline. Avoid alerting on a single transient failure. The repository does not currently claim a hosted alerting service.
