import pandas as pd
from pathlib import Path
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np

OUTPUT_DIR = Path("validation_results")

locations = ["kasoa", "accra"]

metrics = {
    "temp": ("actual_temp", "pred_temp"),
    "rhum": ("actual_rhum", "pred_rhum"),
    "prcp": ("actual_prcp", "pred_prcp")
}

for location in locations:
    file_path = OUTPUT_DIR / f"{location}_backtest.csv"
    df = pd.read_csv(file_path)

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["Month"] = df["timestamp"].dt.month
    df["Month_Name"] = df["timestamp"].dt.strftime("%B").str.upper()

    rows = []

    for month_num in sorted(df["Month"].unique()):
        month_df = df[df["Month"] == month_num]

        for metric, (actual_col, pred_col) in metrics.items():
            actual = month_df[actual_col]
            predicted = month_df[pred_col]

            mae = mean_absolute_error(actual, predicted)
            rmse = np.sqrt(mean_squared_error(actual, predicted))

            rows.append({
                "Month": month_df["Month_Name"].iloc[0],
                "Metric": metric,
                "MAE": mae,
                "RMSE": rmse
            })

    summary = pd.DataFrame(rows)

    output_path = OUTPUT_DIR / f"{location}_monthly_summary.csv"
    summary.to_csv(output_path, index=False)

    print(f"\n{location.upper()}")
    print(summary.to_string(index=False))
    print(f"\nSaved: {output_path}")

print("\nDone! Monthly summaries regenerated from the current April-August backtest.")