# 🩺 IoT-Based Health Monitoring System using ESP32

<div align="center">

<img src="https://img.shields.io/badge/ESP32-IoT-blue?style=for-the-badge&logo=espressif" />
<img src="https://img.shields.io/badge/Arduino-IDE-00979D?style=for-the-badge&logo=arduino" />
<img src="https://img.shields.io/badge/C%2FC%2B%2B-Embedded-orange?style=for-the-badge&logo=cplusplus" />
<img src="https://img.shields.io/badge/IoT-Healthcare-red?style=for-the-badge" />
<img src="https://img.shields.io/badge/WiFi-Connected-success?style=for-the-badge&logo=wifi" />

### 🌐 Real-Time • Wireless • Connected • Smart Healthcare

**An IoT-enabled health monitoring system built around ESP32 for collecting and monitoring vital health parameters in real time.**

</div>

---

## 📌 Overview

The **IoT-Based Health Monitoring System** is a smart healthcare solution designed to continuously collect health-related data using sensors connected to an **ESP32 microcontroller**.

The system captures vital information such as **body temperature and heart rate**, processes the readings on the ESP32, and transmits the collected data wirelessly through **Wi-Fi**.

A web-based dashboard is also included for presenting sensor information in an easy-to-understand format.

> 💡 **Goal:** Build a low-cost, connected health-monitoring prototype that demonstrates how IoT can be applied to real-time healthcare data collection.

---

## ✨ Key Features

| Feature                        | Description                                                   |
| ------------------------------ | ------------------------------------------------------------- |
| 🩺 **Health Monitoring**       | Collects real-time health-related sensor readings             |
| 🌡️ **Temperature Monitoring** | Uses DHT11 for temperature-related measurements               |
| ❤️ **Heart Rate Monitoring**   | Captures heart-rate readings through a heart-rate sensor      |
| 📡 **Wireless Communication**  | ESP32 transmits collected data through Wi-Fi                  |
| 🌐 **Web Dashboard**           | Displays sensor information through a browser-based interface |
| ☁️ **Cloud Logging**           | Supports sending/logging readings to cloud-based services     |
| ⚡ **Real-Time Processing**     | ESP32 processes sensor readings locally                       |
| 🔌 **Low-Cost Hardware**       | Built using easily available IoT components                   |

---

## 🧠 System Architecture

```text
                 ┌──────────────────────┐
                 │      HEALTH DATA     │
                 └──────────┬───────────┘
                            │
                            ▼
              ┌─────────────────────────┐
              │     SENSOR LAYER        │
              │                         │
              │  🌡️ DHT11              │
              │  ❤️ Heart Rate Sensor   │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │        ESP32            │
              │                         │
              │  • Sensor Processing    │
              │  • Data Collection      │
              │  • Wi-Fi Communication  │
              └────────────┬────────────┘
                           │
                           │ Wi-Fi
                           ▼
              ┌─────────────────────────┐
              │     CLOUD / SERVER      │
              │                         │
              │  • Data Logging         │
              │  • Remote Access        │
              └────────────┬────────────┘
                           │
                           ▼
              ┌─────────────────────────┐
              │    WEB DASHBOARD        │
              │                         │
              │  📊 Health Readings     │
              │  📈 Sensor Data         │
              └─────────────────────────┘
```

---

# 🔧 Hardware Requirements

The following components are required to reproduce the project:

### 🧩 Main Components

* 🟦 **ESP32 Development Board**
* 🌡️ **DHT11 Temperature & Humidity Sensor**
* ❤️ **Heart Rate Sensor**
* 🔌 Breadboard
* 🔗 Jumper Wires
* 🔋 USB Power Supply / USB Cable
* 💻 Computer for programming

### Optional Components

Depending on the implementation, the project can be extended with:

* MAX30100 / MAX30102
* OLED / LCD Display
* Buzzer
* LED indicators
* Additional temperature sensors
* Motion / fall detection sensors

---

# 💻 Software & Technologies

### Programming

* **C/C++**
* **Arduino Framework**
* **Arduino IDE**

### Hardware

* **ESP32**
* **DHT11**
* **Heart Rate Sensor**

### Communication

* **Wi-Fi**
* **HTTP / Web-based communication**

### Dashboard

* **HTML**
* **CSS**
* **JavaScript**

### Data & Cloud

* **Google Sheets / Cloud Dashboard**
* Real-time sensor data logging

