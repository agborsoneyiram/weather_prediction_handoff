import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd

def load_results(location):

    file = config.VALIDATION_DIR / f"{location}_backtest.csv"

    return pd.read_csv(file)

def classify_rain(mm):

    if mm < 0.1:
        return "No Rain"

    elif mm < 2.5:
        return "Light"

    elif mm < 10:
        return "Moderate"

    else:
        return "Heavy"

def classify_dataframe(df):

    df["actual_class"] = (
        df["actual_prcp"]
        .apply(classify_rain)
    )

    df["predicted_class"] = (
        df["pred_prcp"]
        .apply(classify_rain)
    )

    return df

def save_results(df, location):

    file = (
        config.VALIDATION_DIR /
        f"{location}_classified.csv"
    )

    df.to_csv(file, index=False)

    print(f"Saved {file}")

def main():

    for location in config.LOCATIONS.keys():

        df = load_results(location)

        df = classify_dataframe(df)

        save_results(df, location)

if __name__ == "__main__":
    main()

