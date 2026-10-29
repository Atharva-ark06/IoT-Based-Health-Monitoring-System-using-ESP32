# Backup Restore Drill

A backup is not considered reliable until restoration is tested.

1. Select a recent backup and verify its checksum or storage integrity metadata.
2. Restore to an isolated, access-controlled test location.
3. Open the restored SQLite database and run integrity checks.
4. Confirm expected tables and representative row counts without displaying sensitive values.
5. Start the application against the restored copy in a non-public test environment.
6. Verify readiness and authenticated retrieval.
7. Record duration, errors, backup age, and corrective actions.

Never overwrite the active database during a drill. No successful restore drill is claimed by this checklist.
