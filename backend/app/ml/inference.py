"""Model inference entry point."""

import pandas as pd

from app.ml.loader import get_model, models_loaded


def predict_rul(sensor_df: pd.DataFrame) -> float:
    """Return estimated RUL in engine cycles for the given sensor window."""
    if not models_loaded():
        from app.ml.stub import predict_rul as _stub
        return _stub(sensor_df)

    ensemble_targets = ["ngafid", "battery_xgb_model"]
    preds = []

    for name in ensemble_targets:
        try:
            model = get_model(name)
        except KeyError:
            continue

        try:
            raw_pred = model.predict(sensor_df.values.reshape(1, -1))
            if hasattr(raw_pred, "flatten"):
                val = float(raw_pred.flatten()[0])
            elif hasattr(raw_pred, "__len__") and len(raw_pred) > 0:
                val = float(raw_pred[0])
            else:
                val = float(raw_pred)
            preds.append(val)
        except Exception as e:
            print(f"Error predicting with {name}: {e}")

    if preds:
        return sum(preds) / len(preds)

    from app.ml.stub import predict_rul as _stub
    return _stub(sensor_df)


def detect_anomaly(sensor_df: pd.DataFrame) -> bool:
    """Return True if the sensor window is anomalous."""
    if models_loaded():
        model = get_model("anomaly_model")
        return bool(model.predict(sensor_df.values.reshape(1, -1))[0] == -1)
    from app.ml.stub import detect_anomaly as _stub
    return _stub(sensor_df)
