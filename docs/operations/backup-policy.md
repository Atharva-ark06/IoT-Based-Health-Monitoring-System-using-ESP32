# Backup Policy

Backups must be protected as sensitive data because they may contain health-related readings and device metadata.

- Define an owner, schedule, retention period, and storage location before enabling automated backups.
- Restrict backup access to named operators and encrypt backups using the storage platform's approved mechanism.
- Use unique destination names and verify backup completion before deleting retained records.
- Do not store backups in the repository or public artifact locations.
- Record success/failure metadata without copying readings into logs.

The maintenance CLI supports online backup; a production schedule and managed encrypted destination are operator responsibilities.
