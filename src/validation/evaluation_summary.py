import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import numpy as np

def load_results(location):

    file = config.VALIDATION_DIR / f"{location}_backtest.csv"

    df = pd.read_csv(file)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df

def monthly_summary(df, location):

    df["month"] = df["timestamp"].dt.to_period("M")

    summaries = []

    for month in sorted(df["month"].unique()):

        monthly = df[df["month"] == month]

        for metric in config.TARGET_METRICS:

            error = (
                monthly[f"actual_{metric}"] -
                monthly[f"pred_{metric}"]
            )

            summaries.append({

                "Month": str(month),

                "Metric": metric,

                "MAE": np.mean(np.abs(error)),

                "RMSE": np.sqrt(np.mean(error**2))

            })

    summary = pd.DataFrame(summaries)

    summary.to_csv(

        config.VALIDATION_DIR /
        f"{location}_monthly_summary.csv",

        index=False

    )

    print(f"Saved monthly summary for {location}")

def main():

    for location in config.LOCATIONS.keys():

        df = load_results(location)

        monthly_summary(df, location)

if __name__ == "__main__":
    main()