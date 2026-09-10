import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import numpy as np
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)


def load_results(location):

    file = config.VALIDATION_DIR / f"{location}_backtest.csv"

    df = pd.read_csv(file)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df


def create_summary(location):

    df = load_results(location)

    df["Month"] = df["timestamp"].dt.strftime("%Y-%m")

    summary = []

    for month, month_df in df.groupby("Month"):

        row = {"Month": month}

        for metric in config.TARGET_METRICS:

            actual = month_df[f"actual_{metric}"]
            predicted = month_df[f"pred_{metric}"]

            row[f"{metric}_MAE"] = mean_absolute_error(actual, predicted)
            row[f"{metric}_RMSE"] = np.sqrt(mean_squared_error(actual, predicted))
            row[f"{metric}_R2"] = r2_score(actual, predicted)

        summary.append(row)

    summary_df = pd.DataFrame(summary)

    output = (
        config.VALIDATION_DIR /
        f"{location}_monthly_summary.csv"
    )

    summary_df.to_csv(output, index=False)

    print(f"Saved {output}")


def main():

    for location in config.LOCATIONS.keys():

        create_summary(location)


if __name__ == "__main__":
    main()