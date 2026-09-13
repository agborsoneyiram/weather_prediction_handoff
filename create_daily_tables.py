import pandas as pd
from pathlib import Path

Path("validation_results").mkdir(exist_ok=True)

for location in ["kasoa", "accra"]:
    df = pd.read_csv(f"validation_results/{location}_classified.csv")

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["date"] = df["timestamp"].dt.date

    # Keep original model predictions untouched.
    # Create a separate non-negative version for daily rainfall reporting.
    df["pred_prcp_nonnegative"] = df["pred_prcp"].clip(lower=0)

    daily = df.groupby("date").agg(
        actual_temp=("actual_temp", "mean"),
        pred_temp=("pred_temp", "mean"),
        actual_rhum=("actual_rhum", "mean"),
        pred_rhum=("pred_rhum", "mean"),
        actual_prcp=("actual_prcp", "sum"),
        pred_prcp=("pred_prcp", "sum"),
        pred_prcp_nonnegative=("pred_prcp_nonnegative", "sum")
    ).reset_index()

    daily["location"] = location

    daily["temp_error"] = daily["actual_temp"] - daily["pred_temp"]
    daily["rhum_error"] = daily["actual_rhum"] - daily["pred_rhum"]
    daily["prcp_error"] = daily["actual_prcp"] - daily["pred_prcp"]

    daily = daily[
        [
            "date",
            "location",
            "actual_temp",
            "pred_temp",
            "temp_error",
            "actual_rhum",
            "pred_rhum",
            "rhum_error",
            "actual_prcp",
            "pred_prcp",
            "pred_prcp_nonnegative",
            "prcp_error"
        ]
    ]

    output = f"validation_results/{location}_daily_backtest.csv"
    daily.to_csv(output, index=False)

    print(f"{location}: {len(daily)} daily rows saved")
    print(daily.head(3).to_string(index=False))
    print()

print("Done!")