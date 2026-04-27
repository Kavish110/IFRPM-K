"""Load .pkl model artifacts at startup."""

import pickle
import sys
from pathlib import Path

try:
    import tensorflow as tf
except ImportError:
    tf = None

from app.config import settings

_models: dict = {}


def load_models() -> None:
    """Deserialize all .pkl files from the models directory."""
    model_dir = Path(settings.model_dir)
    if not model_dir.exists():
        return
    for path in model_dir.glob("*.pkl"):
        with open(path, "rb") as f:
            _models[path.stem] = pickle.load(f)
            
    if tf is not None:
        for path in model_dir.glob("*.h5"):
            _models[path.stem] = tf.keras.models.load_model(str(path))
            
    if _models:
        print(f"[ml] Loaded: {list(_models.keys())}")
    else:
        print("[ml] No models found — stub inference active.")


def models_loaded() -> bool:
    """Return True when at least one model artifact is loaded."""
    return len(_models) > 0


def get_model(name: str):
    """Return a model by name; raises KeyError if not loaded."""
    if name not in _models:
        raise KeyError(f"Model '{name}' not loaded.")
    return _models[name]
