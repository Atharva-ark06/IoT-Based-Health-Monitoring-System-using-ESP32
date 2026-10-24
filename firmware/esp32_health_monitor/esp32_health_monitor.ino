/*
 * ESP32 health-monitoring firmware integration scaffold.
 *
 * Libraries: Adafruit DHT sensor library, ArduinoJson 6.x.
 * Hardware wiring and heart-rate sensor adapter must be verified for your
 * exact board/sensor model before use. No medical-grade accuracy is claimed.
 */
#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <DHT.h>
#include <ArduinoJson.h>
#include <mbedtls/md.h>
#include <time.h>
#include <math.h>
#include "secrets.h"

#ifndef DHT_PIN
#define DHT_PIN 4
#endif
#ifndef DHT_TYPE
#define DHT_TYPE DHT11
#endif
#ifndef HEART_RATE_PIN
#define HEART_RATE_PIN 34
#endif
#ifndef SAMPLE_INTERVAL_MS
#define SAMPLE_INTERVAL_MS 15000
#endif

DHT dht(DHT_PIN, DHT_TYPE);
WiFiClientSecure tlsClient;
unsigned long lastSample = 0;

String hexEncode(const uint8_t *bytes, size_t length) {
  static const char alphabet[] = "0123456789abcdef";
  String result;
  result.reserve(length * 2);
  for (size_t i = 0; i < length; ++i) {
    result += alphabet[bytes[i] >> 4];
    result += alphabet[bytes[i] & 0x0F];
  }
  return result;
}

String newNonce() {
  uint8_t bytes[16];
  for (size_t i = 0; i < sizeof(bytes); i += 4) {
    uint32_t value = esp_random();
    memcpy(bytes + i, &value, 4);
  }
  return hexEncode(bytes, sizeof(bytes));
}

String utcTimestamp(time_t now) {
  struct tm utcTime;
  gmtime_r(&now, &utcTime);
  char buffer[25];
  strftime(buffer, sizeof(buffer), "%Y-%m-%dT%H:%M:%SZ", &utcTime);
  return String(buffer);
}

String hmacSha256Hex(const String &message) {
  uint8_t digest[32];
  const mbedtls_md_info_t *info = mbedtls_md_info_from_type(MBEDTLS_MD_SHA256);
  if (info == nullptr ||
      mbedtls_md_hmac(info,
                      reinterpret_cast<const unsigned char *>(DEVICE_HMAC_SECRET),
                      strlen(DEVICE_HMAC_SECRET),
                      reinterpret_cast<const unsigned char *>(message.c_str()),
                      message.length(), digest) != 0) {
    return String();
  }
  return hexEncode(digest, sizeof(digest));
}

bool connectWiFi() {
  if (WiFi.status() == WL_CONNECTED) return true;
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  const unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 20000) {
    delay(250);
  }
  return WiFi.status() == WL_CONNECTED;
}

bool synchronizeClock() {
  configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  const unsigned long started = millis();
  while (time(nullptr) < 1700000000 && millis() - started < 20000) {
    delay(250);
  }
  return time(nullptr) >= 1700000000;
}

/*
 * TODO: replace this adapter with the verified algorithm/API for your actual
 * heart-rate sensor (for example, the exact MAX30102 library and sampling
 * routine). A raw analog pulse sensor value is NOT a BPM measurement.
 * NAN makes the firmware fail closed until a real BPM adapter is implemented.
 */
float readHeartRateBpm() {
  (void)analogRead(HEART_RATE_PIN);
  return NAN;
}

bool submitReading(float temperatureC, int bpm, time_t now) {
  const String timestampHeader = String((long)now);
  const String nonce = newNonce();
  const String readingTimestamp = utcTimestamp(now);

  StaticJsonDocument<256> document;
  document["device_id"] = DEVICE_ID;
  document["timestamp"] = readingTimestamp;
  document["temperature"] = roundf(temperatureC * 10.0f) / 10.0f;
  document["bpm"] = bpm;
  String body;
  serializeJson(document, body);

  // The API signs: unix_timestamp + "." + nonce + "." + exact JSON body bytes.
  const String signingMessage = timestampHeader + "." + nonce + "." + body;
  const String signature = hmacSha256Hex(signingMessage);
  if (signature.isEmpty()) return false;

  HTTPClient http;
  if (!http.begin(tlsClient, API_URL)) return false;
  http.setConnectTimeout(5000);
  http.setTimeout(5000);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Timestamp", timestampHeader);
  http.addHeader("X-Device-Nonce", nonce);
  http.addHeader("X-Device-Signature", signature);
  const int status = http.POST(reinterpret_cast<const uint8_t *>(body.c_str()), body.length());
  http.end();

  // Do not log sensor values, secrets, signatures, or request bodies.
  return status == 201;
}

void setup() {
  Serial.begin(115200);
  dht.begin();
  // Never use setInsecure(): certificate validation must remain enabled.
  tlsClient.setCACert(ROOT_CA_CERT);
  if (!connectWiFi()) Serial.println("Wi-Fi unavailable; will retry.");
  if (WiFi.status() == WL_CONNECTED && !synchronizeClock()) {
    Serial.println("Clock synchronization failed; signed requests are disabled.");
  }
}

void loop() {
  if (millis() - lastSample < SAMPLE_INTERVAL_MS) {
    delay(100);
    return;
  }
  lastSample = millis();

  if (!connectWiFi() || !synchronizeClock()) {
    Serial.println("Network/time unavailable; sample skipped.");
    return;
  }

  const float temperatureC = dht.readTemperature();
  const float bpmValue = readHeartRateBpm();
  if (!isfinite(temperatureC) || !isfinite(bpmValue) ||
      temperatureC < -20 || temperatureC > 80 || bpmValue < 20 || bpmValue > 250) {
    Serial.println("Sensor adapter returned an invalid sample; not uploaded.");
    return;
  }

  if (!submitReading(temperatureC, (int)lroundf(bpmValue), time(nullptr))) {
    Serial.println("Reading upload failed; will retry on a later sample.");
  } else {
    Serial.println("Reading accepted.");
  }
}
