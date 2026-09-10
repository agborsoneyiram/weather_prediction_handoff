import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import config
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.metrics import (
    confusion_matrix,
    ConfusionMatrixDisplay,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

GRAPH_DIR = config.VALIDATION_DIR / "graphs"
GRAPH_DIR.mkdir(parents=True, exist_ok=True)

def load_results(location):

    file = config.VALIDATION_DIR / f"{location}_classified.csv"

    return pd.read_csv(file)

def create_confusion_matrix(df, location):

    labels = [
        "No Rain",
        "Light",
        "Moderate",
        "Heavy"
    ]

    cm = confusion_matrix(
        df["actual_class"],
        df["predicted_class"],
        labels=labels
    )

    disp = ConfusionMatrixDisplay(
        confusion_matrix=cm,
        display_labels=labels
    )

    plt.figure(figsize=(7,7))

    disp.plot(cmap="Blues")

    plt.title(
        f"{location.title()} Rainfall Classification"
    )

    plt.tight_layout()

    plt.savefig(
        GRAPH_DIR /
        f"{location}_confusion_matrix.png",
        dpi=300,
        bbox_inches="tight"
    )

    plt.close()

def print_metrics(df):

    accuracy = accuracy_score(
        df["actual_class"],
        df["predicted_class"]
    )

    precision = precision_score(
        df["actual_class"],
        df["predicted_class"],
        average="weighted",
        zero_division=0
    )

    recall = recall_score(
        df["actual_class"],
        df["predicted_class"],
        average="weighted",
        zero_division=0
    )

    f1 = f1_score(
        df["actual_class"],
        df["predicted_class"],
        average="weighted",
        zero_division=0
    )

    print(f"Accuracy : {accuracy:.3f}")
    print(f"Precision: {precision:.3f}")
    print(f"Recall   : {recall:.3f}")
    print(f"F1 Score : {f1:.3f}")

def main():

    for location in config.LOCATIONS.keys():

        print(f"\n{location.upper()}")

        df = load_results(location)

        create_confusion_matrix(
            df,
            location
        )

        print_metrics(df)

if __name__ == "__main__":
    main()