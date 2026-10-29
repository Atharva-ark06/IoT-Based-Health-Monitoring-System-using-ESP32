# Secrets Rotation Runbook

Rotate credentials after suspected exposure, staff changes, or the approved rotation interval.

1. Identify the affected secret and every consumer.
2. Generate a new high-entropy value using an approved secret manager or local cryptographic generator.
3. Deploy the new value to the intended runtime without committing it.
4. Verify authenticated synthetic traffic using the new value.
5. Revoke the old value after confirming all consumers have migrated.
6. Review logs and repository history for accidental disclosure.
7. Record rotation metadata only, never the secret itself.

For per-device HMAC keys, plan a staged rollout and fail closed for unknown or revoked identities.
