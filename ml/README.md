# IoT-Based Smart Dual-Axis Solar Tracking and Energy Monitoring System

## 1. Project Problem
Solar energy is highly dependent on the sun's position and environmental factors. Fixed solar panels do not maximize energy capture throughout the day. Furthermore, predicting energy yield is challenging without understanding historical data and environmental features.

## 2. Objectives
- Implement a physical dual-axis solar tracker using ESP32, LDRs, and servo motors.
- Monitor environmental and electrical parameters in real-time via ThingSpeak.
- Leverage real historical solar generation data to build an ML regression model predicting AC Power output.
- Integrate the physical IoT architecture conceptually with the ML prediction pipeline.

## 3. Hardware Architecture
- **ESP32** Microcontroller
- 4x **LDR Sensors** (Top, Bottom, Left, Right) mapped to GPIO 33-36
- 2x **Servo Motors** (Horizontal, Vertical) on GPIO 18, 19
- **DS18B20** Temperature sensor on GPIO 25
- Simulated Voltage (GPIO 32) and Current (GPIO 39) measurement

## 4. IoT Architecture
1. **Sensing:** ESP32 reads LDRs and adjusts servos for optimal sun alignment.
2. **Monitoring:** ESP32 reads temperature, voltage, and current.
3. **Telemetry:** Data is published to ThingSpeak across 8 fields.
4. **ML Layer:** A backend Python service consumes historical/real-time data to predict solar power generation and compares it with actual power.

## 5. Dataset
We utilized real solar generation and weather data from two solar plants:
- `Plant_1_Generation_Data.csv` & `Plant_1_Weather_Sensor_Data.csv`
- `Plant_2_Generation_Data.csv` & `Plant_2_Weather_Sensor_Data.csv`
- Total merged records: 136,472
- Date range: May 15, 2020 - June 17, 2020

## 6. Dataset Preprocessing
- Merged Generation and Weather datasets via `DATE_TIME`.
- Clipped anomalous negative power values to 0.
- Missing values handled (rows containing NaNs dropped).

## 7. Normalization
Continuous features (`AMBIENT_TEMPERATURE`, `MODULE_TEMPERATURE`, `IRRADIATION`) were normalized using `MinMaxScaler` fitted exclusively on the training set to prevent data leakage. The scaler is saved for real-time inference.

## 8. Feature Engineering
Created cyclic time features:
- `HOUR`, `MINUTE`, `TIME_IN_MINUTES`
- `TIME_SIN` and `TIME_COS` for daily cyclic patterns
- `IS_DAY` (Irradiation > 0)

## 9. ML Models
Target Variable: `AC_POWER` (usable electrical output).
Models evaluated:
1. Linear Regression
2. Random Forest Regressor
3. Gradient Boosting Regressor
4. Extra Trees Regressor

## 10. Model Evaluation
A chronological train/val/test split was used (70% Train, 15% Val, 15% Test) to mimic real-world deployment.
Performance metrics calculated: MAE, RMSE, R², MAPE.

## 11. Best Model
**Random Forest Regressor**
- **R² Score:** ~0.84
- **MAE:** ~45.4
- **RMSE:** ~135.5

## 12. Actual Results
Plots generated in `results/plots/`:
- Actual vs Predicted Scatter
- Actual vs Predicted Time Series
- Feature Importances (Irradiation is the strongest predictor)
- Irradiation vs Power Correlation

## 13. IoT Integration
The ESP32 firmware operates the physical tracker and uploads readings to ThingSpeak. The Python ML script can fetch live ThingSpeak data, normalize using the saved scaler, predict power output using the Random Forest model, and push predictions to a new channel for real-time monitoring.
*Note on Limitations: LDR readings indicate light direction and relative intensity, not absolute irradiation in W/m². Real-time ML prediction would require a calibrated pyranometer or mapping LDR voltage to approximate irradiation.*

## 14. Solar Tracker Performance & Comparison
While true baseline static panel generation wasn't physically collected in Phase 1, our dataset analysis proves that maintaining maximum possible irradiation (what a tracker does) yields significantly higher AC Power than sub-optimal angles.
- **Comparison Methodology:** Typical dual-axis tracking increases yield by 25-35% over static panels. The normalized power curves in our actual data show that maximizing `IRRADIATION` dynamically throughout the day maintains peak AC power for a longer duration.

## 15. Limitations & Future Scope
- The historical dataset and IoT prototype lack 1:1 sensor alignment (e.g., LDRs vs actual Irradiation sensors).
- TinyML integration: Future iterations could quantize the Random Forest model (or use a lightweight NN) for direct deployment on the ESP32 using TensorFlow Lite for Microcontrollers.

## 16. How to Run the Project
1. Install dependencies: `pip install pandas numpy matplotlib seaborn scikit-learn joblib`
2. Run data processing: `python src/preprocessing.py`
3. Run feature engineering: `python src/feature_engineering.py`
4. Run normalization: `python src/normalization.py`
5. Run model training: `python src/train.py`
6. Run evaluation & plotting: `python src/evaluate.py`
