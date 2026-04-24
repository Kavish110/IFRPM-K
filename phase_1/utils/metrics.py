"""
Utils: metrics.py
Classification metrics for risk score prediction.
"""

import json
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import (
    f1_score,
    roc_auc_score,
    average_precision_score,
    precision_recall_curve,
    confusion_matrix,
)


def calculate_classification_metrics(y_true, y_prob, threshold=0.5):
    """
    Compute full classification metrics.
    """
    y_pred = (y_prob >= threshold).astype(int)
    metrics = {}

    # Core scores
    try:
        metrics["f1"] = float(f1_score(y_true, y_pred, zero_division=0))
        if len(np.unique(y_true)) > 1:
            metrics["roc_auc"] = float(roc_auc_score(y_true, y_prob))
            metrics["avg_precision"] = float(average_precision_score(y_true, y_prob))
        else:
            metrics["roc_auc"] = 0.5
            metrics["avg_precision"] = 0.0
    except Exception:
        metrics["f1"] = 0.0
        metrics["roc_auc"] = 0.5
        metrics["avg_precision"] = 0.0

    # Confusion matrix
    try:
        cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
        metrics["confusion_matrix"] = cm.tolist()
        tn, fp, fn, tp = cm.ravel()
        metrics["true_negatives"] = int(tn)
        metrics["false_positives"] = int(fp)
        metrics["false_negatives"] = int(fn)
        metrics["true_positives"] = int(tp)
        
        metrics["precision"] = float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0
        metrics["recall"] = float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0
    except Exception:
        metrics["confusion_matrix"] = [[0, 0], [0, 0]]

    # Statistics
    metrics["n_positive"] = int(y_true.sum())
    metrics["n_negative"] = int(len(y_true) - y_true.sum())
    metrics["n_total"] = int(len(y_true))

    return metrics


def save_precision_recall_curve(y_true, y_prob, filepath):
    """
    Compute and save a Precision-Recall curve as PNG.
    """
    if len(np.unique(y_true)) < 2:
        return

    precision, recall, _ = precision_recall_curve(y_true, y_prob)
    ap = average_precision_score(y_true, y_prob)

    plt.figure(figsize=(8, 6))
    plt.plot(recall, precision, color="#2196F3", lw=2, label=f"AP = {ap:.4f}")
    plt.fill_between(recall, precision, alpha=0.15, color="#2196F3")
    plt.xlabel("Recall")
    plt.ylabel("Precision")
    plt.title("Precision-Recall Curve")
    plt.legend(loc="lower left")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    plt.savefig(filepath, dpi=150)
    plt.close()


def save_metrics(metrics, filepath):
    """Save metrics dict to JSON file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(metrics, f, indent=4)
