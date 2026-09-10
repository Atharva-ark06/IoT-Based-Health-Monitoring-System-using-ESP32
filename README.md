# 🩺 IoT-Based Health Monitoring System using ESP32

<div align="center">

### 📡 Real-Time Health Monitoring with IoT

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

## 🏗️ System Workflow

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

## 📁 Project Structure

```text
IoT-Based-Health-Monitoring-System-using-ESP32/
│
├── 📂 health/
│   ├── 📄 sensor_dashboard.html
│   └── 📄 ESP32_Health_Monitoring.ino
│
├── 📂 PBL Reports & Documentation/
│   └── 📄 Project Report.pdf
│
├── 📂 Project Presentations/
│   └── 📄 IoT Health Monitoring Presentation.pptx
│
└── 📄 README.md
```

---

## 🚀 Getting Started

```bash
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
cd IoT-Based-Health-Monitoring-System-using-ESP32
```

1. Open the ESP32 code in **Arduino IDE**.
2. Install the required ESP32 board package and libraries.
3. Connect the sensors and add your Wi-Fi credentials.
4. Select the ESP32 board and COM port.
5. Upload the code and monitor the readings.

> 🔐 Never upload Wi-Fi passwords, API keys, or private credentials to GitHub.

---

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
