
````markdown
# Weather Prediction System - Implementation Guide

## Purpose

This guide explains how the current Weather Prediction System works, how to run the main components, and how the different parts of the system connect.

The machine learning pipeline has already been trained and evaluated. The saved models can be used without retraining unless the historical data, feature engineering, or model configuration is changed.

---

## 1. Project Overview

The system monitors and predicts weather conditions for:

- Kasoa
- Accra

The system works with three main weather variables:

- Temperature
- Relative humidity
- Precipitation (rainfall)

The machine learning models use historical weather data and engineered time-series features to make predictions.

The system also supports physical sensor readings from an ESP32 device.

---

## 2. System Workflow

The main machine learning workflow is:

```text
Open-Meteo Historical Weather Data
              |
              v
      Feature Engineering
              |
              v
       Model Training
              |
              v
        Validation
              |
              v
         Backtesting
              |
              v
          Flask API
              |
              v
       Mobile Application
````

The hardware and live prediction workflow is:

```text
ESP32
 |
 +-- DHT11
 |    +-- Temperature
 |    +-- Humidity
 |
 +-- HW-038
      +-- Rain Sensor ADC Value
              |
              v
       Flask /sensor-data
              |
              v
         MySQL Database
              |
              v
      Live Feature Generation
              |
              v
        /predict/live
              |
              v
         ML Prediction
```

---

## 3. Project Structure

```text
weather_prediction_handoff/

├── config.py
├── requirements.txt
├── README.md
├── HANDOVER.md
├── IMPLEMENTATION_GUIDE.md
├── README_API.md
├── .env.example
├── .gitignore
├── railpack.json
│
├── data/
│   ├── arduino/
│   │   └── sensor_readings.csv
│   ├── historical/
│   │   └── data.csv
│   └── processed/
│       └── features.csv
│
├── models/
│   ├── temp_model.pkl
│   ├── rhum_model.pkl
│   └── prcp_model.pkl
│
├── outputs/
│   ├── figures/
│   └── tables/
│       └── best_models_summary.csv
│
├── validation_results/
│   ├── kasoa_backtest.csv
│   ├── accra_backtest.csv
│   ├── kasoa_classified.csv
│   ├── accra_classified.csv
│   ├── kasoa_daily_backtest.csv
│   ├── accra_daily_backtest.csv
│   ├── kasoa_metrics.csv
│   ├── accra_metrics.csv
│   ├── kasoa_monthly_summary.csv
│   └── accra_monthly_summary.csv
│
└── src/
    ├── api/
    │   ├── app.py
    │   ├── predictor.py
    │   ├── rainfall.py
    │   ├── weather_service.py
    │   └── feature_builder.py
    │
    ├── database/
    │   ├── db.py
    │   └── schema.sql
    │
    ├── data_collection/
    │   └── fetch_data.py
    │
    ├── hardware/
    │   └── weather_sensor.ino
    │
    ├── models/
    │   └── train_models_COMPLETE.py
    │
    ├── preprocessing/
    │   ├── create_features.py
    │   └── live_features.py
    │
    └── validation/
        ├── backtest.py
        ├── rainfall_classifier.py
        └── __init__.py
```

---

## 4. Configuration

All major project settings are stored in:

```text
config.py
```

The configuration contains:

* Project directories
* Kasoa and Accra coordinates
* Open-Meteo API URLs
* Historical data dates
* Training dates
* Validation dates
* Backtesting dates
* Lag settings
* Rolling-window settings
* Model file names
* Rain sensor thresholds

### Current Locations

```text
Kasoa
Accra
```

### Historical Data Period

```text
2020-01-01 to 2026-08-31
```

### Machine Learning Data Split

```text
Training:
2020-01-01 to 2025-12-31

Validation:
2026-01-01 to 2026-03-19

