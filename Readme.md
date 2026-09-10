# Kasoa Weather Prediction System

A weather prediction system that combines historical weather data, live ESP32 sensor readings, machine learning, and a Flask REST API to provide weather information and predictions for Kasoa and Accra.

---

## 1. Project Overview

The system combines:

- Historical weather data from Open-Meteo
- Live temperature and humidity readings from a DHT11 sensor
- Live rain-sensor readings from an HW-038 water level/rain sensor
- ESP32 hardware for sensor acquisition and communication
- MySQL for storing live sensor readings
- Machine learning models for temperature, humidity, and rainfall prediction
- Flask REST API for accessing weather data and predictions

### Supported Locations

- Kasoa
- Accra

---

## 2. System Architecture

The system follows this general flow:

```text
ESP32 Sensors
    │
    │ HTTP POST
    ▼
Flask REST API
    │
    ▼
MySQL Database
    │
    ▼
Recent Sensor History
    +
Historical Weather Context
    │
    ▼
Live Feature Generation
    │
    ▼
Trained ML Models
    │
    ▼
Temperature / Humidity / Rainfall Prediction
    │
    ▼
Frontend Application
```

The backend, ML models, database, ESP32, and frontend work together as separate components.

The frontend communicates with the Flask API rather than accessing the MySQL database directly.

---

## 3. Project Structure

The main project directories are:

| Directory / File | Purpose |
|---|---|
| `src/api/` | Flask API and prediction-related code |
| `src/database/` | MySQL database functions |
| `src/data_collection/` | Historical weather data collection |
| `src/hardware/` | ESP32 and hardware-related code |
| `src/hardware/` | ESP32 and hardware-related code |
| `src/hardware/weather_sensor.ino` | Final ESP32 sensor program |
| `src/models/` | Model training and model-related scripts |
| `src/preprocessing/` | Feature engineering and live feature generation |
| `src/validation/` | Model validation and evaluation |
| `models/` | Trained machine learning models |
| `data/` | Historical and processed datasets |
| `outputs/` | Generated prediction/evaluation outputs |
| `validation_results/` | Validation results |
| `graphs/` | Generated graphs and visualizations |
| `database/schema.sql` | MySQL database schema |
| `config.py` | Project configuration |
| `requirements.txt` | Python dependencies |
| `.env.example` | Environment-variable template |
| `README.md` | Project documentation |

### Trained Models

The `models/` directory contains the trained models used by the prediction API:

- `temp_model.pkl`
- `rhum_model.pkl`
- `prcp_model.pkl`

These files are required by the prediction system and should be included when deploying the backend.

---

## 4. Requirements

### Python

The development environment uses **Python 3.14.6**.

### Python Dependencies

Dependencies are listed in `requirements.txt`.

Install them with:

```powershell
pip install -r requirements.txt
```

The project uses Flask, Flask-CORS, Pandas, NumPy, Scikit-learn, XGBoost, SQLAlchemy, PyMySQL, Requests, Joblib, and supporting libraries.

---

## 5. Environment Configuration

The application uses environment variables for MySQL configuration.

Create a `.env` file in the project root using `.env.example` as a template.

Example:

```env
DB_USER=your_mysql_username
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=weather_prediction
```

The actual `.env` file contains private database credentials and should not be shared publicly.

---

## 6. Database Setup

The system uses MySQL for storing live ESP32 sensor readings.

The database schema is provided in:

`database/schema.sql`

The schema creates the `weather_prediction` database and the `sensor_readings` table.

### `sensor_readings`

The table contains:

| Column | Description |
|---|---|
| `id` | Unique auto-incrementing reading ID |
| `timestamp` | Time the reading was recorded |
| `temperature` | Temperature measured by the DHT11 |
| `humidity` | Relative humidity measured by the DHT11 |
| `rain_value` | Raw analog value from the HW-038 |
| `rain_status` | Classified sensor wetness/rain status |
| `source` | Source of the reading, currently `ESP32` |
| `device_id` | Identifier of the ESP32 device |
| `location` | Sensor location |

Run `database/schema.sql` using MySQL to create the required database and table.

---

## 7. Running the Flask API

From the project root, start the Flask API with:

```powershell
python src\api\app.py
```

The development server runs on port `5000`.

Locally, the API can be accessed through:

`http://127.0.0.1:5000`

The application is configured to listen on all network interfaces so that devices such as the ESP32 can communicate with it over the local network.

---

## 8. API Endpoints

### API Status

**GET** `/`

Returns the API status.

---

### Current Weather

**GET** `/current?location=kasoa`

Returns current weather information for the requested location.

Supported locations:

- `kasoa`
- `accra`

---

### Standard ML Prediction

**GET** `/predict?location=kasoa`

