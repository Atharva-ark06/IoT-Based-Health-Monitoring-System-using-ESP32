# Dependency Update Policy

- Pin or constrain runtime dependencies deliberately and review changes to lock files or requirement constraints.
- Run unit/integration tests and dependency auditing after updates.
- Review upstream release notes for breaking changes and security fixes.
- Prefer supported versions and remove unused dependencies.
- Do not treat an audit report as proof of exploitability or safety; assess reachability and mitigation.
- Record exceptions with owner and review date.

The existing CI includes dependency auditing; this policy describes the review process around its results.