Backtest:
2026-04-01 to 2026-08-31
```

The backtest period is kept separate from model training and validation so that the trained models can be evaluated on later unseen data.

---

## 5. Historical Data Collection

Historical weather data is collected from Open-Meteo.

Run:

```powershell
python src\data_collection\fetch_data.py
```

The script collects hourly:

* Temperature
* Relative humidity
* Precipitation

for Kasoa and Accra.

The combined historical dataset is saved to:

```text
data/historical/data.csv
```

The current dataset contains:

```text
116,880 raw records
```

covering:

```text
2020-01-01 00:00:00
to
2026-08-31 23:00:00
```

---

## 6. Feature Engineering

Feature engineering is handled by:

```text
src/preprocessing/create_features.py
```

Run:

```powershell
python src\preprocessing\create_features.py
```

The script creates time-series features including:

* Hour
* Month
* Day of week
* Cyclical hour features
* Cyclical month features
* Weekend indicator
* Lag features
* Rolling means
* Rolling standard deviations
* Difference features

### Lag Periods

```text
1 hour
3 hours
6 hours
12 hours
24 hours
```

### Rolling Windows

```text
6 hours
12 hours
24 hours
```

The resulting dataset is saved to:

```text
data/processed/features.csv
```

The current feature dataset contains:

```text
116,832 records
49 columns
```

The reduction from the raw dataset is caused by the lag and rolling calculations requiring previous observations.

---

## 7. Machine Learning Models

Model training is handled by:

```text
src/models/train_models_COMPLETE.py
```

Run:

```powershell
python src\models\train_models_COMPLETE.py
```

Three regression models are evaluated:

* Random Forest
* Gradient Boosting
* XGBoost

Separate models are trained for:

* Temperature
* Relative humidity
* Precipitation

The models are compared using validation performance.

### Selected Models

Gradient Boosting was selected as the best-performing model for all three prediction targets based on validation RMSE.

The saved models are:

```text
models/temp_model.pkl
models/rhum_model.pkl
models/prcp_model.pkl
```

---

## 8. Prediction Target

The current trained models perform a:

```text
1-hour-ahead prediction
```

for:

* Temperature
* Relative humidity
* Precipitation

The current models should not be described as producing a 24-hour or next-day forecast unless the prediction target and model pipeline are changed and the models are retrained.

---

## 9. Validation and Backtesting

Backtesting is handled by:

```text
src/validation/backtest.py
```

Run:

```powershell
python src\validation\backtest.py
```

The current backtest covers:

```text
2026-04-01 to 2026-08-31
```

for:

* Kasoa
* Accra

The backtest evaluates:

* MAE
* RMSE
* R²

### Backtest Files

```text
validation_results/kasoa_backtest.csv
validation_results/accra_backtest.csv

validation_results/kasoa_metrics.csv
validation_results/accra_metrics.csv
```

---

## 10. Backtest Results

### Kasoa

| Metric            |   MAE |  RMSE |    R² |
| ----------------- | ----: | ----: | ----: |
| Temperature       | 0.472 | 0.623 | 0.921 |
| Relative Humidity | 2.318 | 3.109 | 0.894 |
| Precipitation     | 0.165 | 0.525 | 0.385 |

### Accra

| Metric            |   MAE |  RMSE |    R² |
| ----------------- | ----: | ----: | ----: |
| Temperature       | 0.459 | 0.593 | 0.925 |
| Relative Humidity | 2.271 | 3.016 | 0.906 |
| Precipitation     | 0.156 | 0.500 | 0.429 |

Temperature and relative humidity show stronger predictive performance than precipitation.

Precipitation is more difficult to predict because rainfall can change rapidly and contains many low or zero values.

---

## 11. Rainfall Classification

The system contains two separate rainfall classification systems.

### 11.1 ML/Open-Meteo Rainfall Classification

The function:

```text
rainfall_category()
```

in:

```text
src/api/rainfall.py
```

classifies precipitation values measured in millimetres.

The current categories are:

* No Rain
* Low
* Moderate
* High

These classifications apply to precipitation values from the weather and ML data.

### 11.2 HW-038 Sensor Classification

The function:

```text
sensor_rain_category()
```

classifies the raw ADC value received from the HW-038 rain sensor.

Current thresholds:

| ADC Reading | Classification |
| ----------: | -------------- |
|      0 - 75 | Dry            |
|    76 - 217 | Light          |
|   218 - 442 | Moderate       |
|   443 - 961 | Heavy          |
|   Above 961 | Very Heavy     |

These values represent sensor readings, not millimetres of rainfall.

The HW-038 sensor is therefore not treated as a calibrated rainfall gauge.

---

## 12. Rainfall Classification Evaluation

The rainfall classifier can be run using:

```powershell
python src\validation\rainfall_classifier.py
```

The resulting classified files are:

```text
validation_results/kasoa_classified.csv
validation_results/accra_classified.csv
```

The classifications can be used to examine how the predicted rainfall categories compare with the observed categories.

---

## 13. Daily Backtest Tables

Daily summaries are generated using:

```text
create_daily_tables.py
```

Run:

```powershell
python create_daily_tables.py
```

The script creates:

```text
validation_results/kasoa_daily_backtest.csv
validation_results/accra_daily_backtest.csv
```

The daily tables contain aggregated values for:

* Temperature
* Relative humidity
* Precipitation
* Prediction errors

Temperature and humidity are calculated using daily means.

Precipitation is calculated using daily totals.

---

## 14. Final Figures

The final actual-vs-predicted figures are generated using:

```text
generate_final_figures.py
```

Run:

```powershell
python generate_final_figures.py
```

The figures are stored in:

```text
outputs/figures/
```

The final figures are:

```text
kasoa_temp_actual_vs_predicted.png
kasoa_rhum_actual_vs_predicted.png
kasoa_prcp_actual_vs_predicted.png

