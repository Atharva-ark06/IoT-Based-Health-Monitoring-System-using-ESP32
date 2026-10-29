# TLS Certificate Rotation

Certificate rotation should avoid silent trust failures and insecure fallback.

- Track certificate expiry and identify the actual certificate authority chain used by the deployment.
- Obtain the replacement certificate from the approved authority.
- Validate hostname, chain, validity period, and trust store before rollout.
- Deploy the new trust configuration and test HTTPS from a controlled client.
- Remove expired or no-longer-trusted material after confirming migration.
- Ensure firmware fails closed when certificate validation fails; never disable verification as a workaround.

The firmware's placeholder CA material must be replaced and validated against the real deployment before hardware use.
