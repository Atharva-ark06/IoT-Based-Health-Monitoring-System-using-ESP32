# Access Review Procedure

Review access whenever a maintainer leaves, a deployment target changes, or a new integration is introduced.

1. Enumerate repository collaborators, deployment operators, database readers, and secret holders.
2. Confirm each person still requires access.
3. Remove stale permissions and rotate shared secrets if exposure is possible.
4. Verify CI tokens and deployment credentials have minimum required scope.
5. Record reviewer, date, exceptions, and next review date.

Public repository access does not imply access to runtime secrets or private health data.
