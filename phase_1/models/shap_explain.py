"""
Phase 1 — SHAP Explainability
Team Kansas IFRPM

Loads trained best_lstm_FDx.pt checkpoints and computes SHAP values
using GradientExplainer (works directly with PyTorch + sequences).

Outputs per dataset:
  results/shap_bar_FD001.png        — mean |SHAP| per feature (top 20)
  results/shap_heatmap_FD001.png    — SHAP values across test samples
  results/shap_values_FD001.npy     — raw SHAP array (for dashboard use)
  results/shap_top_features_FD001.json — top 20 features ranked

Run
---
    cd /home/dmohile/capstone/phase_1
    PYTHONPATH=/home/dmohile/capstone/phase_1 python models/shap_explain.py
"""

import os
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import shap
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings("ignore")

from utils.logger import get_logger

logger = get_logger("shap_explain")

# ─────────────────────────────────────────────
# PATHS  — must match lstm_rul.py exactly
# ─────────────────────────────────────────────
DATA_DIR       = "/home/dmohile/capstone/data"
MODEL_DIR      = "/home/dmohile/capstone/phase_1/models"
RESULTS_DIR    = "/home/dmohile/capstone/phase_1/results"

os.makedirs(RESULTS_DIR, exist_ok=True)

# ─────────────────────────────────────────────
# CONSTANTS  — must match lstm_rul.py exactly
# ─────────────────────────────────────────────
COLS = (
    ["unit", "cycle"]
    + ["op1", "op2", "op3"]
    + ["s" + str(i) for i in range(1, 22)]
)
DROP_SENSORS    = ["s1", "s5", "s6", "s10", "s16", "s18", "s19"]
DROP_COLS       = DROP_SENSORS + ["op3"]
FEATURE_SENSORS = [s for s in ["s" + str(i) for i in range(1, 22)]
                   if s not in DROP_SENSORS]
RUL_CLIP    = 125
WINDOW_SIZE = 30
BATCH_SIZE  = 256


# ─────────────────────────────────────────────
# MODEL  — identical to lstm_rul.py
# ─────────────────────────────────────────────
class BiLSTM(nn.Module):
    def __init__(self, input_size, hidden1=128, hidden2=64, dropout=0.3):
        super().__init__()
        self.lstm1   = nn.LSTM(input_size,  hidden1, batch_first=True, bidirectional=True)
        self.lstm2   = nn.LSTM(hidden1 * 2, hidden2, batch_first=True, bidirectional=True)
        self.dropout = nn.Dropout(dropout)
        self.fc1     = nn.Linear(hidden2 * 2, 64)
        self.fc2     = nn.Linear(64, 1)
        self.relu    = nn.ReLU()

    def forward(self, x):
        out, _ = self.lstm1(x)
        out, _ = self.lstm2(out)
        out = self.dropout(out[:, -1, :])
        out = self.relu(self.fc1(out))
        return self.fc2(out).squeeze(1)


