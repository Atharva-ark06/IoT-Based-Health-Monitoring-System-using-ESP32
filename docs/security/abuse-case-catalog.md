# Abuse Case Catalog

Review these abuse cases during security testing:

1. Replay a previously signed ingestion request.
2. Guess or brute-force the dashboard password.
3. Reuse a revoked or unknown device key.
4. Request excessive history ranges or oversized bodies.
5. Attempt cross-origin dashboard actions.
6. Read database files or backups with unintended permissions.
7. Poison logs with control characters in user-controlled fields.
8. Exhaust disk through unbounded retention or backups.
9. Abuse retry behavior to amplify traffic.
10. Expose secrets through exceptions or CI output.

Map each case to a mitigation, test, and known limitation.
