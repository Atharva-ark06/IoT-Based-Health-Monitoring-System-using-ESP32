# Rollback Runbook

Use rollback when a release causes a security regression, repeated service failures, or data integrity concerns.

1. Declare the incident and identify the affected release digest.
2. Stop further deployments.
3. Check whether the release changed database schema or data format.
4. Restore the last known-good application image only if it is compatible with the current data schema.
5. Preserve logs and audit metadata needed for investigation.
6. Verify readiness, signed synthetic ingestion, and authenticated retrieval.
7. Document the cause and follow-up actions.

Never delete the only copy of production-like data during rollback. Database downgrade behavior is not claimed to be automated.
