#pragma once
// Copy to secrets.h locally. secrets.h is ignored by Git.
// Provision unique, random credentials per device; never commit real values.
#define WIFI_SSID "replace-with-wifi-name"
#define WIFI_PASSWORD "replace-with-wifi-password"
#define DEVICE_ID "esp32-lab-01"
#define API_URL "https://your-api-host.example/api/v1/readings"
#define DEVICE_HMAC_SECRET "replace-with-the-exact-IOT_DEVICE_HMAC_SECRET-value"

// Paste the PEM root/intermediate CA certificate appropriate for API_URL.
// Certificate validation is intentionally enabled; do not use setInsecure().
static const char ROOT_CA_CERT[] = R"EOF(
-----BEGIN CERTIFICATE-----
REPLACE_WITH_REAL_CA_CERTIFICATE
-----END CERTIFICATE-----
)EOF";
