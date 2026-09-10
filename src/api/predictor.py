import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import joblib
import pandas as pd

MODELS = {}

for metric in config.TARGET_METRICS:
    model_data = joblib.load(
        config.MODELS_DIR / f"{metric}_model.pkl"
    )
    MODELS[metric] = model_data


def predict_weather(feature_row):

    predictions = {}

    for metric, model_data in MODELS.items():

        X = (
            feature_row[model_data["features"]]
            .to_frame()
            .T
            .values
        )

        X = model_data["scaler"].transform(X)

        prediction = model_data["model"].predict(X)[0]

        predictions[metric] = round(float(prediction), 2)

    return predictions