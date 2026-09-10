# 🩺 IoT-Based Health Monitoring System using ESP32

<div align="center">

### 📡 Smart • Connected • Real-Time Health Monitoring

An **IoT-based health monitoring prototype** using ESP32 to collect sensor data, process it in real time, and transmit it through Wi-Fi for monitoring and cloud logging.

<br/>

<img src="https://img.shields.io/badge/ESP32-IoT-0066FF?style=for-the-badge&logo=espressif&logoColor=white"/>
<img src="https://img.shields.io/badge/Arduino-IDE-00979D?style=for-the-badge&logo=arduino&logoColor=white"/>
<img src="https://img.shields.io/badge/C%2FC%2B%2B-Embedded-00599C?style=for-the-badge&logo=cplusplus&logoColor=white"/>
<img src="https://img.shields.io/badge/Healthcare-IoT-E63946?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Wi--Fi-Connected-00A67E?style=for-the-badge&logo=wifi"/>

</div>

---

## 🧠 About

This project uses an **ESP32** to collect health-related sensor data and transmit it wirelessly over **Wi-Fi**. The data can be visualized through a web dashboard and logged using cloud-based services.

### ✨ Features

* ❤️ Heart Rate Monitoring
* 🌡️ Temperature Monitoring using DHT11
* 📡 Wi-Fi Connectivity
* 📊 Real-Time Dashboard
* ☁️ Cloud Data Logging
* ⚡ ESP32-Based Processing

---

## 🏗️ System Workflow

```text
🌡️ DHT11 ─────┐
               │
❤️ Heart Rate ─┼──► ESP32 ──► Wi-Fi ──► Cloud
               │                         │
               └─────────────────────────▼
                                   📊 Dashboard
```

---

## 🔧 Hardware

| Component            | Purpose                |
| -------------------- | ---------------------- |
| 🟦 ESP32             | Main controller        |
| 🌡️ DHT11            | Temperature sensing    |
| ❤️ Heart Rate Sensor | Heart-rate measurement |
| 🔌 Jumper Wires      | Connections            |
| 🧱 Breadboard        | Prototyping            |

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
│   └── 📄 sensor_dashboard.html
│
├── 📂 PBL Reports & Documentation/
│   └── 📄 Project Reports
│
├── 📂 Project Presentations/
│   └── 📄 Project PPTs
│
├── 📄 README.md
│
└── 📄 Other Project Files
```

---

## 🚀 Getting Started

```bash
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
cd IoT-Based-Health-Monitoring-System-using-ESP32
```

1. Open the ESP32 source code in **Arduino IDE**.
2. Install the required ESP32 board package and libraries.
3. Connect the sensors to the ESP32.
4. Add your Wi-Fi credentials.
5. Select the ESP32 board and COM port.
6. Upload the code.
7. Open the dashboard to monitor readings.

> 🔐 Never upload Wi-Fi passwords, API keys, or private credentials to GitHub.

---

## 🔮 Future Scope

* 📱 Mobile Application
* 🤖 AI-Based Health Anomaly Detection
* 🚨 Emergency Alerts
* 📈 Historical Health Analytics
* 🔐 Secure Data Transmission
* ☁️ Advanced Cloud Integration

---

## ⚠️ Disclaimer

This is an **academic IoT prototype** created for educational purposes. The sensor readings should not be considered a medical diagnosis or a replacement for professional medical equipment.

---

## 👨‍💻 Author

<div align="center">

### **Atharva Kulkarni**

[![GitHub](https://img.shields.io/badge/GitHub-Atharva--ark06-181717?style=for-the-badge\&logo=github)](https://github.com/Atharva-ark06)

<br/>

⭐ **If you found this project interesting, consider giving it a star!**

**ESP32 × IoT × Healthcare 🚀**

</div>
