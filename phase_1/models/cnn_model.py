"""
Model: cnn_model.py
1D CNN with Residual Blocks and Global Average Pooling.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class ResidualBlock(nn.Module):
    """
    1D Residual Block:
    Conv1d → BN → ReLU → Conv1d → BN + skip connection → ReLU
    """

    def __init__(self, in_channels, out_channels, kernel_size=3, dropout=0.1):
        super().__init__()
        padding = kernel_size // 2
        self.conv1 = nn.Conv1d(in_channels, out_channels, kernel_size, padding=padding)
        self.bn1 = nn.BatchNorm1d(out_channels)
        self.conv2 = nn.Conv1d(out_channels, out_channels, kernel_size, padding=padding)
        self.bn2 = nn.BatchNorm1d(out_channels)
        self.dropout = nn.Dropout(dropout)
        
        # Shortcut connection to match dimensions if needed
        self.shortcut = nn.Sequential()
        if in_channels != out_channels:
            self.shortcut = nn.Sequential(
                nn.Conv1d(in_channels, out_channels, kernel_size=1),
                nn.BatchNorm1d(out_channels)
            )

    def forward(self, x):
        residual = self.shortcut(x)
        out = F.relu(self.bn1(self.conv1(x)))
        out = self.dropout(out)
        out = self.bn2(self.conv2(out))
        out += residual  # skip connection
        out = F.relu(out)
        return out


class CnnModel(nn.Module):
    """
    1D CNN for risk score prediction.
    Architecture:
        Input (batch, window_size, num_features)
        → permute → (batch, num_features, window_size)
        → Stem: Conv1d + BN + ReLU
        → ResidualBlocks (parameterized by config filters)
        → Global Average Pooling
        → Dropout → FC → logit (scalar)
    """

    def __init__(self, num_features, seq_length, num_classes=1, config=None):
        super().__init__()

        filters = config.get("filters", [64, 128, 256]) if config else [64, 128, 256]
        kernel_size = config.get("kernel_size", 3) if config else 3
        dropout = config.get("dropout", 0.3) if config else 0.3

        padding = kernel_size // 2
        
        # Stem
        self.stem = nn.Sequential(
            nn.Conv1d(num_features, filters[0], kernel_size, padding=padding),
            nn.BatchNorm1d(filters[0]),
            nn.ReLU()
        )
        
        # Residual Stages
        layers = []
        current_channels = filters[0]
        for f in filters:
            layers.append(ResidualBlock(current_channels, f, kernel_size, dropout))
            # We add a pooling layer after each residual block to reduce temporal resolution
            layers.append(nn.MaxPool1d(2))
            current_channels = f
            
        self.res_layers = nn.Sequential(*layers)
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.dropout = nn.Dropout(dropout)
        self.fc = nn.Linear(filters[-1], num_classes)

    def forward(self, x):
        # x shape: (batch, window_size, num_features)
        x = x.permute(0, 2, 1)  # (batch, num_features, window_size)
        
        x = self.stem(x)
        x = self.res_layers(x)
        
        x = self.global_pool(x)  # (batch, final_filters, 1)
        x = torch.flatten(x, 1)  # (batch, final_filters)
        
        x = self.dropout(x)
        x = self.fc(x)           # (batch, num_classes)
        return x
