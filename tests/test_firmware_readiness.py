from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
FIRMWARE_DIR = ROOT / "firmware" / "esp32_health_monitor"
SKETCH = FIRMWARE_DIR / "esp32_health_monitor.ino"
EXAMPLE_SECRETS = FIRMWARE_DIR / "secrets.example.h"
GITIGNORE = ROOT / ".gitignore"


class FirmwareReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sketch = SKETCH.read_text(encoding="utf-8")
        cls.example_secrets = EXAMPLE_SECRETS.read_text(encoding="utf-8")
        cls.gitignore = GITIGNORE.read_text(encoding="utf-8")

    def test_firmware_uses_certificate_validation_not_insecure_tls(self):
        self.assertIn("tlsClient.setCACert(ROOT_CA_CERT)", self.sketch)
        self.assertNotRegex(self.sketch, r"\btlsClient\.setInsecure\s*\(")

    def test_heart_rate_adapter_fails_closed_until_implemented(self):
        adapter = re.search(
            r"float\s+readHeartRateBpm\s*\(\)\s*\{(?P<body>.*?)\n\}",
            self.sketch,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(adapter)
        self.assertIn("return NAN;", adapter.group("body"))

    def test_firmware_signs_exact_body_and_expected_headers(self):
        self.assertIn('timestampHeader + "." + nonce + "." + body', self.sketch)
        for header in (
            "X-Device-Timestamp",
            "X-Device-Nonce",
            "X-Device-Signature",
        ):
            self.assertIn(f'\\"{header}\\"', self.sketch)

    def test_secret_template_contains_placeholders_not_credentials(self):
        for placeholder in (
            "replace-with-wifi-name",
            "replace-with-wifi-password",
            "replace-with-the-exact-IOT_DEVICE_HMAC_SECRET-value",
            "REPLACE_WITH_REAL_CA_CERTIFICATE",
        ):
            self.assertIn(placeholder, self.example_secrets)
        self.assertNotIn("setInsecure()", self.example_secrets)

    def test_device_secrets_file_is_gitignored(self):
        self.assertIn("firmware/**/secrets.h", self.gitignore)


if __name__ == "__main__":
    unittest.main()
