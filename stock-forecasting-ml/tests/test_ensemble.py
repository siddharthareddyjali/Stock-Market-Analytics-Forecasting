from app.ml.evaluation import calculate_ensemble_weights, ensemble_fallback
from app.services.ensemble_service import combine_forecasts, compute_ensemble_weights


def test_ensemble_weight_calculation():
    metrics = {
        'ARIMA': {'mae': 2.0, 'rmse': 4.0, 'mape': 10.0},
        'Random Forest': {'mae': 3.0, 'rmse': 5.0, 'mape': 12.0},
        'LSTM': {'mae': 1.0, 'rmse': 2.5, 'mape': 8.0},
    }
    weights = calculate_ensemble_weights(metrics)
    assert set(weights) == {'ARIMA', 'Random Forest', 'LSTM'}
    assert sum(weights.values()) == 1.0


def test_ensemble_fallback():
    prediction_values = {'ARIMA': 100.0, 'Random Forest': 102.0, 'LSTM': 101.5}
    output = ensemble_fallback(prediction_values)
    assert abs(output - 101.1666666667) < 1e-6


def test_combine_forecasts():
    weights = {'ARIMA': 0.5, 'Random Forest': 0.3, 'LSTM': 0.2}
    predictions = {'ARIMA': 100.0, 'Random Forest': 101.0, 'LSTM': 99.0}
    combined = combine_forecasts(predictions, weights)
    assert abs(combined - 100.1) < 1e-6
