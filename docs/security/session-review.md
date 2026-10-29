# Dashboard Session Review

Review the session flow whenever authentication or deployment settings change.

- Session cookie must be `HttpOnly` and use the intended `SameSite` policy.
- `Secure` must be enabled when served over HTTPS.
- Login/logout should enforce the expected origin policy.
- Session lifetime and secret rotation behavior must be documented.
- Responses containing readings should not be cached by shared intermediaries.
- Passwords, cookies, and session identifiers must not appear in logs.
- Test missing, malformed, expired, and forged session cookies.

The current session mechanism is a prototype and should receive a production identity/security review before real personal data is used.
