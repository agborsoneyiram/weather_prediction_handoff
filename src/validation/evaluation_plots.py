import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import matplotlib.pyplot as plt


GRAPH_DIR = config.VALIDATION_DIR / "graphs"
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

def load_results(location):

    file = config.VALIDATION_DIR / f"{location}_backtest.csv"

    df = pd.read_csv(file)

    df["timestamp"] = pd.to_datetime(df["timestamp"])

    return df

def plot_actual_vs_predicted(df, metric, location):

    plt.figure(figsize=(14,6))

    plt.plot(
        df["timestamp"],
        df[f"actual_{metric}"],
        label="Actual Weather",
        linewidth=1
    )

    plt.plot(
        df["timestamp"],
        df[f"pred_{metric}"],
        label="Predicted Weather",
        linewidth=1
    )

    if metric == "temp":
        ylabel = "Temperature (°C)"
    elif metric == "rhum":
        ylabel = "Relative Humidity (%)"
    else:
        ylabel = "Rainfall (mm)"

    plt.xlabel("Date")
    plt.ylabel(ylabel)
    plt.title(
        f"{location.title()}: Actual vs Predicted {ylabel}"
    )
    plt.grid(True, alpha=0.3)
    plt.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR /
        f"{location}_{metric}_actual_vs_predicted.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

def main():

    for location in config.LOCATIONS.keys():

        df = load_results(location)

        for metric in config.TARGET_METRICS:

            plot_actual_vs_predicted(
                df,
                metric,
                location
            )


if __name__ == "__main__":
    main()