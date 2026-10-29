# Device Key Compromise Response

Treat a suspected device HMAC key leak as an authentication incident.

1. Identify the device identity and time window of possible exposure.
2. Disable the affected key and reject subsequent requests using it.
3. Check metadata for unexpected request volume, timestamps, and nonce behavior.
4. Provision a replacement key through a controlled channel.
5. Verify valid requests with the replacement and rejection of the old key.
6. Review whether the key was committed, logged, included in an image, or stored in an artifact.
7. Document residual risk and prevention actions.

Never paste the key into an issue or incident report.
