from __future__ import annotations

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error


def calculate_metrics(actual: np.ndarray, predicted: np.ndarray) -> dict[str, float]:
    actual = np.asarray(actual, dtype=float)
    predicted = np.asarray(predicted, dtype=float)
    if actual.shape[0] == 0:
        raise ValueError("Actual values must not be empty.")
    if actual.shape != predicted.shape:
        raise ValueError("Actual and predicted arrays must have the same shape.")
    mae = float(mean_absolute_error(actual, predicted))
    rmse = float(np.sqrt(mean_squared_error(actual, predicted)))
    mape = float(np.mean(np.abs((actual - predicted) / np.maximum(np.abs(actual), 1e-8))) * 100)
    return {"mae": mae, "rmse": rmse, "mape": mape}


def normalize_inverse_weights(metric_map: dict[str, float]) -> dict[str, float]:
    total = sum(metric_map.values())
    if total <= 0:
        return {name: 0.0 for name in metric_map}
    return {name: value / total for name, value in metric_map.items()}


def calculate_ensemble_weights(model_metrics: dict[str, dict[str, float]]) -> dict[str, float]:
    weights = {}
    for model_name, metrics in model_metrics.items():
        rmse = float(metrics.get("rmse", 0.0))
        mae = float(metrics.get("mae", 0.0))
        mape = float(metrics.get("mape", 0.0))
        composite = rmse + mae + (mape / 100.0)
        weights[model_name] = 1.0 / max(composite, 1e-8)
    total = sum(weights.values())
    if total <= 0:
        return {k: 1.0 / len(weights) for k in weights}
    raw_weights = {k: v / total for k, v in weights.items()}
    equal_weight = 1.0 / len(raw_weights)
    return {k: (0.8 * value) + (0.2 * equal_weight) for k, value in raw_weights.items()}


def ensemble_fallback(prediction_values: dict[str, float]) -> float:
    if not prediction_values:
        raise ValueError("No model predictions provided for ensemble fallback.")
    values = list(prediction_values.values())
    return float(sum(values) / len(values))
