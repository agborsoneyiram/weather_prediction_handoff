"""
Creates all engineered features used by the ML models.

Input:
    data/historical/data.csv

Output:
    data/processed/features.csv
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import numpy as np

def engineer_features(df):
    """
    Add all engineered features to a dataframe.

    Parameters
    ----------
    df : pandas.DataFrame
        Historical weather dataframe.

    Returns
    -------
    pandas.DataFrame
        Dataframe containing engineered features.
    """

    df = df.copy()

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["location", "timestamp"]).reset_index(drop=True)

    # -------------------------
    # Time Features
    # -------------------------

    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.month
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    df["hour_sin"] = np.sin(2*np.pi*df["hour"]/24)
    df["hour_cos"] = np.cos(2*np.pi*df["hour"]/24)

    df["month_sin"] = np.sin(2*np.pi*df["month"]/12)
    df["month_cos"] = np.cos(2*np.pi*df["month"]/12)

    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # -------------------------
    # Lag Features
    # -------------------------

    for metric in config.TARGET_METRICS:

        for lag in config.LAG_HOURS:

            df[f"{metric}_lag_{lag}h"] = (
                df.groupby("location")[metric]
                  .shift(lag)
            )

    # -------------------------
    # Rolling Features
    # -------------------------

    for metric in config.TARGET_METRICS:

        grouped = df.groupby("location")[metric]

        for window in config.ROLLING_WINDOWS:

            df[f"{metric}_rolling_mean_{window}h"] = (
                grouped
                .rolling(window)
                .mean()
                .reset_index(level=0, drop=True)
            )

            df[f"{metric}_rolling_std_{window}h"] = (
                grouped
                .rolling(window)
                .std()
                .reset_index(level=0, drop=True)
            )

    # -------------------------
    # Difference Features
    # -------------------------

    for metric in config.TARGET_METRICS:

        df[f"{metric}_diff_1h"] = (
            df.groupby("location")[metric]
              .diff()
        )

    df = df.dropna().reset_index(drop=True)

    return df

def create_features():

    print("=" * 70)
    print("CREATING FEATURES")
    print("=" * 70)

    df = pd.read_csv(
        config.DATA_DIR / "historical" / "data.csv"
    )

    print(f"Loaded {len(df):,} records")

    df = engineer_features(df)

    output = config.DATA_DIR / "processed" / "features.csv"

    df.to_csv(output, index=False)

    print(f"\nSaved to {output}")
    print(f"Final records: {len(df):,}")
    print("=" * 70)
    print("CREATING FEATURES")
    print("=" * 70)

    print("\nLoading historical data...")
    df = pd.read_csv(config.DATA_DIR / "historical" / "data.csv")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values(["location", "timestamp"]).reset_index(drop=True)
    print(f"Loaded {len(df):,} records")

    # 1. TIME FEATURES
    print("\nCreating time features...")
    df["hour"] = df["timestamp"].dt.hour
    df["month"] = df["timestamp"].dt.month
    df["day_of_week"] = df["timestamp"].dt.dayofweek

    df["hour_sin"] = np.sin(2 * np.pi * df["hour"] / 24)
    df["hour_cos"] = np.cos(2 * np.pi * df["hour"] / 24)
    df["month_sin"] = np.sin(2 * np.pi * df["month"] / 12)
    df["month_cos"] = np.cos(2 * np.pi * df["month"] / 12)
    df["is_weekend"] = (df["day_of_week"] >= 5).astype(int)

    # 2. LAG FEATURES
    print("\nCreating lag features...")
    for metric in config.TARGET_METRICS:
        for lag in config.LAG_HOURS:
            df[f"{metric}_lag_{lag}h"] = (
                df.groupby("location")[metric]
                .shift(lag)
            )

    # 3. ROLLING STATISTICS
    print("\nCreating rolling statistics...")
    for metric in config.TARGET_METRICS:
        grouped = df.groupby("location")[metric]
        
        for window in config.ROLLING_WINDOWS:
            df[f"{metric}_rolling_mean_{window}h"] = (
                grouped
                .rolling(window)
                .mean()
                .reset_index(level=0, drop=True)
            )
            df[f"{metric}_rolling_std_{window}h"] = (
                grouped
                .rolling(window)
                .std()
                .reset_index(level=0, drop=True)
            )

    # 4. DIFFERENCE FEATURES
    print("\nCreating difference features...")
    for metric in config.TARGET_METRICS:
        df[f"{metric}_diff_1h"] = (
            df.groupby("location")[metric]
            .diff()
        )

    # 5. CLEAN AND SAVE
    print("\nRemoving incomplete rows...")
    before = len(df)
    df = df.dropna().reset_index(drop=True)
    after = len(df)
    print(f"Removed {before - after:,} rows")

    print("\nSaving features...")
    output = config.DATA_DIR / "processed" / "features.csv"
    df.to_csv(output, index=False)
    
    print(f"Saved to {output}")
    print(f"Final records: {len(df):,}")
    print("\nDone!")

if __name__ == "__main__":
    create_features()