"""
Task: explain.py
Integrated Gradients attribution explainability for risk score predictions.
- Compute feature importance via Captum IG
- Map to named sensor features
- Save top sensors as JSON + bar chart PNG
"""

import torch
import numpy as np
import os
import json
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from captum.attr import IntegratedGradients

from data.sample_loader import load_data
from models.cnn_model import CnnModel
from models.conv_mhsa_model import ConvMhsaModel
from utils.logger import get_logger

logger = get_logger("explain")


def compute_integrated_gradients(model, data_loader, device, max_batches=5):
    """
    Compute feature importance using Integrated Gradients.
    """
    model.eval()
    ig = IntegratedGradients(model)
    
    all_attributions = []

    for batch_idx, (batch_X, batch_y) in enumerate(data_loader):
        if batch_idx >= max_batches:
            break

        batch_X = batch_X.to(device).requires_grad_(True)
        
        # IG computes attribution relative to a baseline (default zero)
        # target=0 because output is scalar logit
        attributions = ig.attribute(batch_X, target=0, n_steps=50)
        
        # Absolute importance
        abs_attr = torch.abs(attributions).cpu().detach().numpy()
        
        # Average over batch and time: (num_features,)
        mean_attr = abs_attr.mean(axis=(0, 1))
        all_attributions.append(mean_attr)

    final_importances = np.mean(all_attributions, axis=0)
    return final_importances


def run(config):
    """
    Explainability pipeline.
    """
    logger.info("=" * 60)
    logger.info("NGAFID Explainability (Integrated Gradients)")
    logger.info("=" * 60)

    model_type = config["model"]["type"]
    results_dir = config["paths"]["results"]
    checkpoint_dir = config["paths"]["checkpoints"]
    os.makedirs(results_dir, exist_ok=True)

    device = torch.device(config["training"]["device"] if torch.cuda.is_available() else "cpu")

    # 1. Load data
    logger.info("[1/4] Loading data...")
    _, _, test_loader, num_features, feature_names = load_data(config)

    # 2. Build and load model
    logger.info("[2/4] Loading trained model...")
    seq_length = config["model"]["window_size"]

    if model_type == "cnn":
        model = CnnModel(num_features, seq_length, 1, config["model"].get("cnn"))
    else:
        model = ConvMhsaModel(num_features, seq_length, 1, config["model"].get("conv_mhsa"))

    model_path = os.path.join(checkpoint_dir, f"best_{model_type}_model.pt")
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        model = model.to(device)
    else:
        logger.error(f"No model found at {model_path}!")
        return

    # 3. Compute IG
    logger.info("[3/4] Computing Integrated Gradients...")
    importances = compute_integrated_gradients(model, test_loader, device)

    # 4. Save results
    logger.info("[4/4] Saving results...")
    
    feature_importance = {name: float(importances[i]) for i, name in enumerate(feature_names)}
    sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)

    # Save JSON
    json_path = os.path.join(results_dir, f"{model_type}_feature_importance.json")
    with open(json_path, "w") as f:
        json.dump({"importances": dict(sorted_features)}, f, indent=4)

    # Plot
    top_k = min(20, len(sorted_features))
    names = [x[0] for x in sorted_features[:top_k]]
    vals = [x[1] for x in sorted_features[:top_k]]

    plt.figure(figsize=(10, 8))
    plt.barh(range(top_k), vals[::-1], color="#673AB7")
    plt.yticks(range(top_k), names[::-1])
    plt.xlabel("Mean Absolute Attribution (Integrated Gradients)")
    plt.title(f"Feature Importance: {model_type.upper()}")
    plt.tight_layout()
    plt.savefig(os.path.join(results_dir, f"{model_type}_feature_importance.png"))
    plt.close()

    logger.info("Top 5 sensors:")
    for i, (n, v) in enumerate(sorted_features[:5]):
        logger.info(f"  {i+1}. {n}: {v:.6f}")
    logger.info("Done.")
