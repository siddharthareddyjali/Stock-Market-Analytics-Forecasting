from __future__ import annotations

import numpy as np
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA


class ARIMAModel:
    def __init__(self, order=None, seasonal_order=(0, 0, 0, 0)):
        self.order = order
        self.seasonal_order = seasonal_order
        self.model = None
        self.selected_order = None

    def fit(self, series: pd.Series):
        train = series.astype(float).dropna()
        if len(train) < 40 or (train <= 0).any():
            raise ValueError("ARIMA requires at least 10 observations.")
        log_train = np.log(train)
        candidate_orders = [self.order] if self.order else [(1, 1, 1), (2, 1, 1), (1, 1, 2), (2, 1, 2)]
        fitted = []
        for order in candidate_orders:
            try:
                model = ARIMA(
                    log_train,
                    order=order,
                    seasonal_order=self.seasonal_order,
                    trend="t" if order[1] else "c",
                    enforce_stationarity=True,
                    enforce_invertibility=True,
                )
                fitted.append(model.fit())
            except (ValueError, np.linalg.LinAlgError):
                continue
        if not fitted:
            raise ValueError("Unable to fit a valid ARIMA model.")
        self.model_fit = min(fitted, key=lambda result: result.aic)
        self.selected_order = self.model_fit.model.order
        return self.model_fit

    def predict(self, steps: int) -> np.ndarray:
        if self.model_fit is None:
            raise ValueError("ARIMA model has not been fitted.")
        preds = self.model_fit.forecast(steps=steps)
        return np.exp(np.asarray(preds, dtype=float))

    def forecast_from_validation(self, series: pd.Series, validation_days: int):
        self.fit(series)
        return self.predict(validation_days)
