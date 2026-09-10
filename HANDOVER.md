# Weather Prediction System - Handover Guide

## Backend Status

The backend is ready for mobile application integration.

The machine learning pipeline has been completed, validated and integrated into a Flask REST API. Unless bugs are discovered, there is no need to modify the machine learning code before integrating the mobile application.

---

# Project Setup

## 1. Activate the virtual environment

Windows:

```powershell
.venv\Scripts\activate
```

---

## 2. Install dependencies

```powershell
pip install -r requirements.txt
```

---

## 3. Start the API

```powershell
python src/api/app.py
```

The server should start on:

```
http://127.0.0.1:5000
```

---

# Available API Endpoints

## Home

```
GET /
```

Returns the API status.

Example response:

```json
{
    "project": "Kasoa Weather Prediction API",
    "status": "running"
}
```

---

## Current Weather

```
GET /current?location=kasoa
```

Returns the latest weather data from Open-Meteo.

Example response:

```json
{
    "location": "kasoa",
    "temperature": 27.8,
    "humidity": 75,
    "rainfall": 0.0,
    "time": "2026-07-10T12:45"
}
```

---

## Weather Prediction

```
GET /predict?location=kasoa
```

Returns the machine learning prediction.

Example response:

```json
{
    "success": true,
    "location": "Kasoa",
    "generated_at": "2026-07-10T13:20:14",
    "prediction": {
        "temperature": 28.6,
        "humidity": 81.7,
        "rainfall": 1.4,
        "rainfall_category": "Low"
    }
}
```

---

## Available Locations

```
GET /locations
```

Example response:

```json
{
    "locations": [
        "Kasoa",
        "Accra"
    ]
}
```

---

# Mobile App Integration

The mobile application should **only communicate with the Flask API**.

The app should **not**:

- Load ML models directly
- Read CSV files
- Perform feature engineering
- Perform rainfall classification

Those responsibilities are handled by the backend.

The integration flow is:

```
Flutter Mobile App
        │
        ▼
HTTP Request
        │
        ▼
Flask API
        │
        ▼
Machine Learning Model
        │
        ▼
JSON Response
        │
        ▼
Display Results
```

---

# Files That Should NOT Be Modified

Unless retraining the machine learning models is required, please do not modify the following files:

```
config.py

src/api/predictor.py

src/api/weather_service.py

src/api/rainfall.py

models/temp_model.pkl

models/rhum_model.pkl

models/prcp_model.pkl
```

These files are responsible for generating the machine learning predictions and changing them may affect prediction accuracy.

---

# Files That May Be Modified

The following can be safely updated if required for frontend integration:

```
src/api/app.py
```

Examples include:

- Adding new API endpoints
- Improving error handling
- Updating response formatting
- Adding authentication (future work)

Avoid changing the existing endpoint responses unless absolutely necessary.

---

# Current Project Status

Completed:

- Historical weather data collection
- Feature engineering
- Machine learning model training
- Model comparison
- Temporal validation
- Walk-forward backtesting
- Evaluation metrics
- Prediction visualizations
- Rainfall classification
- Confusion matrix evaluation
- REST API
- Current weather endpoint
- Prediction endpoint
- Location endpoint

Pending:

- Mobile application integration
- Hardware validation (Arduino sensors)
- Live feature generation
- Cloud deployment

---

# Important Notes

The current prediction endpoint uses the latest engineered feature vector stored in:

```
data/processed/features.csv
```

This was intentionally done to ensure consistency with the trained models during development and integration.

A future enhancement will replace this with dynamically generated features built from live Open-Meteo weather data.

---

# Support

If issues arise during integration:

1. Confirm the virtual environment is activated.
2. Ensure all packages from `requirements.txt` are installed.
3. Verify the Flask API is running.
4. Test each endpoint in the browser before connecting the mobile app.

If the endpoints respond correctly in the browser but not in the mobile application, the issue is likely on the frontend rather than the backend.

---

## Final Notes

The backend has been tested using temporal validation and walk-forward backtesting. The API is ready for frontend integration.

Any future improvements (such as 7-day forecasting, live feature generation, hardware validation, or deployment) should be implemented as enhancements without affecting the current API structure.