accra_temp_actual_vs_predicted.png
accra_rhum_actual_vs_predicted.png
accra_prcp_actual_vs_predicted.png
```

These figures use daily aggregated backtest data for visualization.

The official performance metrics remain based on the hourly backtest.

---

## 15. Monthly Evaluation

Monthly MAE and RMSE summaries are generated using:

```text
create_monthly_summary.py
```

Run:

```powershell
python create_monthly_summary.py
```

The outputs are:

```text
validation_results/kasoa_monthly_summary.csv
validation_results/accra_monthly_summary.csv
```

The summaries cover:

* April 2026
* May 2026
* June 2026
* July 2026
* August 2026

These monthly summaries are calculated from the hourly backtest results.

---

## 16. Flask API

The Flask application is:

```text
src/api/app.py
```

Start the API with:

```powershell
python src\api\app.py
```

The local server runs on:

```text
http://127.0.0.1:5000
```

The application listens on:

```text
0.0.0.0:5000
```

This allows connections from other devices on the network when network configuration permits it.

---

## 17. API Endpoints

### Home

```text
GET /
```

Returns the API status.

### Current Weather

```text
GET /current?location=kasoa
```

Returns current weather information obtained through the weather service.

Supported locations:

* Kasoa
* Accra

### Standard Prediction

```text
GET /predict?location=kasoa
```

Returns:

* Predicted temperature
* Predicted humidity
* Predicted rainfall
* Rainfall category
* Location
* Generation timestamp

### Live Prediction

```text
GET /predict/live?location=kasoa
```

The live prediction endpoint builds features using recent sensor information and historical weather context.

The prediction source is:

```text
ESP32 + historical context
```

It returns:

* Predicted temperature
* Predicted humidity
* Predicted rainfall
* Rainfall category
* Location
* Generation timestamp

### Available Locations

```text
GET /locations
```

Returns the locations configured in the system.

Current locations:

* Kasoa
* Accra

---

## 18. Sensor Data API

The ESP32 sends sensor readings to:

```text
POST /sensor-data
```

The expected sensor data contains:

```json
{
    "temperature": 28.4,
    "humidity": 79.2,
    "rain_value": 120,
    "device_id": "ESP32_001",
    "location": "Kasoa"
}
```

The API:

1. Receives the sensor reading.
2. Validates the required values.
3. Classifies the HW-038 reading.
4. Creates a timestamp.
5. Saves the reading to MySQL.
6. Returns a success response.

---

## 19. Latest Sensor Reading

```text
GET /sensor-data/latest
```

Returns the latest sensor reading stored in the database.

---

## 20. Sensor History

```text
GET /sensor-data/history?hours=24
```

Returns sensor readings from the requested number of previous hours.

Example:

```text
/sensor-data/history?hours=24
```

returns the available readings for the previous 24 hours.

---

## 21. Hardware

The current hardware implementation uses:

* ESP32
* DHT11
* HW-038 rain sensor

The Arduino/ESP32 code is:

```text
src/hardware/weather_sensor.ino
```

### Sensor Connections

```text
DHT11 DATA → GPIO 4
HW-038 AO  → GPIO 34
```

The ESP32 sends readings to the Flask API over Wi-Fi.

The device currently identifies itself as:

```text
ESP32_001
```

The current configured location is:

```text
Kasoa
```

---

## 22. Database

Sensor readings are stored in MySQL.

Database-related files are:

```text
src/database/db.py
src/database/schema.sql
```

The database stores information including:

* Timestamp
* Temperature
* Humidity
* Raw rain sensor value
* Rain status
* Data source
* Device ID
* Location

The database is used for storing physical sensor readings received from the ESP32.

---

## 23. Mobile Application Integration

The mobile application should communicate with the Flask API rather than loading the machine learning models directly.

Recommended flow:

```text
Mobile App
    |
    v
