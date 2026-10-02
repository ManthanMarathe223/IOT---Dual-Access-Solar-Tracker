#include <Arduino.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <ESP32Servo.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ============================================================
// Smart Solar Tracker - IoT Phase
// ESP32 + 4 LDR + 2 Servo + DS18B20 + 2 potentiometers
// ThingSpeak monitoring
// ============================================================

// ---------------------------
// Pin configuration
// ---------------------------
const int LDR_LEFT_PIN   = 36;
const int LDR_RIGHT_PIN  = 35;
const int LDR_TOP_PIN    = 34;
const int LDR_BOTTOM_PIN = 33;

const int HORIZONTAL_SERVO_PIN = 18;
const int VERTICAL_SERVO_PIN   = 19;

const int TEMPERATURE_PIN = 25;  // DS18B20 data pin
const int VOLTAGE_PIN     = 32;  // Potentiometer: simulated voltage
const int CURRENT_PIN     = 39;  // VN / GPIO39: simulated current

// ---------------------------
// Wi-Fi - Wokwi simulation
// ---------------------------
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASSWORD = "";

// ---------------------------
// ThingSpeak
// ---------------------------
// IMPORTANT: never commit your real Write API key to GitHub.
// Replace this value locally before running the project.
const char* THINGSPEAK_WRITE_API_KEY = "YOUR_THINGSPEAK_WRITE_API_KEY";
const char* THINGSPEAK_UPDATE_URL = "http://api.thingspeak.com/update";

// ThingSpeak free channels are commonly updated no faster than once
// every 15 seconds. We use 20 seconds here.
const unsigned long THINGSPEAK_INTERVAL_MS = 20000UL;

// ---------------------------
// Tracking settings
// ---------------------------
const int SERVO_MIN_ANGLE = 0;
const int SERVO_MAX_ANGLE = 180;
const int LDR_TOLERANCE = 50;
const int SERVO_STEP = 2;

// ---------------------------
// Servo state
// ---------------------------
Servo horizontalServo;
Servo verticalServo;

int horizontalAngle = 90;
int verticalAngle = 90;

// ---------------------------
// DS18B20
// ---------------------------
OneWire oneWire(TEMPERATURE_PIN);
DallasTemperature temperatureSensor(&oneWire);

unsigned long lastThingSpeakUpdate = 0;

// ============================================================
// Wi-Fi helper
// ============================================================
void connectToWiFi() {
  if (WiFi.status() == WL_CONNECTED) {
    return;
  }

  Serial.print("Connecting to WiFi");
  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD, 6);

  const unsigned long timeoutMs = 15000;
  const unsigned long start = millis();

  while (WiFi.status() != WL_CONNECTED && millis() - start < timeoutMs) {
    delay(500);
    Serial.print(".");
  }

  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("WiFi connection failed. Will retry later.");
  }
}

// ============================================================
// Solar tracking
// ============================================================
void updateTracking(int leftValue, int rightValue, int topValue, int bottomValue) {
  // The Wokwi photoresistor module used in this project produces a
  // lower analog reading for stronger illumination.

  const int horizontalDifference = leftValue - rightValue;

  if (abs(horizontalDifference) > LDR_TOLERANCE) {
    if (leftValue < rightValue) {
      // Left side is brighter.
      horizontalAngle -= SERVO_STEP;
    } else {
      // Right side is brighter.
      horizontalAngle += SERVO_STEP;
    }

    horizontalAngle = constrain(
      horizontalAngle,
      SERVO_MIN_ANGLE,
      SERVO_MAX_ANGLE
    );

    horizontalServo.write(horizontalAngle);
  }

  const int verticalDifference = topValue - bottomValue;

  if (abs(verticalDifference) > LDR_TOLERANCE) {
    if (topValue < bottomValue) {
      // Top side is brighter.
      verticalAngle += SERVO_STEP;
    } else {
      // Bottom side is brighter.
      verticalAngle -= SERVO_STEP;
    }

    verticalAngle = constrain(
      verticalAngle,
      SERVO_MIN_ANGLE,
      SERVO_MAX_ANGLE
    );

    verticalServo.write(verticalAngle);
  }
}

// ============================================================
// Read and map simulated electrical values
// ============================================================
float readSimulatedVoltage() {
  const int raw = analogRead(VOLTAGE_PIN);
  return (raw / 4095.0f) * 5.0f;
}

float readSimulatedCurrent() {
  const int raw = analogRead(CURRENT_PIN);
  return (raw / 4095.0f) * 2.0f;
}

