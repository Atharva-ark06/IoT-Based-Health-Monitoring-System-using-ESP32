# 🩺 IoT-Based Health Monitoring System using ESP32

<div align="center">
  
###  📡 Real-Time Health Monitoring with IoT 

<img src="https://img.shields.io/badge/ESP32-IoT-0066FF?style=for-the-badge&logo=espressif&logoColor=white"/>
<img src="https://img.shields.io/badge/Arduino-IDE-00979D?style=for-the-badge&logo=arduino&logoColor=white"/>
<img src="https://img.shields.io/badge/C%2FC%2B%2B-Embedded-00599C?style=for-the-badge&logo=cplusplus&logoColor=white"/>
<img src="https://img.shields.io/badge/Healthcare-IoT-E63946?style=for-the-badge"/>

<br/><br/>

**An IoT-based health monitoring system that collects sensor data using ESP32 and enables real-time monitoring through Wi-Fi and a web dashboard.**

</div>

---

## 🧠 About

This project uses an **ESP32** to collect health-related sensor data, process it in real time, and transmit it over **Wi-Fi** for monitoring and cloud-based logging.

### ✨ Features

* ❤️ Heart Rate Monitoring
* 🌡️ Temperature Monitoring using DHT11
* 📡 Wi-Fi Connectivity
* 📊 Real-Time Web Dashboard
* ☁️ Cloud Data Logging
* ⚡ ESP32-Based Processing

---

## 🏗️  System Workflow

```text
🌡️ DHT11 ──────────┐
                    │
❤️ Heart Rate ──────┼──► ⚡ ESP32 ──► 📡 Wi-Fi ──► ☁️ Cloud
                    │                              │
                    └──────────────────────────────▼
                                           📊 Dashboard
```

---

## 🔧 Hardware

| Component            | Purpose                |
| -------------------- | ---------------------- |
| 🟦 ESP32             | Main Controller        |
| 🌡️ DHT11            | Temperature Monitoring |
| ❤️ Heart Rate Sensor | Heart Rate Measurement |
| 🔌 Jumper Wires      | Connections            |
| 🧱 Breadboard        | Prototyping            |
| 🔋 USB Cable         | Power & Programming    |

---

## 💻 Tech Stack

**Hardware:** ESP32, DHT11, Heart Rate Sensor
**Programming:** C/C++, Arduino IDE
**Web:** HTML, CSS, JavaScript
**Communication:** Wi-Fi
**Cloud:** Google Sheets / Cloud Services

---

## 📁 Repository Structure

```text
├── health/
│   └── sensor_dashboard.html
├── tests/
│   └── dashboard-security.test.mjs
├── README.md
└── SECURITY.md
```

Project reports and presentations are also stored at the repository root. The ESP32 firmware file mentioned in earlier documentation is not currently present in this repository.

---

## 🚀 Getting Started

# clone the repo
```bash
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
```
# change directory 
```
cd IoT-Based-Health-Monitoring-System-using-ESP32
```

1. Open `health/sensor_dashboard.html` in a browser or serve it from a local/static web server.
2. Configure the CSV source by adding a `sensor-data-url` meta tag inside the HTML `<head>`. For example:

   ```html
   <meta name="sensor-data-url" content="https://example.com/readings.csv">
   ```

3. Replace the example URL with an HTTPS CSV endpoint that is intentionally accessible to the dashboard's intended audience. The URL is public to visitors; do not include credentials or access tokens.
4. The CSV should provide a timestamp column and temperature/BPM columns. The dashboard supports common header names such as `Timestamp`, `Temperature`, and `BPM`, as well as the existing positional columns.

> **Security:** Do not publish Wi-Fi passwords, API keys, bearer tokens, or private credentials. Avoid connecting real health readings to a public spreadsheet. Read [SECURITY.md](SECURITY.md) before configuring a source.

> **Firmware note:** The repository currently does not include an `.ino` firmware file, so the ESP32 hardware upload steps cannot be reproduced from the checked-in source alone.

---

## 🔐 Security and privacy

- The dashboard no longer embeds a specific Google Sheets export URL.
- Remote CSV loading requires HTTPS and omits browser credentials and referrer information.
- Imported timestamps are escaped before being rendered in the table.
- Temperature/BPM correlation is calculated only from paired readings from the same rows.
- Basic regression checks are available with Node.js: `node --test tests/dashboard-security.test.mjs`.

These changes improve browser-side handling but do not provide device authentication, server-side access control, or a secure ingestion API. Do not treat this prototype as production-ready for personal health data. See [SECURITY.md](SECURITY.md) for the threat model and deployment guidance.

## 🔮 Future Scope

* 🤖 AI-Based Health Anomaly Detection
* 🚨 Emergency Alerts
* 📱 Mobile Application
* 📈 Historical Health Analytics
* 🔐 Secure Data Transmission

---

## ⚠️ Disclaimer

This is an **academic IoT prototype** for educational purposes. The readings should not be considered a medical diagnosis or a replacement for professional medical equipment.

---

<div align="center">

## 👨‍💻 Author

### **Atharva Kulkarni**

[![GitHub](https://img.shields.io/badge/GitHub-Atharva--ark06-181717?style=for-the-badge\&logo=github)](https://github.com/Atharva-ark06)

<br/>

⭐ **Star the repository if you found it useful!**

### `ESP32 × IoT × Healthcare 🚀`

</div>
