# Firmware Release Checklist

- [ ] Confirm the exact ESP32 board and core version.
- [ ] Confirm sensor model, library, wiring, sampling method, and units.
- [ ] Replace placeholder CA configuration with verified trust material.
- [ ] Configure Wi-Fi and per-device key outside tracked files.
- [ ] Verify certificate validation and NTP/time behavior.
- [ ] Test signature bytes against the API contract.
- [ ] Confirm no reading is uploaded when the sensor adapter fails.
- [ ] Compile and record toolchain versions.
- [ ] Test on physical hardware and document results before claiming device validation.

A successful generic compile does not prove correct hardware behavior.