Flask REST API
    |
    +-- Current Weather
    +-- ML Prediction
    +-- Live Prediction
    +-- Sensor Data
            |
            v
        MySQL Database
```

The mobile application can use endpoints such as:

```text
/current
/predict
/predict/live
/locations
/sensor-data/latest
/sensor-data/history
```

The ML model files should remain on the backend.

---

## 24. Important Project Files

### config.py

Stores the main system configuration, including:

* Locations
* API URLs
* Date ranges
* Feature settings
* Model file names
* Rain sensor thresholds

### fetch_data.py

Downloads historical weather data from Open-Meteo.

### create_features.py

Creates the engineered features required by the trained models.

### train_models_COMPLETE.py

Trains and compares the candidate regression models and saves the selected models.

### backtest.py

Evaluates the saved models on the later unseen backtest period.

### predictor.py

Loads the trained models and generates predictions.

### weather_service.py

Provides weather-service functionality used by the API.

### live_features.py

Builds feature information for live prediction using recent sensor readings and historical weather context.

### rainfall.py

Contains:

* ML precipitation classification
* HW-038 sensor classification

### app.py

Provides the Flask REST API and connects the weather service, prediction system, live features, database, and rainfall classification.

---

## 25. Model Files

The trained models are stored in:

```text
models/
```

Files:

```text
temp_model.pkl
rhum_model.pkl
prcp_model.pkl
```

These files should not be manually edited.

Retraining is required when:

* New historical data is added and should be incorporated into training.
* Feature engineering is changed.
* Model settings are changed.
* The training period is changed.
* The prediction target or forecast horizon is changed.

---

## 26. Deployment

The project contains deployment configuration for cloud hosting.

Deployment-related files include:

```text
railpack.json
requirements.txt
```

The Flask application can be served using a production WSGI server such as Gunicorn when deployed to a supported cloud environment.

For local development:

```powershell
python src\api\app.py
```

---

## 27. Important Notes

### Prediction Horizon

The currently trained models are trained for a:

```text
1-hour-ahead prediction
```

Do not describe the current models as producing a next-day forecast without modifying and retraining the prediction pipeline.

### Rain Sensor

The HW-038 produces an analog sensor reading.

The raw reading is not rainfall in millimetres.

The sensor categories are based on the current experimentally calibrated ADC thresholds.

### Backtesting

The April-August 2026 period is used as the final backtest period.

The saved models are evaluated without retraining them on the backtest period.

### Data Sources

Historical weather data is obtained from Open-Meteo.

Physical sensor data is obtained from the ESP32 and stored in MySQL.

---

## 28. Basic Run Order

For a complete rebuild of the machine learning pipeline:

```powershell
python src\data_collection\fetch_data.py
python src\preprocessing\create_features.py
python src\models\train_models_COMPLETE.py
python src\validation\backtest.py
python src\validation\rainfall_classifier.py
python create_daily_tables.py
python create_monthly_summary.py
python generate_final_figures.py
```

For normal API operation using the existing trained models:

```powershell
python src\api\app.py
```

The model training step is **not required every time the API is started**.

---

## 29. Current System Status

The following components are currently implemented:

* Historical weather data collection
* Kasoa weather data
* Accra weather data
* Feature engineering
* Temperature prediction
* Relative humidity prediction
* Precipitation prediction
* Gradient Boosting model selection
* Model validation
* April-August 2026 backtesting
* Rainfall classification
* Daily backtest summaries
* Monthly evaluation summaries
* Actual-vs-predicted figures
* Flask REST API
* ESP32 sensor data collection
* DHT11 temperature/humidity sensing
* HW-038 rain sensing
* MySQL sensor-data storage
* Live feature generation
* Live prediction endpoint
* API endpoints for sensor readings
* Mobile API integration support

---

## 30. Recommended Future Work

Potential future improvements include:

* Further physical sensor calibration using longer-term observations.
* Additional hardware validation.
* Improved precipitation prediction.
* Multi-step forecasting beyond the current 1-hour-ahead target.
* Mobile application integration and testing.
* Cloud deployment testing.
* SMS notification integration.
* Additional weather locations if required.

```