// ============================================================
// Serial output
// ============================================================
void printReadings(
  int leftValue,
  int rightValue,
  int topValue,
  int bottomValue,
  float voltage,
  float current,
  float power,
  float temperatureC
) {
  Serial.println("--------------------------------");
  Serial.print("Left LDR: ");
  Serial.println(leftValue);

  Serial.print("Right LDR: ");
  Serial.println(rightValue);

  Serial.print("Top LDR: ");
  Serial.println(topValue);

  Serial.print("Bottom LDR: ");
  Serial.println(bottomValue);

  Serial.print("Horizontal Servo: ");
  Serial.print(horizontalAngle);
  Serial.println(" deg");

  Serial.print("Vertical Servo: ");
  Serial.print(verticalAngle);
  Serial.println(" deg");

  Serial.print("Voltage: ");
  Serial.print(voltage, 2);
  Serial.println(" V");

  Serial.print("Current: ");
  Serial.print(current, 2);
  Serial.println(" A");

  Serial.print("Power: ");
  Serial.print(power, 2);
  Serial.println(" W");

  Serial.print("Temperature: ");
  if (temperatureC == DEVICE_DISCONNECTED_C) {
    Serial.println("Sensor disconnected");
  } else {
    Serial.print(temperatureC, 2);
    Serial.println(" C");
  }
}

// ============================================================
// ThingSpeak upload
// ============================================================
bool sendToThingSpeak(
  int leftValue,
  int rightValue,
  int topValue,
  int bottomValue,
  float voltage,
  float current,
  float power,
  float temperatureC
) {
  if (WiFi.status() != WL_CONNECTED) {
    Serial.println("ThingSpeak: WiFi not connected.");
    return false;
  }

  if (String(THINGSPEAK_WRITE_API_KEY) == "YOUR_THINGSPEAK_WRITE_API_KEY") {
    Serial.println("ThingSpeak: add your Write API Key before uploading.");
    return false;
  }

  HTTPClient http;

  String url = String(THINGSPEAK_UPDATE_URL);
  url += "?api_key=";
  url += THINGSPEAK_WRITE_API_KEY;
  url += "&field1=";
  url += leftValue;
  url += "&field2=";
  url += rightValue;
  url += "&field3=";
  url += topValue;
  url += "&field4=";
  url += bottomValue;
  url += "&field5=";
  url += String(voltage, 2);
  url += "&field6=";
  url += String(current, 2);
  url += "&field7=";
  url += String(power, 2);
  url += "&field8=";
  if (temperatureC == DEVICE_DISCONNECTED_C) {
    url += "0";
  } else {
    url += String(temperatureC, 2);
  }

  http.begin(url);
  const int responseCode = http.GET();

  Serial.print("ThingSpeak Response: ");
  Serial.println(responseCode);

  if (responseCode == HTTP_CODE_OK) {
    Serial.print("ThingSpeak Entry ID: ");
    Serial.println(http.getString());
    http.end();
    return true;
  }

  if (responseCode > 0) {
    Serial.print("ThingSpeak Reply: ");
    Serial.println(http.getString());
  } else {
    Serial.print("HTTP error: ");
    Serial.println(http.errorToString(responseCode));
  }

  http.end();
  return false;
}

// ============================================================
// Setup
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(300);

  analogReadResolution(12);

  // Servo setup
  horizontalServo.setPeriodHertz(50);
  verticalServo.setPeriodHertz(50);

  horizontalServo.attach(HORIZONTAL_SERVO_PIN, 500, 2400);
  verticalServo.attach(VERTICAL_SERVO_PIN, 500, 2400);

  horizontalServo.write(horizontalAngle);
  verticalServo.write(verticalAngle);

  // Temperature sensor
  temperatureSensor.begin();

  // Network
  connectToWiFi();

  Serial.println("================================");
  Serial.println(" SMART SOLAR TRACKER STARTED");
  Serial.println("================================");
}

// ============================================================
// Main loop
// ============================================================
void loop() {
  // Read LDRs
  const int leftValue = analogRead(LDR_LEFT_PIN);
  const int rightValue = analogRead(LDR_RIGHT_PIN);
  const int topValue = analogRead(LDR_TOP_PIN);
  const int bottomValue = analogRead(LDR_BOTTOM_PIN);

  // Update tracker
  updateTracking(leftValue, rightValue, topValue, bottomValue);

  // Read temperature
  temperatureSensor.requestTemperatures();
  const float temperatureC = temperatureSensor.getTempCByIndex(0);

  // Read simulated voltage and current
  const float voltage = readSimulatedVoltage();
  const float current = readSimulatedCurrent();
  const float power = voltage * current;

  // Print values locally
  printReadings(
    leftValue,
    rightValue,
    topValue,
    bottomValue,
    voltage,
    current,
    power,
    temperatureC
  );

  // Upload to ThingSpeak at the selected interval
  if (millis() - lastThingSpeakUpdate >= THINGSPEAK_INTERVAL_MS) {
    connectToWiFi();

    Serial.println("Sending data to ThingSpeak...");

    sendToThingSpeak(
      leftValue,
      rightValue,
      topValue,
      bottomValue,
      voltage,
      current,
      power,
      temperatureC
    );

    lastThingSpeakUpdate = millis();
  }

  delay(500);
}
