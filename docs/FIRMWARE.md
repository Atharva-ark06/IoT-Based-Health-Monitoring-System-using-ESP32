# ESP32 Firmware Integration

## Status

This is an integration scaffold, not a hardware-verified firmware release. It demonstrates the API's request-signing protocol, Wi-Fi reconnection, NTP time synchronization, TLS CA verification, and local secret separation. The heart-rate adapter intentionally returns NAN until the sensor model and library are confirmed. The firmware therefore refuses to upload readings with a fake BPM value.

## Arduino IDE setup

1. Install the ESP32 board support package for the board you actually have.
2. Install the Adafruit DHT sensor library and ArduinoJson 6.x.
3. Copy secrets.example.h to secrets.h in the same folder. The local secrets.h path is ignored by Git.
4. Set Wi-Fi SSID/password, a device ID, the HTTPS API URL, the exact device HMAC secret configured on the server, and the valid PEM CA certificate for the API hostname.
5. Check the DHT11 wiring and DHT_PIN setting. The sketch example uses GPIO 4; verify that against your board and wiring.
6. Implement readHeartRateBpm() for the exact sensor model, including its sampling algorithm and invalid-signal handling.
7. Build and flash the sketch; inspect only non-sensitive status messages on the serial monitor.

## Secret handling

The device HMAC secret must match IOT_DEVICE_HMAC_SECRET on the API. Use a different random secret for each real device. Do not commit secrets.h or paste real values into issue trackers. For production, use a provisioning strategy appropriate to the device's secure-storage capabilities and document rotation/revocation.

## TLS and clock requirements

The sketch calls WiFiClientSecure.setCACert(ROOT_CA_CERT). Replace the example placeholder with the real CA certificate chain required by your API endpoint. Do not replace certificate validation with setInsecure(). The device synchronizes time before signing because the server rejects stale Unix timestamps. If Wi-Fi or clock synchronization fails, the sample is skipped.

## Signing compatibility

The firmware signs the exact serialized JSON body with HMAC-SHA256 over:

~~~text
unix_timestamp + "." + nonce + "." + raw_json_body
~~~

The header names and format match backend/app.py. The body must not be reserialized after signing. A 16-byte random nonce is hex-encoded, and the signature is lowercase hexadecimal.

## Still to verify

- Exact board, DHT pinout, heart-rate sensor model, and wiring.
- BPM algorithm and signal-quality behavior.
- Arduino compilation against installed board/library versions.
- Valid TLS certificate and real endpoint reachability.
- Upload accepted by API and visible in the authenticated dashboard.
- Wi-Fi loss/reconnect and clock drift behavior.
- No secret logging and no secret committed to the repository.
