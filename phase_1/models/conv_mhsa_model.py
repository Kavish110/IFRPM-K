"""
Model: conv_mhsa_model.py
1D Convolutional Embedding + Multi-Head Self-Attention.
"""

import torch
import torch.nn as nn
import math

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer('pe', pe)

    def forward(self, x):
        # x: (batch, seq_len, d_model)
        x = x + self.pe[:, :x.size(1)]
        return x

class ConvMhsaModel(nn.Module):
    """
    Combines Conv1d features with Transformer MHSA.
    Architecture:
        Input (batch, window_size, num_features)
        → Conv1d temporal embedding → (batch, embed_dim, window_size)
        → Permute → (batch, window_size, embed_dim)
        → Positional encoding
        → Transformer Encoder layers (MHSA + FFN)
        → Global Average Pooling (over time)
        → FC → logit
    """
    def __init__(self, num_features, seq_length, num_classes=1, config=None):
        super().__init__()
        
        embed_dim = config.get("embed_dim", 64) if config else 64
        num_heads = config.get("num_heads", 4) if config else 4
        num_layers = config.get("num_layers", 2) if config else 2
        conv_kernel = config.get("conv_kernel", 5) if config else 5
        dropout = config.get("dropout", 0.1) if config else 0.1
        
        # Temporal Embedding: projects raw sensors into a latent space
        # padding=kernel//2 preserves sequence length
        self.conv_embed = nn.Sequential(
            nn.Conv1d(num_features, embed_dim, kernel_size=conv_kernel, padding=conv_kernel//2),
            nn.BatchNorm1d(embed_dim),
            nn.ReLU(),
            nn.Dropout(dropout)
        )
        
        self.pos_encoder = PositionalEncoding(embed_dim, max_len=seq_length)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=embed_dim,
            nhead=num_heads,
            dim_feedforward=embed_dim * 4,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.global_pool = nn.AdaptiveAvgPool1d(1)
        self.fc = nn.Linear(embed_dim, num_classes)

    def forward(self, x):
        # x: (batch, seq_len, num_features)
        
        # 1. Conv Embedding
        x = x.permute(0, 2, 1)  # (batch, num_features, seq_len)
        x = self.conv_embed(x)   # (batch, embed_dim, seq_len)
        
        # 2. Transformer Logic
        x = x.permute(0, 2, 1)  # (batch, seq_len, embed_dim)
        x = self.pos_encoder(x)
        x = self.transformer_encoder(x) # (batch, seq_len, embed_dim)
        
        # 3. Pooling and Output
        x = x.permute(0, 2, 1)  # (batch, embed_dim, seq_len)
        x = self.global_pool(x)  # (batch, embed_dim, 1)
        x = torch.flatten(x, 1)  # (batch, embed_dim)
        
        x = self.fc(x)           # (batch, num_classes)
        return x
