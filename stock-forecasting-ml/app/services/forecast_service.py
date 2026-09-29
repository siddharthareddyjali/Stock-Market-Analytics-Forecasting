from __future__ import annotations

import logging
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

from app.ml.arima_model import ARIMAModel
from app.ml.evaluation import calculate_ensemble_weights, calculate_metrics
from app.ml.feature_engineering import build_feature_matrix
from app.ml.lstm_model import LSTMModel
from app.ml.random_forest_model import RandomForestModel
from app.services.ensemble_service import combine_forecasts, compute_ensemble_weights

logger = logging.getLogger(__name__)


class ForecastService:
    def __init__(self, forecast_days: int):
        self.forecast_days = forecast_days

    def prepare_time_series(self, history: pd.DataFrame):
        if history is None or history.empty:
            raise ValueError("Historical price dataset is empty.")
        series = history["Close"].copy().astype(float)
        series = series.sort_index()
        series = series[~series.index.duplicated(keep="last")]
        return series

    def split_validation(self, series: pd.Series, validation_days: int | None = None):
        validation_days = validation_days or self.forecast_days
        validation_days = max(7, min(validation_days, 90))
        if len(series) < validation_days + 30:
            raise ValueError("Insufficient data for chronological validation.")
        train_end = len(series) - validation_days
        train = series.iloc[:train_end]
        validation = series.iloc[train_end:]
        return train, validation

    def build_modelling_frame(self, series: pd.Series, target: str = "price"):
        frame = pd.DataFrame({"Close": series})
        frame = frame.sort_index()
        feature_frame = build_feature_matrix(frame)
        if target == "return":
            feature_frame["target"] = feature_frame["Close"].pct_change().shift(-1)
        else:
            feature_frame["target"] = feature_frame["Close"].shift(-1)
        feature_frame = feature_frame.dropna(subset=["target"])
        X = feature_frame.drop(columns=["target", "Close"])
        y = feature_frame["target"]
        return X, y

    def _recursive_return_forecast(self, model, series: pd.Series, steps: int) -> np.ndarray:
        working = series.copy()
        prices = []
        for _ in range(steps):
            features, _ = self.build_modelling_frame(working, target="return")
            raw_return = float(model.predict(features.tail(1))[0])
            recent_returns = working.pct_change().dropna()
            recent_volatility = float(recent_returns.rolling(20).std().iloc[-1])
            if not np.isfinite(recent_volatility) or recent_volatility <= 0:
                recent_volatility = float(recent_returns.std())
            return_limit = max(0.03, min(0.12, 3.0 * recent_volatility))
            next_return = float(np.clip(raw_return * 0.65, -return_limit, return_limit))
            next_price = float(working.iloc[-1]) * (1.0 + next_return)
            prices.append(next_price)
            next_index = working.index[-1] + pd.offsets.BDay(1)
            working.loc[next_index] = next_price
        return np.asarray(prices, dtype=float)

    @staticmethod
    def _returns_to_prices(returns: np.ndarray, starting_price: float) -> np.ndarray:
        return starting_price * np.cumprod(1.0 + np.asarray(returns, dtype=float))

    def train_models(self, series: pd.Series):
        train, validation = self.split_validation(series)
        X_all, y_all = self.build_modelling_frame(series, target="return")
        validation_start = validation.index[0]
        validation_feature_start = series.index[series.index.get_loc(validation_start) - 1]
        train_mask = X_all.index < validation_feature_start
        validation_mask = X_all.index >= validation_feature_start
        X_train, y_train = X_all.loc[train_mask], y_all.loc[train_mask]
        X_val, y_val = X_all.loc[validation_mask], y_all.loc[validation_mask]
        if X_train.empty or X_val.empty:
            raise ValueError("Insufficient data to create chronological model validation features.")

        arima = ARIMAModel(order=(1, 1, 1))
        arima_fit = arima.fit(train)
        arima_val = arima.predict(len(validation))

        rf = RandomForestModel(n_estimators=500, random_state=42, max_depth=12, min_samples_leaf=8, max_features=0.7)
        rf.fit(X_train, y_train)
        rf_val = self._recursive_return_forecast(rf, train, len(validation))

        train_returns = train.pct_change().dropna()
        lstm_model = LSTMModel(lookback=30, units=32, epochs=12, batch_size=32)
        lstm_model.fit(train_returns)
        lstm_returns = lstm_model.predict(len(validation), np.asarray(train_returns.iloc[-30:], dtype=float))
        lstm_val = self._returns_to_prices(lstm_returns, float(train.iloc[-1]))

        model_metrics = {
            "ARIMA": calculate_metrics(np.asarray(validation.values, dtype=float), np.asarray(arima_val, dtype=float)),
            "Random Forest": calculate_metrics(np.asarray(validation.values, dtype=float), np.asarray(rf_val, dtype=float)),
            "LSTM": calculate_metrics(np.asarray(validation.values, dtype=float), np.asarray(lstm_val, dtype=float)),
        }
        weights = compute_ensemble_weights(model_metrics)
        return {"train": train, "validation": validation, "metrics": model_metrics, "weights": weights, "arima": arima, "rf": rf, "lstm": lstm_model}

    def generate_forecast(self, history: pd.DataFrame):
        series = self.prepare_time_series(history)
        trained = self.train_models(series)
        arima_forecast = trained["arima"].predict(self.forecast_days)
        rf_forecast = self._recursive_return_forecast(trained["rf"], series, self.forecast_days)
        latest_returns = np.asarray(series.pct_change().dropna().iloc[-30:], dtype=float)
        lstm_returns = trained["lstm"].predict(self.forecast_days, latest_returns)
        lstm_forecast = self._returns_to_prices(lstm_returns, float(series.iloc[-1]))

        predictions = {
            "ARIMA": float(np.asarray(arima_forecast)[-1]),
            "Random Forest": float(np.asarray(rf_forecast)[-1]),
            "LSTM": float(np.asarray(lstm_forecast)[-1]),
        }
        ensemble_value = combine_forecasts(predictions, trained["weights"])
        current_price = float(series.iloc[-1])
        projected_change = ensemble_value - current_price
        projected_change_percent = (projected_change / current_price) * 100 if current_price else 0.0

        future_dates = pd.date_range(start=pd.Timestamp(datetime.utcnow().date()) + timedelta(days=1), periods=self.forecast_days, freq="B")
        forecast_rows = []
        for idx, future_date in enumerate(future_dates):
            date_value = future_date.date().isoformat()
            model_values = {
                "ARIMA": float(np.asarray(arima_forecast)[idx]),
                "Random Forest": float(np.asarray(rf_forecast)[idx]),
                "LSTM": float(np.asarray(lstm_forecast)[idx]),
            }
            forecast_rows.append({
                "date": date_value,
                "arima_prediction": model_values["ARIMA"],
                "random_forest_prediction": model_values["Random Forest"],
                "lstm_prediction": model_values["LSTM"],
                "ensemble_prediction": combine_forecasts(model_values, trained["weights"]),
            })

        return {
            "series": series,
            "metrics": trained["metrics"],
            "weights": trained["weights"],
            "predictions": predictions,
            "forecast_rows": forecast_rows,
            "current_price": current_price,
            "predicted_price": ensemble_value,
            "predicted_change": projected_change,
            "predicted_change_percent": projected_change_percent,
        }
