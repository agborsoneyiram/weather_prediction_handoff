import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

OUTPUT_DIR = Path("outputs/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

locations = ["kasoa", "accra"]

for location in locations:
    file_path = Path(f"validation_results/{location}_daily_backtest.csv")
    df = pd.read_csv(file_path)
    df["date"] = pd.to_datetime(df["date"])

    plots = [
        {
            "actual": "actual_temp",
            "predicted": "pred_temp",
            "title": f"{location.title()} - Actual vs Predicted Temperature",
            "ylabel": "Temperature (°C)",
            "filename": f"{location}_temp_actual_vs_predicted.png"
        },
        {
            "actual": "actual_rhum",
            "predicted": "pred_rhum",
            "title": f"{location.title()} - Actual vs Predicted Relative Humidity",
            "ylabel": "Relative Humidity (%)",
            "filename": f"{location}_rhum_actual_vs_predicted.png"
        },
        {
            "actual": "actual_prcp",
            "predicted": "pred_prcp_nonnegative",
            "title": f"{location.title()} - Actual vs Predicted Precipitation",
            "ylabel": "Precipitation (mm)",
            "filename": f"{location}_prcp_actual_vs_predicted.png"
        }
    ]

    for plot in plots:
        plt.figure(figsize=(12, 5))

        plt.plot(
            df["date"],
            df[plot["actual"]],
            label="Actual"
        )

        plt.plot(
            df["date"],
            df[plot["predicted"]],
            label="Predicted"
        )

        plt.title(plot["title"])
        plt.xlabel("Date")
        plt.ylabel(plot["ylabel"])
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()

        output_path = OUTPUT_DIR / plot["filename"]
        plt.savefig(output_path, dpi=300, bbox_inches="tight")
        plt.close()

        print(f"Saved: {output_path}")

print("\nDone! Final figures generated successfully.")