# ─────────────────────────────────────────────
# DATA LOADING & PREPROCESSING
# ─────────────────────────────────────────────
def load_and_preprocess(fd):
    """Load + preprocess test data — mirrors lstm_rul.py exactly."""
    train = pd.read_csv(f"{DATA_DIR}/train_{fd}.txt",
                        sep=r"\s+", header=None, names=COLS, engine="python")
    test  = pd.read_csv(f"{DATA_DIR}/test_{fd}.txt",
                        sep=r"\s+", header=None, names=COLS, engine="python")
    rul   = pd.read_csv(f"{DATA_DIR}/RUL_{fd}.txt",
                        sep=r"\s+", header=None, names=["RUL"], engine="python")

    # Train RUL labels
    max_cycle = train.groupby("unit")["cycle"].max().rename("max_cycle")
    train = train.merge(max_cycle, on="unit")
    train["RUL"] = (train["max_cycle"] - train["cycle"]).clip(upper=RUL_CLIP)
    train.drop(columns=["max_cycle"], inplace=True)

    # Test RUL labels
    last_cycles = test.groupby("unit")["cycle"].max().reset_index()
    last_cycles.columns = ["unit", "last_cycle"]
    rul["unit"] = last_cycles["unit"].values
    test = test.merge(last_cycles, on="unit")
    test = test.merge(rul, on="unit")
    test["RUL"] = (test["RUL"] + test["last_cycle"] - test["cycle"]).clip(0, RUL_CLIP)
    test.drop(columns=["last_cycle"], inplace=True)

    # Drop unused columns + rolling features
    for df in [train, test]:
        df.drop(columns=DROP_COLS, errors="ignore", inplace=True)

    def add_rolling(df):
        new_cols = {}
        for s in FEATURE_SENSORS:
            grp = df.groupby("unit")[s]
            new_cols[f"{s}_mean"] = grp.transform(lambda x: x.rolling(5, min_periods=1).mean())
            new_cols[f"{s}_std"]  = grp.transform(lambda x: x.rolling(5, min_periods=1).std().fillna(0))
            new_cols[f"{s}_min"]  = grp.transform(lambda x: x.rolling(5, min_periods=1).min())
            new_cols[f"{s}_max"]  = grp.transform(lambda x: x.rolling(5, min_periods=1).max())
        return pd.concat([df, pd.DataFrame(new_cols, index=df.index)], axis=1)

    train = add_rolling(train)
    test  = add_rolling(test)

    exclude      = {"unit", "cycle", "RUL"}
    feature_cols = [c for c in train.columns if c not in exclude]

    scaler = MinMaxScaler()
    train[feature_cols] = scaler.fit_transform(train[feature_cols])
    test[feature_cols]  = scaler.transform(test[feature_cols])

    return test, feature_cols


def build_windows(df, feature_cols, window=WINDOW_SIZE, max_windows=500):
    """
    Build sliding windows from test data.
    Capped at max_windows for SHAP speed — SHAP is expensive on sequences.
    """
    X, y = [], []
    for _, grp in df.groupby("unit"):
        grp  = grp.sort_values("cycle")
        feat = grp[feature_cols].values
        rul  = grp["RUL"].values
        for i in range(len(grp) - window + 1):
            X.append(feat[i: i + window])
            y.append(rul[i + window - 1])

    X = np.array(X, dtype=np.float32)
    y = np.array(y, dtype=np.float32)

    # Subsample for SHAP speed
    if len(X) > max_windows:
        idx = np.random.choice(len(X), max_windows, replace=False)
        X, y = X[idx], y[idx]

    logger.info(f"  SHAP windows: {X.shape}")
    return X, y


# ─────────────────────────────────────────────
# SHAP COMPUTATION
# ─────────────────────────────────────────────
def compute_shap(model, X_tensor, background_size=50):
    """
    Use GradientExplainer — best choice for LSTM + PyTorch.
    Background = small random subset used as reference baseline.
    """
    model.eval()
    bg_idx  = np.random.choice(len(X_tensor), min(background_size, len(X_tensor)), replace=False)
    background = X_tensor[bg_idx]

    explainer   = shap.GradientExplainer(model, background)
    shap_values = explainer.shap_values(X_tensor)
    # shap_values shape: (n_samples, window_size, n_features)
    return np.array(shap_values)


# ─────────────────────────────────────────────
# PLOTS
# ─────────────────────────────────────────────
def plot_shap_bar(shap_values, feature_cols, fd, top_n=20):
    """
    Bar chart: mean |SHAP| per feature, averaged over window timesteps.
    Shows which features drive predictions the most.
    """
    # Average over timesteps → (n_samples, n_features)
    mean_over_time = np.abs(shap_values).mean(axis=1)
    # Average over samples → (n_features,)
    importance = mean_over_time.mean(axis=0)

    # Rank and take top N
    ranked_idx  = np.argsort(importance)[::-1][:top_n]
    top_names   = [feature_cols[i] for i in ranked_idx]
    top_vals    = importance[ranked_idx]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(top_n), top_vals[::-1], color="steelblue", alpha=0.8)
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_names[::-1], fontsize=9)
    ax.set_xlabel("Mean |SHAP value|")
    ax.set_title(f"Feature Importance — Bi-LSTM {fd}\n(Top {top_n} features by mean |SHAP|)")
    ax.grid(True, axis="x", alpha=0.3)
    fig.tight_layout()

    path = f"{RESULTS_DIR}/shap_bar_{fd}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info(f"  Saved: {path}")

    return top_names, top_vals.tolist()


