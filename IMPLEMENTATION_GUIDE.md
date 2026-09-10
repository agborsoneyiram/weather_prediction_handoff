# Weather Prediction System - Implementation Guide

## Purpose

This guide explains how to run, maintain and integrate the Weather Prediction System.

The machine learning pipeline has already been completed. In most cases, you DO NOT need to retrain the models unless new historical data has been added.

---

# Project Workflow

The complete workflow is:

```
Historical Weather Data
        │
        ▼
Feature Engineering
        │
        ▼
ML Model Training
        │
        ▼
Validation & Backtesting
        │
        ▼
Flask API
        │
        ▼
Mobile Application
```

---

# Folder Structure

```
weather_prediction/

config.py
requirements.txt

models/
    temp_model.pkl
    rhum_model.pkl
    prcp_model.pkl

data/
    historical/
    processed/
        features.csv
    realtime/

outputs/

validation_results/

src/
    api/
    models/
    preprocessing/
    validation/
```

---

# Step 1 - Install Requirements

Activate the virtual environment.

Windows:

```powershell
.venv\Scripts\activate
```

Install packages:

```powershell
pip install -r requirements.txt
```

---

# Step 2 - Configuration

All project settings are stored in

```
config.py
```

This file contains:

- project directories
- API URLs
- model paths
- training dates
- validation dates
- backtest dates
- prediction horizons
- locations

Normally this file should not be modified unless adding a new location or changing date ranges.

---

# Step 3 - Data Collection

Historical weather data is downloaded from Open-Meteo.

The resulting files are stored inside

```
data/historical/
```

---

# Step 4 - Feature Engineering

Run:

```
prepare_data.py
```

Purpose:

Creates the engineered dataset

```
features.csv
```

Features include

- time features
- lag features
- rolling statistics
- difference features

The trained models depend on these engineered features.

---

# Step 5 - Model Training

Run

```
train_models_COMPLETE.py
```

This script

- loads features.csv
- trains three ML models
- compares their performance
- selects the best model
- saves the trained models

Output

```
models/

temp_model.pkl
rhum_model.pkl
prcp_model.pkl
```

These are the production models.

---

# Step 6 - Backtesting

Run

```
backtest.py
```

Purpose

Tests the trained models on unseen historical data.

Outputs

```
validation_results/

kasoa_backtest.csv

accra_backtest.csv

kasoa_metrics.csv

accra_metrics.csv
```

These files compare

Actual Weather

vs

Predicted Weather

---

# Step 7 - Evaluation

The validation scripts create

- actual vs predicted plots
- scatter plots
- error plots
- confusion matrix
- rainfall classifications

These are used for reporting and model evaluation.

---

# Step 8 - API

The Flask application is

```
src/api/app.py
```

Start the API

```
python src/api/app.py
```

Server

```
http://127.0.0.1:5000
```

---

# API Endpoints

## Home

```
GET /
```

Returns server status.

---

## Current Weather

```
GET /current?location=kasoa
```

Returns

- temperature
- humidity
- rainfall

using Open-Meteo.

---

## Prediction

```
GET /predict?location=kasoa
```

Returns

- predicted temperature
- predicted humidity
- predicted rainfall
- rainfall category

---

## Locations

```
GET /locations
```

Returns

Available locations.

---

# Important Files

## weather_service.py

Responsibilities

- Fetch current weather
- Build feature row for prediction

---

## predictor.py

Responsibilities

- Load trained ML models
- Scale features
- Generate predictions

---

## rainfall.py

Responsibilities

Convert rainfall amount into categories.

Current categories

- No Rain
- Low
- Moderate
- High

---

## app.py

Responsibilities

Exposes the REST API.

This file connects

weather_service

↓

predictor

↓

rainfall classifier

↓

JSON response

---

# Mobile App Integration

The mobile application should ONLY communicate with the API.

It should never load ML models directly.

Example flow

```
Flutter

↓

GET /predict

↓

Flask API

↓

Prediction

↓

Display Results
```

---

# Important Notes

The current prediction endpoint uses the latest engineered feature vector stored in

```
features.csv
```

This ensures compatibility with the trained models.

Future work will replace this with dynamically generated features using live Open-Meteo data.

---

# Do NOT Modify

Unless retraining the system

Do not edit

```
models/

temp_model.pkl

rhum_model.pkl

prcp_model.pkl
```

These are the production models.

---

# When Retraining Is Required

Retrain ONLY if

- new historical data is added
- feature engineering changes
- model parameters change

Otherwise simply use the existing models.

---

# Deployment Checklist

✓ Install requirements

✓ Verify config.py

✓ Verify models exist

✓ Start Flask

✓ Test

/current

/predict

/locations

✓ Connect Flutter app

---

# Future Improvements

- Live feature generation
- 7-day forecasting
- Hardware validation
- Cloud deployment
- SMS notifications
- User authentication