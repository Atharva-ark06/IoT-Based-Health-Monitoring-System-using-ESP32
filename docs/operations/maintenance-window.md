# Maintenance Window Checklist

Before planned maintenance:

- Announce the time window and expected impact to relevant users.
- Confirm a recent backup and available rollback path.
- Record the release revision and database state.
- Verify the maintenance command's dry-run output.
- Ensure the operator has only the required permissions.

After maintenance:
- Verify database integrity and readiness.
- Run synthetic ingestion and authenticated retrieval checks.
- Confirm no unexpected access or error spikes.
- Record start/end times, commands, outcomes, and follow-up actions.
