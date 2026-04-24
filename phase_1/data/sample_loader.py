"""
Data loader: sample_loader.py
- Load parquet with Dask, header with pandas
- Flight-level sampling using size_ratio
- Join on Master Index
- Preprocess → window → PyTorch DataLoaders
"""

import pandas as pd
import numpy as np
import os
import dask.dataframe as dd
import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from sklearn.model_selection import train_test_split

from preprocessing.clean import clean_flight_data
from preprocessing.feature_engineering import (
    get_feature_columns,
    assign_flight_labels,
    fit_minmax_scaler,
    apply_minmax_scaler,
)
from preprocessing.windowing import process_flight_windows
from utils.logger import get_logger

logger = get_logger("sample_loader")


class NGAFIDWindowDataset(Dataset):
    """PyTorch dataset wrapping pre-computed sliding windows."""

    def __init__(self, X, y, master_indices=None, timesteps=None):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)
        self.master_indices = master_indices
        self.timesteps = timesteps

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        # Add metadata to return if needed, but trainer expects (X, y)
        return self.X[idx], self.y[idx]


def load_data(config):
    """
    Full data loading pipeline:
    1. Load header CSV (pandas)
    2. Load parquet data (Dask)
    3. Flight-level sampling
    4. Join header → data on Master Index
    5. Clean, scale, window
    6. Split train/val/test
    7. Return DataLoaders
    """
    header_path = config["dataset"]["header_path"]
    data_path = config["dataset"]["data_path"]
    size_ratio = config["dataset"]["size_ratio"]
    debug = config["dataset"]["debug"]
    seed = config["dataset"].get("seed", 42)

    window_size = config["model"]["window_size"]
    stride = config["model"]["stride"]
    max_timesteps = config["model"]["max_timesteps"]
    horizon_steps = config["task"]["horizon_steps"]
    batch_size = config["training"]["batch_size"]
    oversampling = config["training"].get("oversampling", True)

    # 1. Load header
    logger.info(f"Loading flight header from: {header_path}")
    header_df = pd.read_csv(header_path)
    header_df = assign_flight_labels(header_df)

    all_flight_ids = header_df["Master Index"].unique()
    logger.info(f"Total flights in header: {len(all_flight_ids)}")

    # 2. Flight-level sampling
    if debug:
        sample_ratio = min(size_ratio, 0.05)
        logger.info(f"DEBUG mode: sampling {sample_ratio*100:.1f}% of flights")
    else:
        sample_ratio = size_ratio

    np.random.seed(seed)
    n_sample = max(1, int(len(all_flight_ids) * sample_ratio))
    sampled_ids = np.random.choice(all_flight_ids, size=n_sample, replace=False)
    sampled_ids = sorted(sampled_ids)
    logger.info(f"Sampled {len(sampled_ids)} flights")

    # Filter header
    header_sampled = header_df[header_df["Master Index"].isin(sampled_ids)].copy()

    # 3. Load parquet with Dask
    logger.info(f"Loading parquet data from: {data_path}")
    ddf = dd.read_parquet(os.path.join(data_path, "*.parquet"), engine="pyarrow")
    
    # Ensure Master Index is a column to use .isin() reliably
    if "Master Index" not in ddf.columns:
        ddf = ddf.reset_index()

    # Filter in Dask using map_partitions to bypass potential metadata issues with .isin() in dask-expr
    # Master Index should be a column after reset_index
    ddf_sampled = ddf.map_partitions(lambda pdf: pdf[pdf["Master Index"].isin(sampled_ids)])

    # 4. Compute to Pandas (Memory efficient because we filtered first)
    logger.info("Computing sampled data to pandas...")
    df = ddf_sampled.compute()
    logger.info(f"Loaded {len(df)} rows for {df['Master Index'].nunique()} flights")

    if len(df) == 0:
        raise RuntimeError("No data found for sampled flights!")

    # 5. Identify feature columns
    feature_cols = get_feature_columns(df.columns)
    logger.info(f"Sensor features ({len(feature_cols)})")

    # 6. Join header info
    df = df.merge(
        header_sampled[["Master Index", "flight_label", "before_after"]],
        on="Master Index",
        how="left",
    )

    # 7. Sort and Clean
    df = df.sort_values(["Master Index", "timestep"]).reset_index(drop=True)
    df = clean_flight_data(df, feature_cols)

    # 8. MinMax Scale
    scaler = fit_minmax_scaler(df, feature_cols)
    df = apply_minmax_scaler(df, feature_cols, scaler)

    # 9. Split flights (70/15/15)
    unique_ids = df["Master Index"].unique()
    train_ids, temp_ids = train_test_split(unique_ids, test_size=0.3, random_state=seed)
    val_ids, test_ids = train_test_split(temp_ids, test_size=0.5, random_state=seed)

    logger.info(f"Split — train: {len(train_ids)}, val: {len(val_ids)}, test: {len(test_ids)}")

    # 10. Windowing function
    def _build_windows(flight_ids, label=""):
        all_X, all_y, all_mi, all_ts = [], [], [], []
        for fid in flight_ids:
            fdata = df[df["Master Index"] == fid]
            if len(fdata) == 0: continue
            
            flight_label = fdata["flight_label"].iloc[0]
            result = process_flight_windows(
                flight_data=fdata[feature_cols].values,
                flight_timesteps=fdata["timestep"].values,
                master_index=fid,
                flight_label=flight_label,
                max_timesteps=max_timesteps,
                window_size=window_size,
                stride=stride,
                horizon_steps=horizon_steps,
            )
            if result:
                all_X.append(result["X"])
                all_y.append(result["y"])
                all_mi.append(result["master_index"])
                all_ts.append(result["timesteps"])
        
        if not all_X: return None, None, None, None
        
        return (np.concatenate(all_X), np.concatenate(all_y), 
                np.concatenate(all_mi), np.concatenate(all_ts))

    # Build split windows
    X_train, y_train, mi_train, ts_train = _build_windows(train_ids, "Train")
    X_val, y_val, mi_val, ts_val = _build_windows(val_ids, "Val")
    X_test, y_test, mi_test, ts_test = _build_windows(test_ids, "Test")

    if X_train is None:
        raise RuntimeError("No training windows created. Check parameters.")

    # 11. Create Datasets and Loaders
    train_ds = NGAFIDWindowDataset(X_train, y_train, mi_train, ts_train)
    val_ds = NGAFIDWindowDataset(X_val, y_val, mi_val, ts_val)
    test_ds = NGAFIDWindowDataset(X_test, y_test, mi_test, ts_test)

    # Balanced Sampler
    sampler = None
    if oversampling and len(np.unique(y_train)) > 1:
        class_sample_count = np.array([len(np.where(y_train == t)[0]) for t in np.unique(y_train)])
        weight = 1. / class_sample_count
        samples_weight = np.array([weight[int(t)] for t in y_train])
        sampler = WeightedRandomSampler(torch.from_numpy(samples_weight).double(), len(samples_weight))
        logger.info(f"Oversampling enabled (class counts: {class_sample_count})")

    train_loader = DataLoader(train_ds, batch_size=batch_size, sampler=sampler, shuffle=(sampler is None))
    val_loader = DataLoader(val_ds, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_ds, batch_size=batch_size, shuffle=False)

    return train_loader, val_loader, test_loader, len(feature_cols), feature_cols
