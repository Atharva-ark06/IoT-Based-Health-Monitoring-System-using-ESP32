# Operations, Privacy, Security, and Verification Guides

This directory tree contains operational checklists and proposed procedures for the educational health-monitoring prototype. These guides are **planning and review artifacts**; they do not claim that production monitoring, legal compliance, real-data workflows, or physical hardware validation is already implemented.

## Operations
- [Observability baseline](observability.md)
- [Alerting policy](alerting-policy.md)
- [Logging policy](logging-policy.md)
- [Metrics catalog](metrics-catalog.md)
- [Health-check semantics](health-checks.md)
- [Readiness checklist](readiness-checks.md)
- [Deployment verification](deployment-verification.md)
- [Release checklist](release-checklist.md)
- [Rollback runbook](rollback-runbook.md)
- [Backup policy](backup-policy.md)
- [Restore drill](restore-drill.md)
- [SQLite maintenance](sqlite-maintenance.md)
- [Audit event schema](audit-event-schema.md)
- [Audit review](audit-review.md)
- [Disaster recovery](disaster-recovery.md)
- [Maintenance window](maintenance-window.md)
- [Service-level objectives template](service-level-objectives.md)
- [Phases 11–15 roadmap](phase-11-15-roadmap.md)

## Privacy
See the sibling `docs/privacy/` guides for data minimization, retention, synthetic data, export controls, and privacy-impact review.

## Security and device lifecycle
See `docs/security/` for access review, secrets rotation, incident handling, vulnerability management, and device lifecycle procedures. Firmware acceptance templates live in `docs/firmware/`.

## Verification
See `docs/testing/` for manual acceptance, security matrix, performance, load, and resilience test plans.

All checklists must be completed against the actual target environment. Do not mark unexecuted checks as passed, and do not use real personal health data for demonstration or automated tests.
