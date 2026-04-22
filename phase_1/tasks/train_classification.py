"""
Task: train_classification.py
Unified risk_score prediction pipeline:
1. Load data → preprocess → window
2. Build model (CNN or ConvMHSA)
3. Train with class weighting + balanced sampling
4. Evaluate → compute metrics
5. Save risk_scores.csv, metrics.json, model.pt
"""

import torch
import numpy as np
import pandas as pd
import os

from data.sample_loader import load_data
from models.cnn_model import CnnModel
from models.conv_mhsa_model import ConvMhsaModel
from models.trainer import train_model, get_predictions
from utils.logger import get_logger
from utils.metrics import (
    calculate_classification_metrics,
    save_precision_recall_curve,
    save_metrics,
)

logger = get_logger("train_classification")


def build_model(num_features, config):
    """Instantiate the model based on config."""
    model_type = config["model"]["type"]
    seq_length = config["model"]["window_size"]

    if model_type == "cnn":
        model = CnnModel(
            num_features=num_features,
            seq_length=seq_length,
            num_classes=1,
            config=config["model"].get("cnn"),
        )
    elif model_type == "conv_mhsa":
        model = ConvMhsaModel(
            num_features=num_features,
            seq_length=seq_length,
            num_classes=1,
            config=config["model"].get("conv_mhsa"),
        )
    else:
        raise ValueError(f"Unknown model type: {model_type}. Choose 'cnn' or 'conv_mhsa'.")

    total_params = sum(p.numel() for p in model.parameters())
    logger.info(f"Model: {model_type} | Parameters: {total_params:,}")
    return model


def save_risk_scores(test_loader, all_probs, results_dir):
    """
    Save risk_scores.csv with columns: Master Index, timestep, risk_score
    """
    dataset = test_loader.dataset
    mi = dataset.master_indices
    ts = dataset.timesteps

    if mi is None or ts is None:
        logger.warning("No metadata available — saving risk scores without Master Index / timestep")
        df = pd.DataFrame({"risk_score": all_probs})
    else:
        df = pd.DataFrame({
            "Master Index": mi.astype(int),
            "timestep": ts.astype(int),
            "risk_score": np.round(all_probs, 6),
        })

    os.makedirs(results_dir, exist_ok=True)
    output_path = os.path.join(results_dir, "risk_scores.csv")
    df.to_csv(output_path, index=False)
    logger.info(f"Saved risk scores to {output_path} ({len(df)} rows)")


def run(config):
    """Main entry point for the risk-score prediction pipeline."""
    logger.info("=" * 60)
    logger.info("NGAFID Risk Score Prediction Pipeline")
    logger.info("=" * 60)

    model_type = config["model"]["type"]
    results_dir = config["paths"]["results"]
    os.makedirs(results_dir, exist_ok=True)

    # 1. Load data
    logger.info("[1/5] Loading and preprocessing data...")
    train_loader, val_loader, test_loader, num_features, feature_names = load_data(config)
    logger.info(f"Features loaded: {num_features}")

    # 2. Build model
    logger.info("[2/5] Building model...")
    model = build_model(num_features, config)

    # 3. Train
    logger.info("[3/5] Training...")
    model, train_losses, val_losses = train_model(model, train_loader, val_loader, config)

    # 4. Evaluate
    logger.info("[4/5] Evaluating on test set...")
    all_targets, all_probs = get_predictions(model, test_loader, config)

    # Compute metrics
    metrics = calculate_classification_metrics(all_targets, all_probs)
    metrics.update({
        "model_type": model_type,
        "window_size": config["model"]["window_size"],
        "stride": config["model"]["stride"],
        "horizon_steps": config["task"]["horizon_steps"],
        "epochs_trained": len(train_losses),
        "final_train_loss": float(train_losses[-1]),
        "final_val_loss": float(val_losses[-1])
    })

    logger.info(f"Test Metrics: F1={metrics['f1']:.4f}, ROC-AUC={metrics['roc_auc']:.4f}, AP={metrics['avg_precision']:.4f}")

    # 5. Save outputs
    logger.info("[5/5] Saving outputs...")
    
    metrics_path = os.path.join(results_dir, f"{model_type}_metrics.json")
    save_metrics(metrics, metrics_path)

    pr_path = os.path.join(results_dir, f"{model_type}_pr_curve.png")
    save_precision_recall_curve(all_targets, all_probs, pr_path)

    save_risk_scores(test_loader, all_probs, results_dir)

    logger.info("=" * 60)
    logger.info("Pipeline complete!")
    logger.info(f"  Model saved to: {config['paths']['checkpoints']}")
    logger.info(f"  Risk Scores:  {results_dir}/risk_scores.csv")
    logger.info("=" * 60)
