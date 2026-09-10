import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent))

import config

from flask import Flask, jsonify, request
from datetime import datetime

from weather_service import (get_current_weather, build_feature_row)

from predictor import predict_weather
from rainfall import rainfall_category, sensor_rain_category
from src.database.db import save_sensor_reading, get_latest_sensor_reading, get_sensor_history
from src.preprocessing.live_features import build_live_features

app = Flask(__name__)


@app.route("/")
def home():
    return {
        "project": "Kasoa Weather Prediction API",
        "status": "running"
    }


@app.route("/current")
def current_weather():

    location = request.args.get("location", "kasoa").lower()

    try:
        return jsonify(get_current_weather(location))
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/predict")
def predict():

    location = request.args.get(
        "location",
        "kasoa"
    ).lower()

    if location not in ["kasoa", "accra"]:
        return jsonify({
            "error": "Invalid location"
        }), 400

    feature_row = build_feature_row(location)

    prediction = predict_weather(feature_row)

    prediction["rainfall_category"] = rainfall_category(
        prediction["prcp"]
    )

    return jsonify({
        "success": True,
        "location": location.title(),
        "generated_at": datetime.now().isoformat(),

        "prediction": {
            "temperature": prediction["temp"],
            "humidity": prediction["rhum"],
            "rainfall": prediction["prcp"],
            "rainfall_category": prediction["rainfall_category"]
        }
    })

@app.route("/predict/live")
def live_prediction():

    location = request.args.get(
        "location",
        "kasoa"
    ).lower()

    if location not in ["kasoa", "accra"]:
        return jsonify({
            "success": False,
            "error": "Invalid location"
        }), 400

    try:
        feature_row = build_live_features(location)

        prediction = predict_weather(feature_row)

        prediction["rainfall_category"] = rainfall_category(
            prediction["prcp"]
        )

        return jsonify({
            "success": True,
            "location": location.title(),
            "generated_at": datetime.now().isoformat(),

            "prediction_source": "ESP32 + historical context",

            "prediction": {
                "temperature": prediction["temp"],
                "humidity": prediction["rhum"],
                "rainfall": prediction["prcp"],
                "rainfall_category": prediction["rainfall_category"]
            }
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route("/locations")
def locations():

    return jsonify({
        "locations": [
            value["name"]
            for value in config.LOCATIONS.values()
        ]
    })

@app.route("/sensor-data", methods=["POST"])
def sensor_data():

    data = request.get_json()

    if not data:
        return jsonify({
            "success": False,
            "error": "No sensor data received"
        }), 400

    temperature = data.get("temperature")
    humidity = data.get("humidity")
    rain_value = data.get("rain_value")
    device_id = data.get("device_id", "ESP32_001")
    location = data.get("location", "Kasoa")

    # Validate required sensor values
    if temperature is None or humidity is None or rain_value is None:
        return jsonify({
            "success": False,
            "error": "Missing sensor data"
        }), 400

    # Classify HW-038 sensor reading
    rain_status = sensor_rain_category(rain_value)

    # Create timestamp for this reading
    timestamp = datetime.now().isoformat()

    # Prepare reading
    reading = {
        "timestamp": timestamp,
        "temperature": temperature,
        "humidity": humidity,
        "rain_value": rain_value,
        "rain_status": rain_status,
        "source": "ESP32",
        "device_id": device_id,
        "location": location
    }

    # Save to MySQL
    try:
        database_saved = save_sensor_reading(reading)

        if not database_saved:
            return jsonify({
                "success": False,
                "message": "Database save returned false",
                "database_saved": False
            }), 500

    except Exception as e:
        print("🔥 DATABASE EXCEPTION:", repr(e))

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

    return jsonify({
        "success": True,
        "message": "Sensor data received and saved",
        "database_saved": True,
        "data": reading
    })
    print("🔥 DATABASE EXCEPTION:", repr(e))

    return jsonify({
        "success": False,
        "error": str(e)
    }), 500


@app.route("/sensor-data/latest", methods=["GET"])
def latest_sensor_data():

    reading = get_latest_sensor_reading()

    if reading is None:
        return jsonify({
            "success": False,
            "message": "No sensor readings available"
        }), 404

    # Convert timestamp to string for JSON
    reading["timestamp"] = reading["timestamp"].isoformat()

    return jsonify({
        "success": True,
        "data": reading
    })

@app.route("/sensor-data/history", methods=["GET"])
def sensor_history():

    hours = request.args.get("hours", default=24, type=int)

    if hours <= 0:
        return jsonify({
            "success": False,
            "error": "Hours must be greater than 0"
        }), 400

    readings = get_sensor_history(hours)

    # Convert timestamps to strings for JSON
    for reading in readings:
        reading["timestamp"] = reading["timestamp"].isoformat()

    return jsonify({
        "success": True,
        "hours": hours,
        "count": len(readings),
        "data": readings
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)