Returns a machine-learning prediction based on the standard weather-data feature pipeline.

The response contains:

- Temperature prediction
- Humidity prediction
- Rainfall prediction
- Rainfall category

---

### Live ML Prediction

**GET** `/predict/live?location=kasoa`

This is the main endpoint for the live prediction system.

It uses recent ESP32 sensor history together with historical weather context to generate the feature row required by the trained models.

The response contains:

- Temperature prediction
- Humidity prediction
- Rainfall prediction
- Rainfall category
- Location
- Prediction generation timestamp

Example request:

```text
/predict/live?location=kasoa
```

---

### Available Locations

**GET** `/locations`

Returns the locations supported by the system.

---

### Receive ESP32 Sensor Data

**POST** `/sensor-data`

The ESP32 sends its readings to this endpoint.

Example request body:

```json
{
    "temperature": 29.5,
    "humidity": 72.1,
    "rain_value": 0,
    "device_id": "ESP32_001",
    "location": "Kasoa"
}
```

The API:

1. Receives the sensor reading.
2. Classifies the rain-sensor value.
3. Adds a timestamp.
4. Stores the reading in MySQL.
5. Returns the saved reading.

---

### Latest Sensor Reading

**GET** `/sensor-data/latest`

Returns the most recent ESP32 sensor reading stored in the database.

---

### Sensor History

**GET** `/sensor-data/history?hours=24`

Returns sensor readings from the specified number of previous hours.

For example:

`/sensor-data/history?hours=1`

returns the sensor readings from the previous hour.

---

## 9. ESP32 Hardware

The ESP32 is responsible for collecting live environmental readings and sending them to the Flask API.

### DHT11

The DHT11 provides:

- Temperature
- Relative humidity

### HW-038

The HW-038 provides an analog water/rain sensor value.

The sensor was experimentally calibrated using different levels of wetness.

The ESP32 sends the readings to the Flask API using an HTTP POST request.

The current development sketch contains the local Flask server address.

When the backend is deployed, the `serverURL` in the ESP32 sketch must be changed to the deployed API address.

---
## 10. Hardware Connections

The weather monitoring hardware consists of an ESP32, DHT11 temperature/humidity sensor, and HW-038 water-level/rain sensor.

### DHT11 → ESP32

| DHT11 Pin | ESP32  |
|---        |---     |
| VCC       | 3.3V   |
| DATA      | GPIO 4 |
| GND       | GND    |

The DHT11 is configured in the ESP32 code using `DHTPIN 4`.

### HW-038 → ESP32

| HW-038 Pin | ESP32 |
|---|---|
| VCC | 3.3V |
| GND | GND |
| AO | GPIO 34 |

The HW-038 analog output is read using GPIO 34, configured in the ESP32 code as `RAIN_PIN 34`.

### Power

During development/testing, the ESP32 can be powered through USB or a power bank.

The sensors receive power from the ESP32.

### Hardware Data Flow

DHT11 and HW-038
→ ESP32
→ Wi-Fi
→ Flask `/sensor-data`
→ MySQL
→ Live feature generation
→ ML prediction
→ Frontend

---
## 11. Rain Sensor Classification

The HW-038 produces a raw analog value rather than directly reporting rainfall in millimetres.

The sensor was therefore calibrated experimentally by exposing it to different levels of wetness.

The calibrated sensor classifications are:

- Dry
- Light
- Moderate
- Heavy
- Very Heavy

These classifications describe the **physical wetness detected by the HW-038**.

They should not be confused with the rainfall categories produced by the machine-learning prediction model.

### ML Rainfall Categories

The ML prediction system uses:

- No Rain
- Low
- Moderate
- High

The raw HW-038 value is therefore used as sensor information, while the ML model produces its own rainfall prediction.

---

## 12. Machine Learning

The system uses engineered weather features for prediction.

The feature set includes:

- Hour
- Month
- Day of week
- Cyclical time features
- Weekend indicator
- Temperature lag features
- Humidity lag features
- Rainfall lag features
- Rolling means
- Rolling standard deviations
- Difference features

The live feature-generation process uses recent sensor history together with the required historical feature structure.

### Prediction Targets

The trained models predict:

- Temperature
- Relative humidity
- Rainfall

The trained models are stored in the `models/` directory.

---

## 13. Live Prediction Pipeline

The live prediction process is:

1. The ESP32 collects temperature, humidity, and rain-sensor readings.
2. The ESP32 sends the readings to `POST /sensor-data`.
3. Flask validates and stores the readings in MySQL.
4. Recent sensor history is retrieved from the database.
5. Live features are generated.
6. The trained ML models process the generated features.
7. Predictions are produced for temperature, humidity, and rainfall.
8. The rainfall prediction is converted into a rainfall category.
9. The frontend can retrieve the result through `/predict/live`.

