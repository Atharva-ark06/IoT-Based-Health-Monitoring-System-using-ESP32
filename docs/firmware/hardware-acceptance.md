# Hardware Acceptance Plan

Physical acceptance requires the exact hardware components to be recorded.

- Board model and revision: [record].
- Temperature sensor model and pin mapping: [record].
- Heart-rate sensor model and validated library: [record].
- Power supply and safe operating range: [record].
- Network and TLS test environment: [record].
- Firmware revision and build output: [record].
- Test cases for disconnected sensor, invalid reading, Wi-Fi loss, clock failure, and certificate failure: [record].

Do not fill in unknown sensor details by assumption. The current heart-rate adapter intentionally fails closed until the actual sensor is known.