---

# ⚙️ How It Works

### 1️⃣ Sensor Initialization

The ESP32 initializes the connected sensors when the system starts.

### 2️⃣ Data Collection

Sensors continuously collect health-related readings such as:

```text
Temperature
     +
Heart Rate
     ↓
Sensor Data
```

### 3️⃣ Data Processing

The ESP32 reads and processes the incoming sensor values.

```text
Sensor
   ↓
ESP32
   ↓
Process Reading
   ↓
Prepare Data
```

### 4️⃣ Wireless Transmission

The ESP32 connects to a Wi-Fi network and transmits the collected information.

```text
ESP32
  │
  │ Wi-Fi
  ▼
Cloud / Server
```

### 5️⃣ Dashboard Visualization

The transmitted information can then be displayed through the project's web dashboard.

```text
             HEALTH DASHBOARD
        ┌─────────────────────────┐
        │ 🌡️ Temperature           │
        │ ❤️ Heart Rate            │
        │ 📡 Connection Status     │
        │ 📊 Sensor Information    │
        └─────────────────────────┘
```

---

# 🌐 Web Dashboard

The repository includes a dedicated dashboard:

```text
health/
└── sensor_dashboard.html
```

The dashboard provides a browser-based interface for presenting sensor information.

This creates a simple IoT pipeline:

```text
Sensors
   ↓
ESP32
   ↓
Wi-Fi
   ↓
Cloud / Data Service
   ↓
Web Dashboard
```

---

# 🔌 ESP32 Pin Connections

> ⚠️ Pin assignments may vary depending on the exact sensor modules and firmware implementation.

A typical configuration can be structured as:

| Component         | ESP32 Connection                         |
| ----------------- | ---------------------------------------- |
| DHT11 Data        | Digital GPIO                             |
| Heart Rate Sensor | Analog GPIO                              |
| Sensor VCC        | 3.3V / according to module specification |
| Sensor GND        | GND                                      |
| USB               | ESP32 Power & Programming                |

Always verify the pin configuration used by the source code before wiring the physical circuit.

---

# 🚀 Getting Started

## 1. Clone the Repository

```bash
git clone https://github.com/Atharva-ark06/IoT-Based-Health-Monitoring-System-using-ESP32.git
```

Navigate into the project:

```bash
cd IoT-Based-Health-Monitoring-System-using-ESP32
```

---

## 2. Install Arduino IDE

Install the **Arduino IDE** and configure it for ESP32 development.

Then install the ESP32 board package through:

```text
Arduino IDE
   ↓
Boards Manager
   ↓
ESP32
   ↓
Install
```

---

## 3. Connect the Hardware

Connect:

```text
ESP32
 ├── DHT11
 ├── Heart Rate Sensor
 ├── GND
 └── 3.3V / Power
```

Use the wiring configuration required by the firmware in the project.

---

## 4. Configure Wi-Fi

Update the Wi-Fi credentials in the ESP32 source code:

```cpp
const char* ssid = "YOUR_WIFI_NAME";
const char* password = "YOUR_WIFI_PASSWORD";
```

> 🔐 **Never commit your real Wi-Fi password, API keys, tokens, or other credentials to GitHub.**

---

## 5. Select ESP32 Board

In Arduino IDE:

```text
Tools
 ↓
Board
 ↓
ESP32
 ↓
ESP32 Dev Module
```

Select the correct COM port.

---

## 6. Upload the Firmware

Connect the ESP32 through USB and upload the program.

After successful uploading:

```text
ESP32
  ↓
Initialize Sensors
  ↓
Connect to Wi-Fi
  ↓
Collect Health Data
  ↓
Transmit Data
  ↓
Dashboard / Cloud
```

---

# 📊 Data Flow

```text
┌───────────────┐
│    DHT11      │
│ Temperature   │
└───────┬───────┘
        │
        │
┌───────▼────────┐
│ Heart Rate     │
│    Sensor      │
└───────┬────────┘
        │
        ▼
┌─────────────────┐
│      ESP32      │
│ Data Processing │
└────────┬────────┘
         │
         │ Wi-Fi
         ▼
┌─────────────────┐
│ Cloud / Server  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Web Dashboard   │
└─────────────────┘
```

---

# 📁 Project Structure

