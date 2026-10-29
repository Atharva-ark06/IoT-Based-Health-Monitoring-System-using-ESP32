# Data Minimization

Collect only fields required for the explicitly approved prototype purpose.

- Avoid names, contact details, precise location, or other identifiers unless required and justified.
- Use synthetic readings in demonstrations and automated tests.
- Do not add free-text notes to readings without a reviewed need.
- Keep device identity separate from a person's identity.
- Review each new database column for purpose, retention, and access implications.
- Avoid copying production-like data into issue reports, screenshots, or CI artifacts.

A smaller dataset reduces exposure if credentials, logs, backups, or a development machine are compromised.
