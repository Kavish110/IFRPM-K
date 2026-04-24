"""
Trainer: models/trainer.py
- BCEWithLogitsLoss with pos_weight for class imbalance
- Early stopping
- Save model as .pt
- Prediction tracking for evaluation
"""

import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import os
from tqdm import tqdm

from utils.logger import get_logger
from utils.plotter import plot_losses

logger = get_logger("trainer")


def compute_pos_weight(train_loader):
    """
    Compute pos_weight = #negative / #positive from training labels.
    Used for BCEWithLogitsLoss to handle class imbalance.
    """
    all_labels = []
    for _, labels in train_loader:
        all_labels.append(labels.numpy())
    
    if not all_labels:
        return torch.tensor([1.0])
        
    all_labels = np.concatenate(all_labels)
    n_pos = (all_labels == 1).sum()
    n_neg = (all_labels == 0).sum()

    if n_pos == 0:
        logger.warning("No positive samples found! Setting pos_weight=1.0")
        return torch.tensor([1.0])

    pw = n_neg / n_pos
    logger.info(f"Class distribution — neg: {n_neg}, pos: {n_pos}, pos_weight: {pw:.4f}")
    return torch.tensor([pw])


def train_model(model, train_loader, val_loader, config):
    """
    Training loop with BCEWithLogitsLoss + pos_weight and early stopping.
    """
    device = torch.device(config["training"]["device"] if torch.cuda.is_available() else "cpu")
    model = model.to(device)

    epochs = config["training"]["epochs"]
    lr = config["training"]["lr"]
    patience = config["training"]["patience"]
    class_weighting = config["training"].get("class_weighting", True)

    optimizer = optim.Adam(model.parameters(), lr=float(lr))

    if class_weighting:
        pos_weight = compute_pos_weight(train_loader).to(device)
    else:
        pos_weight = torch.tensor([1.0]).to(device)

    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)

    checkpoint_dir = config["paths"]["checkpoints"]
    os.makedirs(checkpoint_dir, exist_ok=True)
    model_type = config["model"]["type"]
    best_model_path = os.path.join(checkpoint_dir, f"best_{model_type}_model.pt")

    best_val_loss = float("inf")
    epochs_no_improve = 0
    train_loss_history = []
    val_loss_history = []

    logger.info(f"Training on {device} | epochs={epochs} | lr={lr}")

    for epoch in range(epochs):
        model.train()
        train_loss = 0.0
        
        pbar = tqdm(train_loader, desc=f"Epoch {epoch+1}/{epochs} [Train]")
        for batch_X, batch_y in pbar:
            batch_X, batch_y = batch_X.to(device), batch_y.to(device).float()

            optimizer.zero_grad()
            outputs = model(batch_X).squeeze(-1)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * batch_X.size(0)
            pbar.set_postfix({"loss": loss.item()})

        train_loss /= len(train_loader.dataset)
        train_loss_history.append(train_loss)

        # Validation
        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for batch_X, batch_y in val_loader:
                batch_X, batch_y = batch_X.to(device), batch_y.to(device).float()
                outputs = model(batch_X).squeeze(-1)
                loss = criterion(outputs, batch_y)
                val_loss += loss.item() * batch_X.size(0)

        val_loss /= len(val_loader.dataset)
        val_loss_history.append(val_loss)

        logger.info(f"Epoch {epoch+1} Summary | Train Loss: {train_loss:.6f} | Val Loss: {val_loss:.6f}")

        # Periodic checkpoint
        epoch_path = os.path.join(checkpoint_dir, f"{model_type}_epoch_{epoch+1}.pt")
        torch.save({
            'epoch': epoch + 1,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'train_loss': train_loss,
            'val_loss': val_loss,
        }, epoch_path)
        logger.info(f"  --> Saved epoch checkpoint to {epoch_path}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            epochs_no_improve = 0
            torch.save(model.state_dict(), best_model_path)
            logger.info(f"  --> Saved best model checkpoint to {best_model_path}")
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                logger.info(f"Early stopping at epoch {epoch+1}")
                break

    # Save loss plot
    results_dir = config["paths"]["results"]
    os.makedirs(results_dir, exist_ok=True)
    plot_losses(train_loss_history, val_loss_history, os.path.join(results_dir, f"{model_type}_loss_plot.png"))

    # Reload best model
    model.load_state_dict(torch.load(best_model_path, map_location=device))
    return model, train_loss_history, val_loss_history


def get_predictions(model, loader, config):
    """
    Get all predictions and ground truth labels from a loader.
    Returns:
        y_true: numpy array of labels
        y_prob: numpy array of risk_scores (sigmoid logit)
    """
    device = torch.device(config["training"]["device"] if torch.cuda.is_available() else "cpu")
    model.eval()
    all_y_true = []
    all_y_prob = []

    with torch.no_grad():
        for batch_X, batch_y in loader:
            batch_X = batch_X.to(device)
            outputs = model(batch_X).squeeze(-1)
            probs = torch.sigmoid(outputs)
            
            all_y_true.append(batch_y.numpy())
            all_y_prob.append(probs.cpu().numpy())

    return np.concatenate(all_y_true), np.concatenate(all_y_prob)
