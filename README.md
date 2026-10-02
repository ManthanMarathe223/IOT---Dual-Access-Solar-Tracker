# IoT-Based Smart Dual-Axis Solar Tracking and Energy Monitoring System

<img width="1510" height="856" alt="image" src="https://github.com/user-attachments/assets/bc91ce9d-4a64-4e98-8fcf-2d3c2af7e901" />


A low-cost ESP32-based solar tracker that uses four LDR sensors to detect the stronger light direction, two servo motors to move the panel on two axes, and an IoT dashboard to monitor sensor and energy-related data.

This repository contains the **Phase 1 IoT prototype**. The machine-learning prediction layer is intentionally kept for a later phase.

## Project Overview

The system combines three main functions:

1. **Dual-axis solar tracking** using four LDR sensors and two servo motors.
2. **Energy/environment monitoring** using simulated voltage and current inputs plus a DS18B20 temperature sensor.
3. **IoT monitoring** using ESP32 Wi-Fi and ThingSpeak.

The project follows the planned architecture:

```text
Sunlight
   ↓
4 LDR Sensors
   ↓
ESP32
   ├── Compare light levels
   │      ↓
   │   2 Servo Motors
   │      ↓
   │   Panel movement
   │
   └── Read monitoring values
          ↓
       Wi-Fi
          ↓
      ThingSpeak
          ↓
       Dashboard
```

## Current Project Status

### Completed

- ESP32 DevKit-based Wokwi simulation
- Four-direction LDR sensing
- Horizontal servo control
- Vertical servo control
- LDR tolerance to reduce unnecessary movement
- Servo angle limiting between 0° and 180°
- DS18B20 temperature monitoring
- Simulated voltage input using a potentiometer
- Simulated current input using a potentiometer
- Power calculation using `Power = Voltage × Current`
- Wi-Fi connectivity through Wokwi-GUEST
- ThingSpeak data upload
- ThingSpeak time-series dashboard

### Planned Later

- Collection/cleaning of historical data
- Machine-learning regression model
- Predicted-vs-actual power graph
- Future prediction/anomaly features
- Replacement of simulated voltage/current inputs with physical electrical sensors in the hardware prototype

The AI extension described in the project concept uses historical voltage, current, temperature and time-related data to predict future solar power. That part is outside the current Phase 1 implementation.

## Hardware / Simulation Components

### Main controller

- ESP32 DevKit v1 / ESP32 Dev Module

### Tracking

- 4 × Wokwi photoresistor (LDR) modules
- 2 × servo motors

### Monitoring

- 1 × DS18B20 temperature sensor
- 1 × potentiometer for simulated voltage
- 1 × potentiometer for simulated current

### IoT

- Wi-Fi
- ThingSpeak

> **Simulation note:** The voltage and current potentiometers are only used to simulate electrical measurements in Wokwi. They are not replacements for a real solar voltage/current sensor in the physical prototype.

## Pin Configuration

The current project uses the following ESP32 pins:

| Component | ESP32 Pin | Purpose |
|---|---:|---|
| Left LDR AO | GPIO 36 | Left light level |
| Right LDR AO | GPIO 35 | Right light level |
| Top LDR AO | GPIO 34 | Top light level |
| Bottom LDR AO | GPIO 33 | Bottom light level |
| Horizontal Servo signal | GPIO 18 | Left/right movement |
| Vertical Servo signal | GPIO 19 | Up/down movement |
| DS18B20 data | GPIO 25 | Temperature |
| Voltage potentiometer SIG | GPIO 32 | Simulated voltage |
| Current potentiometer SIG | GPIO 39 / VN | Simulated current |

### LDR power connections

```text
All LDR VCC → ESP32 3.3V
All LDR GND → ESP32 GND
Use AO for analog readings
DO is not used
```

### Servo connections

```text
Horizontal servo signal → GPIO 18
Vertical servo signal   → GPIO 19
Servo VCC               → 5V/VIN in the simulation
Servo GND               → Common GND
```

### Added monitoring sensors

```text
DS18B20 VCC → 3.3V
DS18B20 GND → GND
DS18B20 DATA → GPIO 25

Voltage potentiometer SIG → GPIO 32
Current potentiometer SIG → GPIO 39 (VN)
```

## Tracking Logic

The tracker continuously reads the four LDR values.

```text
Read Left and Right
        ↓
Compare their readings
        ↓
Move horizontal servo toward the brighter side

Read Top and Bottom
        ↓
Compare their readings
        ↓
Move vertical servo toward the brighter side
```

A tolerance value is used so the servos do not react to very small differences. The servo angle is constrained between 0° and 180°.

For the Wokwi photoresistor modules used in this project, the implemented logic treats the **lower ADC reading as stronger illumination**.

## Monitoring Logic

### Voltage

The voltage potentiometer is mapped to a simulated range of:

```text
0 to 5 V
```

### Current

The current potentiometer is mapped to a simulated range of:

```text
0 to 2 A
```

### Power

Power is calculated in software:

```text
Power = Voltage × Current
```

### Temperature

The DS18B20 provides the temperature reading in °C.

## ThingSpeak Dashboard

Create one ThingSpeak channel and use these 8 fields:

| Field | Name | Data |
|---|---|---|
| 1 | Left LDR | ADC reading |
| 2 | Right LDR | ADC reading |
| 3 | Top LDR | ADC reading |
| 4 | Bottom LDR | ADC reading |
| 5 | Voltage | V |
| 6 | Current | A |
| 7 | Power | W |
| 8 | Temperature | °C |