In short:

**ESP32 → Flask → MySQL → Live Features → ML Models → Prediction API → Frontend**

---

## 14. Testing and Verification

The following API endpoints were successfully tested during development:

| Endpoint | Status |
|---|---|
| `GET /` | Passed |
| `GET /current` | Passed |
| `GET /predict` | Passed |
| `GET /predict/live` | Passed |
| `GET /sensor-data/latest` | Passed |
| `GET /sensor-data/history` | Passed |

### ESP32 Testing

The ESP32 system was tested for:

- Wi-Fi connectivity
- Sensor readings
- Flask communication
- HTTP POST requests
- MySQL data storage
- Device ID and location transmission
- Operation using a power bank
- Sensor calibration

The ESP32 successfully transmitted readings to Flask and the readings were stored in MySQL.

---

## 15. Reproducing the Development Environment

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\activate
```

Install the project dependencies:

```powershell
pip install -r requirements.txt
```

Configure the `.env` file with the appropriate MySQL credentials.

Create the database using:

`database/schema.sql`

Then start the Flask API:

```powershell
python src\api\app.py
```

---

## 16. Deployment

The current setup is configured for local development and testing.

A complete deployed system requires the following components:

| Component | Deployment Requirement |
|---|---|
| Flask API | Deploy to an accessible server |
| ML models | Include the trained `.pkl` files |
| MySQL | Deploy or connect to a production database |
| Frontend | Deploy separately or alongside the backend |
| ESP32 | Update the API URL to the deployed backend |
| Environment variables | Configure securely on the deployment server |

### Important Deployment Changes

Before production deployment:

- Replace the local Flask server address in the ESP32 sketch.
- Configure production MySQL credentials.
- Configure CORS for the deployed frontend.
- Use a production WSGI server instead of Flask's development server.
- Use HTTPS for production API communication.
- Keep database credentials private.
- Ensure the deployed API is reachable by the ESP32.
- Ensure the trained model files are available to the backend.

---

## 17. Frontend Integration

The frontend should communicate with the Flask API rather than connecting directly to MySQL.

The main endpoint for displaying live ML predictions is:

`GET /predict/live?location=kasoa`

For live sensor information, the frontend can use:

- `GET /sensor-data/latest`
- `GET /sensor-data/history?hours=24`

This allows the frontend and backend to be deployed independently while communicating through the Flask API.

The frontend API base URL will need to be updated when the Flask backend is deployed.

---

## 18. Handoff Information

This backend/ML/IoT component is designed to be handed over and deployed independently of the frontend.

The person deploying the system will need:

1. The complete project directory.
2. The trained models in `models/`.
3. `requirements.txt`.
4. `.env.example`.
5. `database/schema.sql`.
6. The final ESP32 sketch.
7. Access to a MySQL database.
8. The deployment server or hosting environment.

### Do Not Include

The following should not be included in a public or shared deployment package:

- `.env` containing real credentials
- `.venv/`
- `__pycache__/`
- Python `.pyc` files
- Temporary files
- Local development-only configuration

The trained `.pkl` model files **should be included**, because they are required by the prediction API unless the models are intentionally retrained during deployment.

---

## 19. Quick Start

For a fresh environment:

### 1. Create the environment

```powershell
python -m venv .venv
```

### 2. Activate it

```powershell
.\.venv\Scripts\activate
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. Configure the database

Create `.env` using `.env.example`.

Then run:

`database/schema.sql`

### 5. Start Flask

```powershell
python src\api\app.py
```

### 6. Verify the API

Open:

`GET /`

Then test:

`GET /predict/live?location=kasoa`

### 7. Configure the ESP32

Update the ESP32 `serverURL` to point to the deployed Flask API.

---

## 20. Current Project Status

The following components have been completed and tested:

- Historical weather-data processing
- Feature engineering
- Machine-learning model training
- Trained model storage
- ESP32 sensor acquisition
- HW-038 calibration
- Rainfall sensor classification
- Flask API
- MySQL sensor storage
- Live sensor-data endpoints
- Live feature generation
- Live ML prediction
- ESP32-to-Flask communication
- Power-bank operation
- API smoke testing
- Project requirements file
- Database schema
- Environment-variable template
- Handoff documentation

The remaining deployment work is primarily infrastructure-related: hosting the Flask backend and MySQL database, deploying the frontend, connecting the deployed frontend to the API, and updating the ESP32 API URL.

---

## 21. Notes

The current system is configured for development/testing.

The Flask development server should not be used as the production server.

The local IP address currently used by the ESP32 is specific to the development network and must be replaced with the deployed backend address before production use.

The frontend should consume the Flask API and should not connect directly to the MySQL database.