"""
Preprocessing: clean.py
Handle missing values for NGAFID sensor data.
- Forward fill within each flight group
- Fallback: feature median across dataset
- No smoothing (keep raw signals per spec)
"""

import pandas as pd
import numpy as np
from utils.logger import get_logger

logger = get_logger("clean")


def clean_flight_data(df, feature_cols, group_col="Master Index"):
    """
    Clean sensor data per-flight:
    1. Forward fill within each flight group
    2. Fill any remaining NaN with dataset-wide feature median
    """
    df = df.copy()

    # Compute dataset-wide medians before group operations (for fallback)
    feature_medians = df[feature_cols].median()

    logger.info(f"NaN count before cleaning: {df[feature_cols].isna().sum().sum()}")

    # Forward fill within each flight
    # We use transform which respects the group boundaries
    for col in feature_cols:
        df[col] = df.groupby(group_col)[col].transform(lambda x: x.ffill())

    # Fallback: fill remaining NaN with dataset median
    for col in feature_cols:
        if df[col].isna().any():
            df[col] = df[col].fillna(feature_medians[col])

    # Final safety: fill any remaining with 0
    df[feature_cols] = df[feature_cols].fillna(0)

    logger.info(f"NaN count after cleaning: {df[feature_cols].isna().sum().sum()}")

    return df
