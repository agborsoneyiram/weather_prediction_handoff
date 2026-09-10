import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import numpy as np

from src.database.db import get_latest_sensor_reading


def build_live_features(location="kasoa"):
    """
    Build the 44 ML features required by the trained models.

    Historical Open-Meteo data provides the required lag and rolling
    context. The latest ESP32 temperature and humidity readings are
    used as the current observation.

    The HW-038 rain sensor is NOT converted to rainfall (mm), because
    its raw ADC value represents surface wetness/conductivity rather
    than measured rainfall amount.
    """

    # --------------------------------------------------
    # 1. Load historical engineered dataset
    # --------------------------------------------------

    features_file = (
        config.DATA_DIR
        / "processed"
        / "features.csv"
    )

    df = pd.read_csv(features_file)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    df = df[
        df["location"].str.lower() == location.lower()
    ].copy()

    if df.empty:
        raise ValueError(
            f"No historical data found for location: {location}"
        )

    df = df.sort_values("timestamp")

    # --------------------------------------------------
    # 2. Get latest ESP32 reading
    # --------------------------------------------------

    sensor = get_latest_sensor_reading()

    if sensor is None:
        raise ValueError(
            "No ESP32 sensor readings available."
        )

    sensor_timestamp = pd.to_datetime(
        sensor["timestamp"]
    )

    # --------------------------------------------------
    # 3. Create current observation
    # --------------------------------------------------

    latest_historical = df.iloc[-1].copy()

    current = latest_historical.copy()

    current["timestamp"] = sensor_timestamp

    # Replace current temperature/humidity with ESP32 data
    current["temp"] = float(sensor["temperature"])
    current["rhum"] = float(sensor["humidity"])

    # Keep historical rainfall amount for ML.
    # HW-038 rain_value is NOT rainfall in mm.
    current["prcp"] = float(latest_historical["prcp"])

    # --------------------------------------------------
    # 4. Build a raw hourly dataframe
    # --------------------------------------------------

    raw_file = (
        config.DATA_DIR
        / "historical"
        / "data.csv"
    )

    raw = pd.read_csv(raw_file)

    raw["timestamp"] = pd.to_datetime(
        raw["timestamp"]
    )

    raw = raw[
        raw["location"].str.lower() == location.lower()
    ].copy()

    raw = raw.sort_values("timestamp")

    # --------------------------------------------------
    # 5. Append live observation
    # --------------------------------------------------

    live_row = pd.DataFrame([{
        "timestamp": sensor_timestamp,
        "location": location.lower(),
        "temp": float(sensor["temperature"]),
        "rhum": float(sensor["humidity"]),
        "prcp": float(latest_historical["prcp"])
    }])

    raw = pd.concat(
        [raw, live_row],
        ignore_index=True
    )

    raw = raw.sort_values("timestamp")

    # Remove duplicate timestamps
    raw = raw.drop_duplicates(
        subset=["timestamp"],
        keep="last"
    )

    # --------------------------------------------------
    # 6. Time features
    # --------------------------------------------------

    raw["hour"] = raw["timestamp"].dt.hour
    raw["month"] = raw["timestamp"].dt.month
    raw["day_of_week"] = (
        raw["timestamp"].dt.dayofweek
    )

    raw["hour_sin"] = np.sin(
        2 * np.pi * raw["hour"] / 24
    )

    raw["hour_cos"] = np.cos(
        2 * np.pi * raw["hour"] / 24
    )

    raw["month_sin"] = np.sin(
        2 * np.pi * raw["month"] / 12
    )

    raw["month_cos"] = np.cos(
        2 * np.pi * raw["month"] / 12
    )

    raw["is_weekend"] = (
        raw["day_of_week"] >= 5
    ).astype(int)

    # --------------------------------------------------
    # 7. Lag features
    # --------------------------------------------------

    for metric in config.TARGET_METRICS:

        for lag in config.LAG_HOURS:

            raw[f"{metric}_lag_{lag}h"] = (
                raw[metric].shift(lag)
            )

    # --------------------------------------------------
    # 8. Rolling features
    # --------------------------------------------------

    for metric in config.TARGET_METRICS:

        for window in config.ROLLING_WINDOWS:

            raw[
                f"{metric}_rolling_mean_{window}h"
            ] = (
                raw[metric]
                .rolling(window)
                .mean()
            )

            raw[
                f"{metric}_rolling_std_{window}h"
            ] = (
                raw[metric]
                .rolling(window)
                .std()
            )

    # --------------------------------------------------
    # 9. Difference features
    # --------------------------------------------------

    for metric in config.TARGET_METRICS:

        raw[f"{metric}_diff_1h"] = (
            raw[metric].diff()
        )

    # --------------------------------------------------
    # 10. Get latest complete row
    # --------------------------------------------------

    raw = raw.dropna().reset_index(drop=True)

    if raw.empty:
        raise ValueError(
            "Unable to create complete live feature row."
        )

    latest = raw.iloc[-1].copy()

    # --------------------------------------------------
    # 11. Verify model feature requirements
    # --------------------------------------------------

    for metric in config.TARGET_METRICS:

        model_file = (
            config.MODELS_DIR
            / f"{metric}_model.pkl"
        )

        import joblib

        model_data = joblib.load(model_file)

        required_features = model_data["features"]

        missing = [
            feature
            for feature in required_features
            if feature not in latest.index
        ]

        if missing:
            raise ValueError(
                f"Missing features for {metric}: {missing}"
            )

    return latest