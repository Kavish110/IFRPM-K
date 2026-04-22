"""
Preprocessing: windowing.py
- Truncate to last max_timesteps per flight
- Pad shorter sequences (zero-pad at front)
- Sliding windows with stride
- Track Master Index and timestep per window for output
"""

import numpy as np
from utils.logger import get_logger

logger = get_logger("windowing")


def truncate_and_pad(sequence, max_timesteps):
    """
    Truncate to the LAST max_timesteps of the flight.
    Pad shorter sequences with zeros at the front.
    """
    seq_len, num_features = sequence.shape

    if seq_len > max_timesteps:
        # Take the last max_timesteps
        return sequence[-max_timesteps:]
    elif seq_len < max_timesteps:
        # Zero-pad at front
        pad_len = max_timesteps - seq_len
        padding = np.zeros((pad_len, num_features), dtype=sequence.dtype)
        return np.vstack([padding, sequence])
    else:
        return sequence


def create_sliding_windows(sequence, window_size, stride):
    """
    Create sliding windows from a sequence.
    """
    seq_len = sequence.shape[0]
    windows = []
    window_starts = []

    if seq_len < window_size:
        # Single padded window
        pad_len = window_size - seq_len
        padded = np.zeros((window_size, sequence.shape[1]), dtype=sequence.dtype)
        padded[pad_len:] = sequence
        windows.append(padded)
        window_starts.append(0)
    else:
        for start in range(0, seq_len - window_size + 1, stride):
            windows.append(sequence[start:start + window_size])
            window_starts.append(start)

    if not windows:
        return np.array([]), []
        
    return np.array(windows), window_starts


def process_flight_windows(flight_data, flight_timesteps, master_index,
                           flight_label, max_timesteps, window_size,
                           stride, horizon_steps):
    """
    Full windowing pipeline for a single flight.
    Uses the timestep at the END of each window for metadata.
    """
    from preprocessing.feature_engineering import assign_window_labels

    seq_len = flight_data.shape[0]

    # 1. Truncate/pad data
    processed = truncate_and_pad(flight_data, max_timesteps)
    effective_len = min(seq_len, max_timesteps)

    # Truncate/pad timesteps similarly
    if len(flight_timesteps) > max_timesteps:
        ts = flight_timesteps[-max_timesteps:]
    elif len(flight_timesteps) < max_timesteps:
        pad_ts = np.zeros(max_timesteps - len(flight_timesteps), dtype=flight_timesteps.dtype)
        ts = np.concatenate([pad_ts, flight_timesteps])
    else:
        ts = flight_timesteps

    # 2. Create sliding windows
    windows, window_starts = create_sliding_windows(processed, window_size, stride)

    if len(windows) == 0:
        return None

    # 3. Assign labels
    targets = assign_window_labels(
        flight_label=flight_label,
        flight_length=effective_len,
        window_starts=window_starts,
        window_size=window_size,
        horizon_steps=horizon_steps,
    )

    # 4. Track metadata — use the timestep at the END of each window
    window_end_timesteps = []
    for start in window_starts:
        end_idx = start + window_size - 1
        if end_idx < len(ts):
            window_end_timesteps.append(ts[end_idx])
        else:
            window_end_timesteps.append(ts[-1])

    return {
        "X": windows,                                         # (num_windows, window_size, num_features)
        "y": np.array(targets, dtype=np.float32),             # (num_windows,)
        "master_index": np.full(len(windows), master_index),  # (num_windows,)
        "timesteps": np.array(window_end_timesteps),          # (num_windows,)
    }
