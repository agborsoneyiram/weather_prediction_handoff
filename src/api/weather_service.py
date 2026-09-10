import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import requests
import pandas as pd


def get_current_weather(location):
    """
    Fetch current weather from Open-Meteo.

    Returns:
        dict containing temperature, humidity and rainfall
    """

    if location not in config.LOCATIONS:
        raise ValueError(f"Unknown location: {location}")

    loc = config.LOCATIONS[location]

    params = {
        "latitude": loc["lat"],
        "longitude": loc["lon"],
        "current": "temperature_2m,relative_humidity_2m,precipitation",
        "timezone": "Africa/Accra"
    }

    response = requests.get(
        config.OPEN_METEO_REALTIME,
        params=params,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()["current"]

    return {
        "location": location,
        "temperature": data["temperature_2m"],
        "humidity": data["relative_humidity_2m"],
        "rainfall": data.get("precipitation", 0.0),
        "time": data["time"]
    }

def build_feature_row(location):
    """
    Returns one feature row for prediction.
    """

    df = pd.read_csv(
        config.DATA_DIR / "processed" / "features.csv"
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    latest = (
        df[df["location"] == location]
        .sort_values("timestamp")
        .iloc[-1]
    )

    return latest