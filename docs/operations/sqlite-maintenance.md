# SQLite Maintenance Guidance

SQLite maintenance must account for file permissions, concurrent writers, and backup integrity.

- Run maintenance as the same restricted service identity used for normal database access.
- Stop or coordinate writers before operations that require exclusive access.
- Back up before retention deletion or schema changes.
- Prefer SQLite's online backup support over copying a live database file blindly.
- Check available disk space before backup and vacuum operations.
- Validate the database after maintenance and keep a record of the operation.

Use the maintenance CLI's dry-run mode first. Never run destructive retention commands without an approved retention period and a fresh backup.
