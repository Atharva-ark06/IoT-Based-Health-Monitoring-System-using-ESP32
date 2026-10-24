# End-to-End Integration Test

This procedure exercises the simulator → signed API request → SQLite → authenticated dashboard path without physical hardware.

## 1. Start the API

Follow the local secret setup in SETUP.md. Run the API on 127.0.0.1 only and keep the generated values in the terminal environment.

## 2. Send synthetic readings

In a second PowerShell terminal, activate the virtual environment and set IOT_DEVICE_HMAC_SECRET to the same device secret used by the API. Run:

~~~powershell
python -m simulator.device_simulator --count 5 --interval 1
~~~

Expected behavior: each simulated request prints an HTTP 201 status. The simulator emits synthetic data and never prints request bodies, signatures, or secrets.

## 3. View dashboard history

Open http://127.0.0.1:8000/dashboard, sign in with IOT_DASHBOARD_PASSWORD, and refresh the readings. The most recent synthetic readings should appear in the metrics and table.

## 4. Negative checks

- Run the Python tests to verify missing or invalid device signatures are rejected.
- Confirm GET /api/v1/dashboard/readings returns 401 in a fresh unauthenticated client.
- Confirm the login endpoint rejects an incorrect password and a mismatched Origin.
- Confirm the dashboard browser code has no server bearer token.
- Confirm the Node tests check safe text rendering of incoming values.

## 5. Hardware integration is a separate acceptance gate

Do not mark physical integration complete until the exact sensor model is known, the firmware compiles, the heart-rate adapter is implemented and validated, a real device uses certificate-validated HTTPS, and a device-originated reading appears in the dashboard. Simulator success proves the software protocol path, not sensor accuracy or hardware operation.
