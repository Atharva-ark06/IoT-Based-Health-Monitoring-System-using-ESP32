# Data Classification

Use a simple classification model to guide handling decisions.

- **Public:** source code and documentation intended for public release.
- **Internal:** non-sensitive operational notes and deployment configuration without credentials.
- **Confidential:** access tokens, HMAC secrets, session secrets, private logs, and database backups.
- **Sensitive personal data:** any readings that can be linked to an identifiable person.

Store secrets outside source control. Restrict confidential artifacts to authorized operators. Treat pseudonymized health readings as potentially sensitive because combinations of timestamps and device identifiers may enable linkage.
