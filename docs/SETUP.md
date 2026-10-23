# Setup Guide

This guide runs the existing static dashboard and the optional authenticated API locally. It does not configure a real ESP32 end-to-end: the firmware `.ino` source and device-side signing implementation are not currently in the repository.

## Requirements

- Git
- Python 3.11 or newer
- Node.js 20+ (only for dashboard regression tests)
- A modern browser

## 1. Clone and prepare Python

Windows PowerShell:

```powershell
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
cd IoT-Based-Health-Monitoring-System-using-ESP32

py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend/requirements.txt
```

If PowerShell blocks activation, use a permitted local environment policy or invoke the venv interpreter directly with `.\.venv\Scripts\python.exe`; do not weaken machine-wide execution policy just for this project.

## 2. Configure local API secrets

Create independent random values for device signing and read access. Keep them in the current shell only; do not paste them into source files or commit them.

```powershell
$env:IOT_DEVICE_HMAC_SECRET = (python -c "import secrets; print(secrets.token_hex(32))")
$env:IOT_READ_API_TOKEN = (python -c "import secrets; print(secrets.token_urlsafe(32))")
$env:IOT_DATABASE_PATH = "data/readings.sqlite3"
```

Start the API bound to loopback:

```powershell
python -m uvicorn backend.app:app --host 127.0.0.1 --port 8000
```

In a second terminal, check service health:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/healthz
```

Expected response:

```json
{"status":"ok"}
```

The read endpoint requires the separate bearer token:

```powershell
$headers = @{ Authorization = "Bearer $env:IOT_READ_API_TOKEN" }
Invoke-RestMethod "http://127.0.0.1:8000/api/v1/readings?limit=20" -Headers $headers
```

A fresh database returns an empty readings list. The write endpoint intentionally rejects unsigned requests; this repository does not yet provide a production device-side signing client.

## 3. Run the automated checks

From the repository root, with the virtual environment active:

```powershell
python -m pytest -q tests/test_ingestion_api.py
node --test tests/dashboard-security.test.mjs
```

The GitHub Actions security workflow additionally runs Bandit and pip-audit. Local success is not a substitute for checking the CI result for the exact commit you intend to merge.

## 4. Open the existing dashboard

Open `health/sensor_dashboard.html` in a browser, or serve it using a local/static web server. The dashboard uses an HTTPS CSV source configured through a `sensor-data-url` meta tag in its HTML `<head>`, for example:

```html
<meta name="sensor-data-url" content="https://your-approved-host.example/readings.csv">
```

Use only a source that is intentionally accessible to the dashboard audience. The URL is visible to anyone who can view the HTML. Do not use a private spreadsheet export or put a bearer token in the URL. The existing dashboard is **not connected** to the authenticated API; its read token must never be embedded in browser JavaScript.

## 5. Hardware setup status

The project description references ESP32, DHT11, and a heart-rate sensor, but no firmware source is currently checked in. Therefore pin assignments, sensor library versions, calibration, Wi-Fi configuration, and the device-side HMAC algorithm cannot be verified from this repository. Do not wire a device to real health-data infrastructure until firmware, key provisioning, TLS validation, and end-to-end tests have been reviewed.

## Safe teardown

Stop Uvicorn with Ctrl+C. Close the PowerShell sessions holding the temporary environment variables. Treat any value exposed in a screenshot, issue, or terminal log as compromised and rotate it.
