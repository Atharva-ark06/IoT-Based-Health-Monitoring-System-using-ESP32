# Disaster Recovery Plan

Document recovery before the system is relied on for anything important.

- Critical assets: application source/image, runtime configuration, database, secrets, and deployment manifests.
- Recovery owner and backup contact: [assign].
- Approved backup location and retention: [define].
- Recovery time and recovery point objectives: [approve].
- Restore procedure: follow the restore drill and verify database integrity.
- Secret recovery: use an approved secret manager; do not restore secrets from source control.
- Validate readiness, signed synthetic ingestion, authenticated history, and dashboard sessions.

Test the plan periodically and record gaps. No disaster recovery guarantee is currently claimed.
