#  IoT-Based Health Monitoring System using ESP32

<div align="center">

<img src="https://img.shields.io/badge/ESP32-IoT-blue?style=for-the-badge&logo=espressif" />
<img src="https://img.shields.io/badge/Arduino-IDE-00979D?style=for-the-badge&logo=arduino" />
<img src="https://img.shields.io/badge/Healthcare-IoT-red?style=for-the-badge" />
<img src="https://img.shields.io/badge/C%2FC%2B%2B-Embedded-orange?style=for-the-badge&logo=cplusplus" />

**A smart IoT-based system for real-time health monitoring using ESP32.**

</div> 
 
--- 

## 🌐 About
#


This project uses an **ESP32** to collect health data from sensors and transmit it wirelessly over **Wi-Fi**. The collected data can be monitored through a web dashboard and stored using cloud-based services.

### ✨ Features

* ❤️ Heart Rate Monitoring
* 🌡️ Temperature Monitoring using DHT11
* 📡 Wi-Fi Connectivity
* 📊 Real-Time Dashboard
* ☁️ Cloud Data Logging
* ⚡ ESP32-based Processing

---

## 🧠 System Workflow

```text
🌡️ DHT11 ─────┐
               ├──► ESP32 ──► Wi-Fi ──► Cloud
❤️ Heart Rate ─┘                       │
                                       ▼
                                📊 Web Dashboard
```

---

## 🔧 Hardware Required

| Component            | Purpose                |
| -------------------- | ---------------------- |
| 🟦 ESP32             | Main controller        |
| 🌡️ DHT11            | Temperature sensing    |
| ❤️ Heart Rate Sensor | Heart-rate measurement |
| 🔌 Jumper Wires      | Connections            |
| 🧱 Breadboard        | Prototyping            |
| 🔋 USB Cable         | Power & programming    |

---

## 💻 Technologies

**Hardware:** ESP32, DHT11, Heart Rate Sensor
**Programming:** C/C++, Arduino IDE
**Communication:** Wi-Fi
**Dashboard:** HTML, CSS, JavaScript
**Cloud:** Google Sheets / Cloud Services

---

## 🚀 Getting Started

### Clone

```bash
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
cd IoT-Based-Health-Monitoring-System-using-ESP32
```

### Setup

1. Open the ESP32 source code in **Arduino IDE**.
2. Install the required ESP32 board package and libraries.
3. Connect the sensors to the ESP32.
4. Add your Wi-Fi credentials.
5. Select your ESP32 board and COM port.
6. Upload the code.
7. Open the dashboard to monitor the readings.

> 🔐 Never upload Wi-Fi passwords, API keys, or private credentials to GitHub.

---

## 📁 Project Structure

```text
IoT-Based-Health-Monitoring-System-using-ESP32/
│
├── health/
│   └── sensor_dashboard.html
│
├── PBL Reports & Documentation
├── Project Presentations
└── README.md
```

---

## 🔮 Future Scope

* 📱 Mobile Application
* 🤖 AI-based health anomaly detection
* 🚨 Emergency alerts
* 📈 Historical health analytics
* 🔐 Secure data transmission
* ☁️ Advanced cloud integration

---

## ⚠️ Disclaimer

This is an **academic IoT prototype** for educational purposes. Sensor readings should not be considered a medical diagnosis or a replacement for professional medical equipment.

---

## 👨‍💻 Author

**Atharva Kulkarni**

[GitHub](https://github.com/Atharva-ark06)

---

<div align="center">

⭐ **Star the repository if you found it useful!**

**ESP32 × IoT × Healthcare**

</div>