def plot_shap_heatmap(shap_values, feature_cols, fd, top_n=15):
    """
    Heatmap: SHAP values for top N features across test samples.
    Rows = features, Cols = samples. Colour = SHAP direction + magnitude.
    """
    mean_over_time = shap_values.mean(axis=1)          # (n_samples, n_features)
    importance     = np.abs(mean_over_time).mean(axis=0)
    top_idx        = np.argsort(importance)[::-1][:top_n]

    heatmap_data = mean_over_time[:, top_idx].T        # (top_n, n_samples)
    top_names    = [feature_cols[i] for i in top_idx]

    fig, ax = plt.subplots(figsize=(14, 6))
    im = ax.imshow(heatmap_data, aspect="auto", cmap="RdBu_r",
                   vmin=-np.percentile(np.abs(heatmap_data), 95),
                   vmax= np.percentile(np.abs(heatmap_data), 95))
    ax.set_yticks(range(top_n))
    ax.set_yticklabels(top_names, fontsize=9)
    ax.set_xlabel("Test samples")
    ax.set_title(f"SHAP Value Heatmap — Bi-LSTM {fd}\n(Top {top_n} features, red=increases RUL pred, blue=decreases)")
    plt.colorbar(im, ax=ax, label="SHAP value")
    fig.tight_layout()

    path = f"{RESULTS_DIR}/shap_heatmap_{fd}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    logger.info(f"  Saved: {path}")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    np.random.seed(42)
    torch.manual_seed(42)

    all_top_features = {}

    for fd in ["FD001", "FD002", "FD003", "FD004"]:
        logger.info(f"\n{'='*50}\nSHAP — {fd}\n{'='*50}")

        # 1. Load data
        test_df, feature_cols = load_and_preprocess(fd)
        n_features = len(feature_cols)
        logger.info(f"  Features: {n_features}")

        # 2. Load trained model
        model_path = f"{MODEL_DIR}/best_lstm_{fd}.pt"
        if not os.path.exists(model_path):
            logger.warning(f"  No checkpoint found at {model_path} — skipping {fd}")
            continue

        model = BiLSTM(input_size=n_features)
        model.load_state_dict(torch.load(model_path, map_location="cpu"))
        model.eval()
        logger.info(f"  Loaded: {model_path}")

        # 3. Build windows
        X, _ = build_windows(test_df, feature_cols, max_windows=300)
        X_tensor = torch.tensor(X, dtype=torch.float32)

        # 4. Compute SHAP
        logger.info("  Computing SHAP values (GradientExplainer)...")
        shap_values = compute_shap(model, X_tensor, background_size=50)
        logger.info(f"  SHAP shape: {shap_values.shape}")

        # 5. Save raw SHAP values (frontend / Phase 2 can use these)
        npy_path = f"{RESULTS_DIR}/shap_values_{fd}.npy"
        np.save(npy_path, shap_values)
        logger.info(f"  Saved raw SHAP: {npy_path}")

        # 6. Bar chart + heatmap
        top_names, top_vals = plot_shap_bar(shap_values, feature_cols, fd, top_n=20)
        plot_shap_heatmap(shap_values, feature_cols, fd, top_n=15)

        # 7. Save top features as JSON (for dashboard API)
        top_features = [
            {"feature": name, "importance": round(val, 6)}
            for name, val in zip(top_names, top_vals)
        ]
        json_path = f"{RESULTS_DIR}/shap_top_features_{fd}.json"
        with open(json_path, "w") as f:
            json.dump(top_features, f, indent=4)
        logger.info(f"  Saved JSON: {json_path}")

        all_top_features[fd] = top_names[:5]

    # Summary — which sensors matter most per dataset
    logger.info("\n" + "="*55)
    logger.info("  TOP 5 FEATURES PER DATASET")
    logger.info("="*55)
    for fd, features in all_top_features.items():
        logger.info(f"  {fd}: {', '.join(features)}")
    logger.info("="*55)
    logger.info(f"\nAll SHAP outputs saved to: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
