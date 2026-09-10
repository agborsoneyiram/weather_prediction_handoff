import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

def load_models():
    """Load trained models."""
    print("\nLoading trained models...")
    models = {}
    for metric in config.TARGET_METRICS:
        model_path = config.MODELS_DIR / f"{metric}_model.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Missing model: {model_path}")
        model_data = joblib.load(model_path)
        print(f"✓ {metric.upper()} → {model_data['model_name']}")
        models[metric] = model_data
    return models

def load_feature_data(location):
    """Load engineered features for one location."""
    print(f"\nLoading features for {location.title()}...")
    df = pd.read_csv(config.DATA_DIR / "processed" / "features.csv")
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = (
        df[df["location"] == location]
        .sort_values("timestamp")
        .reset_index(drop=True)
    )
    print(f"Loaded {len(df):,} feature rows")
    return df

def predict(models, feature_row):
    """Generate predictions for all weather metrics."""
    predictions = {}
    for metric, model_data in models.items():
        feature_names = model_data["features"]
        X = (
            feature_row[feature_names]
            .to_frame()
            .T
            .values
        )

        X_scaled = model_data["scaler"].transform(X)
        prediction = (
            model_data["model"]
            .predict(X_scaled)[0]
        )
        predictions[metric] = round(float(prediction), 2)
    return predictions

def walk_forward_backtest(location):
    """Perform walk-forward validation for one location."""
    print(f"\n{'=' * 70}")
    print(f"BACKTESTING: {location.upper()}")
    print(f"{'=' * 70}")

    models = load_models()
    df = load_feature_data(location)

    results = []
    start_date = pd.Timestamp(config.BACKTEST_TEST_START)
    end_date = pd.Timestamp(config.BACKTEST_TEST_END)

    backtest_df = df[
        (df["timestamp"] >= start_date) &
        (df["timestamp"] <= end_date)
    ].copy()

    print(f"Backtest rows: {len(backtest_df):,}")

    for _, row in backtest_df.iterrows():
        predictions = predict(models, row)
        results.append({
            "timestamp": row["timestamp"],
            "location": location,
            "actual_temp": row["temp"],
            "pred_temp": predictions["temp"],
            "actual_rhum": row["rhum"],
            "pred_rhum": predictions["rhum"],
            "actual_prcp": row["prcp"],
            "pred_prcp": predictions["prcp"]
        })

    results_df = pd.DataFrame(results)
    print(f"\nPredictions generated: {len(results_df):,}")

    results_df["temp_error"] = (
    results_df["actual_temp"] -
    results_df["pred_temp"]
)

    results_df["rhum_error"] = (
        results_df["actual_rhum"] -
        results_df["pred_rhum"]
    )

    results_df["prcp_error"] = (
        results_df["actual_prcp"] -
        results_df["pred_prcp"]
    )

    output_file = (config.VALIDATION_DIR / f"{location}_backtest.csv")
    results_df.to_csv(output_file, index=False)
    print(f"\nSaved to {output_file}")

    print("\n" + "=" * 50)
    print("BACKTEST RESULTS")
    print("=" * 50)

    metrics_summary = []

    for metric in config.TARGET_METRICS:

        actual = results_df[f"actual_{metric}"]
        predicted = results_df[f"pred_{metric}"]

        mae = mean_absolute_error(actual, predicted)
        rmse = np.sqrt(mean_squared_error(actual, predicted))
        r2 = r2_score(actual, predicted)

        print(f"\n{metric.upper()}")
        print(f"MAE : {mae:.3f}")
        print(f"RMSE: {rmse:.3f}")
        print(f"R²  : {r2:.3f}")

        metrics_summary.append({
            "Metric": metric,
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2
        })

    summary_df = pd.DataFrame(metrics_summary)

    summary_file = (
        config.VALIDATION_DIR /
        f"{location}_metrics.csv"
    )

    summary_df.to_csv(summary_file, index=False)

    print(f"\nSaved metrics to {summary_file}")
        

def main():
    for location in config.LOCATIONS.keys():
        walk_forward_backtest(location)

if __name__ == "__main__":
    main()