```text
IoT-Based-Health-Monitoring-System-using-ESP32/
│
├── health/
│   └── sensor_dashboard.html
│
├── Abstract-PBL (1).docx
├── Abstract-PBL (1).pdf
├── Abstract-PBL_.pdf
├── PBL_REVIEW_2 AuroraX.pptx
├── pbl FINIAL new 1.pptx
├── pbl FINIAL new.pptx
├── pbl FINIAL.pptx
├── pbl report auroraX.docx
│
└── README.md
```

The repository also contains supporting PBL documentation and presentation material.

---

# 🎯 Objectives

The project aims to:

* Develop an IoT-based healthcare monitoring prototype.
* Collect health data using electronic sensors.
* Process sensor readings using ESP32.
* Enable wireless transmission of health information.
* Provide a simple dashboard for monitoring.
* Demonstrate the application of IoT in healthcare.
* Explore cloud-based health-data logging.
* Create a foundation for future smart healthcare systems.

---

# 🏥 Potential Applications

This system can serve as a prototype for:

* 🏠 **Home Health Monitoring**
* 👴 **Elderly Care**
* 🏥 **Remote Patient Monitoring**
* 🚑 **Healthcare IoT Systems**
* 🌐 **Telemedicine Applications**
* 🧑‍⚕️ **Patient Observation Systems**
* 🏫 **Academic IoT Projects**
* 🔬 **Healthcare Research Prototypes**

Similar ESP32 healthcare architectures commonly combine sensor acquisition, wireless communication, and remote dashboards for real-time monitoring.

---

# 🔮 Future Enhancements

The system can be expanded significantly.

### 🤖 AI-Based Monitoring

Integrate machine learning models for:

* Abnormal heart-rate detection
* Health trend analysis
* Anomaly detection
* Predictive monitoring

### 📱 Mobile Application

Develop an Android/iOS application for:

```text
Patient
   ↓
ESP32
   ↓
Cloud
   ↓
Mobile App
   ↓
Doctor / Caregiver
```

### 🚨 Emergency Alerts

Add automatic alerts for abnormal readings:

```text
Normal
  │
  ▼
Continuous Monitoring
  │
  ▼
Abnormal Reading?
  │
 ┌┴──────────────┐
 YES             NO
 │                │
 ▼                ▼
Alert         Continue
Caregiver     Monitoring
```

### 🔐 Security

Future versions can include:

* HTTPS communication
* Authentication
* Encrypted data transmission
* Secure API endpoints
* Role-based access
* Protected patient information

### 📈 Advanced Analytics

Add:

* Historical graphs
* Daily health reports
* Weekly trends
* Threshold detection
* Patient profiles
* Multi-user monitoring

---

# ⚠️ Important Disclaimer

This project is an **academic/engineering prototype** intended for educational and research purposes.

The sensor readings and system output **should not be treated as medical diagnoses or a replacement for professional medical equipment or healthcare professionals**.

For real-world medical applications, appropriate calibration, validation, safety testing, regulatory compliance, and clinical evaluation would be required.

---

# 🧪 Learning Outcomes

Through this project, the following concepts can be explored:

```text
Embedded Systems
       +
IoT
       +
Sensors
       +
ESP32
       +
Wi-Fi Communication
       +
Cloud Data
       +
Web Development
       ↓
Smart Healthcare System
```

### Skills Demonstrated

* Embedded programming
* ESP32 development
* Sensor integration
* IoT architecture
* Wireless communication
* Web dashboard development
* Cloud data handling
* Hardware prototyping
* Real-time data processing

---

# 📚 Project Documentation

This repository also contains supporting academic material including:

* 📄 Project Abstract
* 📑 PBL Reports
* 📊 Project Presentations
* 📝 Supporting Documentation

These files provide additional information about the project's academic implementation and development process.

---

# 👨‍💻 Author

<div align="center">

## **Atharva Kulkarni**

Computer Science Engineering Student
IoT • AI/ML • Embedded Systems • Cybersecurity

**GitHub:** [Atharva-ark06](https://github.com/Atharva-ark06)

</div>

---

# ⭐ Support

If you found this project useful or interesting:

⭐ **Star the repository**

🍴 **Fork the project**

🐛 **Open an issue**

💡 **Suggest improvements**

---

<div align="center">

### 🩺 Building Smarter Healthcare with IoT

**ESP32 × Sensors × Wi-Fi × Cloud × Healthcare**

---

Made with ❤️ by **Atharva Kulkarni**

</div>
