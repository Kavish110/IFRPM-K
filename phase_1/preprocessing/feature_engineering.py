"""
Preprocessing: feature_engineering.py
- RUL-based flight labeling from before_after column
- Window-level labeling using horizon
- MinMax scaling across dataset
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from utils.logger import get_logger

logger = get_logger("feature_engineering")


# ─── Sensor feature columns (excluding metadata) ────────────────────────────
SENSOR_FEATURES = [
    "volt1", "volt2", "amp1", "amp2",
    "FQtyL", "FQtyR",
    "E1 FFlow", "E1 OilT", "E1 OilP", "E1 RPM",
    "E1 CHT1", "E1 CHT2", "E1 CHT3", "E1 CHT4",
    "E1 EGT1", "E1 EGT2", "E1 EGT3", "E1 EGT4",
    "OAT", "IAS", "VSpd", "NormAc", "AltMSL",
]

METADATA_COLS = ["Master Index", "timestep", "cluster"]


def get_feature_columns(df_columns):
    """
    Return the list of sensor feature columns that actually exist in the dataframe.
    """
    return [c for c in SENSOR_FEATURES if c in df_columns]


def assign_flight_labels(header_df):
    """
    RUL-based labeling from flight_header.csv:
    - before  → 1 (risk: flight occurs before maintenance)
    - same    → 1 (risk: maintenance day)
    - after   → 0 (healthy: flight occurs after maintenance)
    """
    header_df = header_df.copy()
    header_df["flight_label"] = header_df["before_after"].map({
        "before": 1,
        "same": 1,
        "after": 0,
    })
    # Fill any unmapped values with 0 (safe default)
    header_df["flight_label"] = header_df["flight_label"].fillna(0).astype(int)

    n_risk = (header_df["flight_label"] == 1).sum()
    n_healthy = (header_df["flight_label"] == 0).sum()
    logger.info(f"Flight labels — risk: {n_risk}, healthy: {n_healthy}")

    return header_df


def assign_window_labels(flight_label, flight_length, window_starts,
                         window_size, horizon_steps):
    """
    Assign binary labels to each window within a flight.

    For risk flights (flight_label=1):
        - If the window's END position is within `horizon_steps` of the
          flight's end → target = 1
        - Otherwise → target = 0

    For healthy flights (flight_label=0):
        - All windows → target = 0
    """
    targets = []
    for start in window_starts:
        if flight_label == 0:
            targets.append(0)
        else:
            # Window end position relative to flight start
            window_end = start + window_size
            # Distance from window end to flight end
            remaining = flight_length - window_end
            if remaining <= horizon_steps:
                targets.append(1)
            else:
                targets.append(0)
    return targets


def fit_minmax_scaler(df, feature_cols):
    """
    Fit a MinMaxScaler [0, 1] on the dataset and return the fitted scaler.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(df[feature_cols].values)
    logger.info("MinMaxScaler fitted on dataset")
    return scaler


def apply_minmax_scaler(df, feature_cols, scaler):
    """
    Apply a pre-fitted MinMaxScaler to the dataframe.
    """
    df = df.copy()
    df[feature_cols] = scaler.transform(df[feature_cols].values)
    return df
