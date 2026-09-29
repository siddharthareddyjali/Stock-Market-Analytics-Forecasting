from __future__ import annotations

from typing import Any


def compute_ensemble_weights(model_metrics: dict[str, dict[str, float]]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for model_name, metrics in model_metrics.items():
        rmse = float(metrics.get("rmse", 0.0))
        mae = float(metrics.get("mae", 0.0))
        mape = float(metrics.get("mape", 0.0))
        composite = rmse + mae + (mape / 100.0)
        weights[model_name] = 1.0 / max(composite, 1e-8)
    total = sum(weights.values())
    if total <= 0:
        return {name: 1.0 / len(weights) for name in model_metrics}
    raw_weights = {name: value / total for name, value in weights.items()}
    equal_weight = 1.0 / len(raw_weights)
    return {name: (0.8 * value) + (0.2 * equal_weight) for name, value in raw_weights.items()}


def combine_forecasts(model_predictions: dict[str, float], weights: dict[str, float]) -> float:
    if not model_predictions:
        raise ValueError("No model predictions provided.")
    if not weights:
        raise ValueError("No model weights provided.")
    combined = 0.0
    total_weight = 0.0
    for key in model_predictions:
        if key in weights:
            combined += float(model_predictions[key]) * float(weights[key])
            total_weight += float(weights[key])
    if total_weight <= 0:
        raise ValueError("Sum of ensemble weights must be positive.")
    return combined / total_weight
