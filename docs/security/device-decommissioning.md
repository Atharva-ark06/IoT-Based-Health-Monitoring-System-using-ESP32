# Device Decommissioning

When a device is retired, lost, or suspected compromised:

- Mark its identity revoked in the operator's source of truth.
- Remove its key from active server configuration and reload safely.
- Verify requests signed with the retired key are rejected.
- Preserve only metadata required for audit and troubleshooting.
- Remove local secrets and securely reset or dispose of the device where feasible.
- Rotate shared credentials if the device used any shared secret.

Do not reuse a retired device identifier without a documented migration and audit plan.
