# ESP32 Firmware Integration and Build Readiness

## Status

This is an integration scaffold, not a hardware-verified firmware release. It demonstrates the API's request-signing protocol, Wi-Fi connectivity, NTP time synchronization, TLS CA verification, and local secret separation. The heart-rate adapter intentionally returns NAN until the sensor model and library are confirmed. The firmware therefore refuses to upload readings with a fake BPM value.

Phase 6 adds a reproducible, hardware-free Arduino compile job. A successful compile proves that the sketch and its declared libraries build for the selected generic ESP32 target; it does not verify wiring, sensor accuracy, live TLS trust, endpoint reachability, or actual device behavior.

## Local Arduino CLI build

1. Install Arduino CLI and the ESP32 board platform.
2. Install the Adafruit DHT sensor library, Adafruit Unified Sensor, and ArduinoJson 6.21.5.
3. Copy secrets.example.h to secrets.h in the same folder. The local secrets.h path is ignored by Git.
4. For a compile-only check, placeholder values are enough. For a real device, configure Wi-Fi SSID/password, device ID, HTTPS API URL, the exact device HMAC secret configured on the server, and the valid PEM CA certificate for the API hostname.
5. Compile for a generic ESP32 target:

~~~powershell
arduino-cli core update-index --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli core install esp32:esp32 --additional-urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
arduino-cli lib install "DHT sensor library"
arduino-cli lib install "Adafruit Unified Sensor"
arduino-cli lib install "ArduinoJson@6.21.5"
Copy-Item firmware/esp32_health_monitor/secrets.example.h firmware/esp32_health_monitor/secrets.h
arduino-cli compile --fqbn esp32:esp32:esp32 --warnings all firmware/esp32_health_monitor
~~~

This generic board target is for a build check only. Select the exact board in the IDE or CLI before flashing physical hardware.

## Automated firmware build

The GitHub Actions workflow at .github/workflows/firmware-build.yml installs Arduino CLI, the ESP32 platform, and required libraries, creates a temporary ignored secrets.h from the placeholder template, then compiles the sketch. It uses no real credentials and does not upload firmware to a device.

## Arduino IDE setup

1. Install the ESP32 board support package for the board you actually have.
2. Install the Adafruit DHT sensor library, Adafruit Unified Sensor, and ArduinoJson 6.x.
3. Copy secrets.example.h to secrets.h in the same folder. The local secrets.h path is ignored by Git.
4. Set the real device configuration only in the local secrets.h file.
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

## Hardware acceptance checklist

- [ ] Confirm exact ESP32 board model and its pinout.
- [ ] Confirm temperature sensor model, supply voltage, wiring, and GPIO.
- [ ] Confirm heart-rate sensor model and use a sensor-specific sampling/BPM algorithm.
- [ ] Confirm invalid signal handling and that no guessed BPM value can be uploaded.
- [ ] Replace the placeholder CA certificate with the real trust chain for the API host.
- [ ] Provision a unique device secret without committing it.
- [ ] Build with the target board's Arduino toolchain and flash the device.
- [ ] Confirm HTTPS certificate validation and clock synchronization on the device.
- [ ] Send a signed device reading and verify it appears in the authenticated dashboard.
- [ ] Test Wi-Fi loss/reconnect, clock drift, rejected signatures, and replay behavior.
- [ ] Confirm no secrets, signatures, request bodies, or personal health data appear in logs.

Physical pin assignments, sensor calibration, heart-rate calculations, and hardware-side behavior remain unverified until the above checks are completed.