The servo angles remain available in the Serial Monitor. The ThingSpeak fields are focused on tracking sensor readings and solar/condition monitoring.

## ThingSpeak Setup

1. Sign in to ThingSpeak.
2. Create a new channel named something such as **Smart Solar Tracker**.
3. Enable the 8 fields listed above.
4. Open **API Keys** for the channel.
5. Copy the **Write API Key**.
6. Put the key into `src/sketch.ino` locally.
7. Do **not** commit the real key to GitHub.

In the code, replace:

```cpp
const char* THINGSPEAK_WRITE_API_KEY = "YOUR_THINGSPEAK_WRITE_API_KEY";
```

with your local Write API key.

## Running with PlatformIO + Wokwi

### Project structure

```text
project-root/
├── src/
│   └── sketch.ino
├── diagram.json
├── libraries.txt
├── platformio.ini
└── wokwi.toml
```

### PlatformIO dependencies

The project requires these libraries:

```text
ESP32Servo
OneWire
DallasTemperature
```

For PlatformIO, add them to `platformio.ini` through `lib_deps` if they are not already present.

Example:

```ini
[env:esp32dev]
platform = espressif32
board = esp32dev
framework = arduino

lib_deps =
    madhephaestus/ESP32Servo
    paulstoffregen/OneWire
    milesburton/DallasTemperature
```

### Build

From the VS Code PlatformIO terminal:

```bash
platformio run
```

A successful build should create:

```text
.pio/build/esp32dev/firmware.bin
.pio/build/esp32dev/firmware.elf
```

### Start Wokwi

After the PlatformIO build succeeds, start the Wokwi simulator from the Wokwi extension in VS Code.

## Testing the Simulation

### LDR tracking test

Change the illumination of one LDR in Wokwi.

Expected behavior:

```text
Left brighter  → horizontal servo reacts
Right brighter → horizontal servo reacts
Top brighter   → vertical servo reacts
Bottom brighter→ vertical servo reacts
```

The exact ADC numbers depend on the simulated illumination.

### Voltage/current test

Rotate the voltage potentiometer and observe:

```text
Voltage changes
Power changes
```

Rotate the current potentiometer and observe:

```text
Current changes
Power changes
```

### Temperature test

Change the DS18B20 temperature in Wokwi and verify that the temperature changes in:

- Serial Monitor
- ThingSpeak Field 8

### ThingSpeak upload test

A successful upload should produce:

```text
Sending data to ThingSpeak...
ThingSpeak Response: 200
```

## Example Serial Output

```text
SMART SOLAR TRACKER STARTED
--------------------------------
Left LDR: 2100
Right LDR: 1000
Top LDR: 1500
Bottom LDR: 1900
Horizontal Servo: 92 deg
Vertical Servo: 88 deg
Voltage: 2.54 V
Current: 0.94 A
Power: 2.39 W
Temperature: 26.87 C
Sending data to ThingSpeak...
ThingSpeak Response: 200
ThingSpeak Entry ID: 17
```

## Dashboard Presentation

A project-ready ThingSpeak dashboard can contain:

```text
LDR Tracking
├── Left LDR
├── Right LDR
├── Top LDR
└── Bottom LDR

Energy / Condition Monitoring
├── Voltage
├── Current
├── Power
└── Temperature
```

Use time-series charts for trends and numeric/gauge widgets for the current voltage, current, power and temperature values.

## Why These Measurements Matter

The LDR readings show how the four sensor positions compare, which demonstrates the tracking decision.

Voltage, current and calculated power provide a simple view of simulated energy production.

Temperature provides an environmental/panel-condition measurement.

Together, these values make it possible to monitor the tracker remotely through ThingSpeak.

## Phase 2: Machine Learning Extension

The next project stage can reuse the data produced by this system.

Suggested pipeline:

```text
Historical ThingSpeak / collected data
                ↓
          Data preparation
                ↓
       ML regression model
                ↓
         Power prediction
                ↓
      Actual vs Predicted graph
```

The current project intentionally stops before this ML layer.

## Reference Projects / Sources

The project was designed by combining the useful parts of several existing implementations and references:

- **Arduino Solar Tracker (ESP32)** — useful reference for 4-LDR dual-axis tracking logic and tolerance-based servo movement.
- **IoT Dual-Axis Solar Tracker (ESP32 + Blynk)** — useful reference for combining tracking with electrical/environmental monitoring and IoT.
- **Circuit Digest – ESP32 Solar Power Monitoring with ThingSpeak** — useful reference for voltage/current/power/temperature monitoring and ThingSpeak visualization.
- **Development of Dual Axis Solar Tracker with IoT Monitoring (UniKL BMI)** — useful academic reference for overall architecture, tracking, monitoring and dashboard design.

See the project research notes for the collected links and detailed comparison of these references.

## Project Context

The project was developed as an IoT mini-project focused on **SDG 7 – Affordable and Clean Energy**. The intended system is a low-cost automatic solar tracker with real-time monitoring and a later AI-based prediction extension.

## Team

- Yogya Suryawanshi
- Manthan Marathe
- Pruthviraj Suryawanshi

## License / Usage

This repository is an academic/student mini-project. Third-party libraries and reference projects remain subject to their respective licenses. Check the original repository/license before reusing external code beyond this project.
