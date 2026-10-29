# Device Enrollment Design

A production device-enrollment flow should bind a unique device identity to a dedicated secret.

1. Authenticate the administrator or provisioning station.
2. Assign a unique, non-reused device identifier.
3. Generate a high-entropy per-device key outside source control.
4. Transfer the key over a controlled provisioning channel.
5. Store it in protected device configuration or hardware-backed storage when supported.
6. Register the corresponding server-side mapping and status.
7. Verify signed synthetic traffic, then record enrollment metadata.

The current JSON secret map is configuration-based; a full enrollment service is not implemented.
