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

    return pd.read_csv(file)

def scatter_plot(df, metric, location):

    plt.figure(figsize=(7,7))

    plt.scatter(
        df[f"actual_{metric}"],
        df[f"pred_{metric}"],
        alpha=0.4,
        s=12,
        label="Predictions",
        edgecolors="black",
        linewidths=0.2
    )

    minimum = min(
        df[f"actual_{metric}"].min(),
        df[f"pred_{metric}"].min()
    )

    maximum = max(
        df[f"actual_{metric}"].max(),
        df[f"pred_{metric}"].max()
    )

    plt.plot(
        [minimum, maximum],
        [minimum, maximum],
        "r--",
        linewidth=2,
        label="Perfect Prediction"
    )

    if metric == "temp":
        label = "Temperature (°C)"
    elif metric == "rhum":
        label = "Relative Humidity (%)"
    else:
        label = "Rainfall (mm)"

    plt.xlabel(f"Actual {label}")
    plt.ylabel(f"Predicted {label}")

    plt.title(
        f"{location.title()}: Predicted vs Actual {label}"
    )

    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR /
        f"{location}_{metric}_scatter.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

def main():

    for location in config.LOCATIONS.keys():

        df = load_results(location)

        for metric in config.TARGET_METRICS:

            scatter_plot(
                df,
                metric,
                location
            )

if __name__ == "__main__":
    main()