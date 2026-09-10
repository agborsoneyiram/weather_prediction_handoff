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


def plot_error_histogram(df, metric, location):

    plt.figure(figsize=(8,5))

    plt.hist(
        df[f"{metric}_error"],
        bins=40,
        edgecolor="black"
    )

    plt.axvline(
        0,
        color="red",
        linestyle="--",
        linewidth=2,
        label="Perfect Prediction"
    )

    if metric == "temp":
        xlabel = "Temperature Error (°C)"
    elif metric == "rhum":
        xlabel = "Humidity Error (%)"
    else:
        xlabel = "Rainfall Error (mm)"

    plt.title(
        f"{location.title()}: {metric.upper()} Prediction Error Distribution"
    )

    plt.xlabel(xlabel)
    plt.ylabel("Frequency")

    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR /
        f"{location}_{metric}_error_histogram.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()


def main():

    for location in config.LOCATIONS.keys():

        df = load_results(location)

        for metric in config.TARGET_METRICS:

            plot_error_histogram(
                df,
                metric,
                location
            )


if __name__ == "__main__":
    main()