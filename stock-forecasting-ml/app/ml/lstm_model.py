from __future__ import annotations

import numpy as np
import pandas as pd
from tensorflow.keras import Sequential
from tensorflow.keras.layers import Input, LSTM, Dense
from tensorflow.keras.optimizers import Adam
from sklearn.preprocessing import StandardScaler


class LSTMModel:
    def __init__(self, lookback=30, units=32, epochs=8, batch_size=16):
        self.lookback = lookback
        self.units = units
        self.epochs = epochs
        self.batch_size = batch_size
        self.model = None
        self.scaler = StandardScaler()

    def _prepare_sequences(self, values: np.ndarray):
        if len(values) <= self.lookback:
            raise ValueError("Not enough data to create LSTM sequences.")
        X, y = [], []
        for i in range(self.lookback, len(values)):
            X.append(values[i - self.lookback : i])
            y.append(values[i])
        return np.asarray(X, dtype=float), np.asarray(y, dtype=float)

    def fit(self, series: pd.Series):
        values = np.asarray(series.astype(float).dropna(), dtype=float)
        if len(values) <= self.lookback:
            raise ValueError("LSTM requires more observations than the lookback window.")
        scaled_values = self.scaler.fit_transform(values.reshape(-1, 1)).reshape(-1)
        X, y = self._prepare_sequences(scaled_values)
        X = X.reshape(len(X), self.lookback, 1)
        self.model = Sequential([
            Input(shape=(self.lookback, 1)),
            LSTM(self.units),
            Dense(1),
        ])
        self.model.compile(optimizer=Adam(learning_rate=0.001), loss="mse")
        self.model.fit(X, y, epochs=self.epochs, batch_size=self.batch_size, verbose=0)
        return self.model

    def predict(self, steps: int, last_values: np.ndarray) -> np.ndarray:
        if self.model is None:
            raise ValueError("LSTM model has not been trained.")
        seq = np.asarray(last_values, dtype=float).reshape(-1)
        scaled_seq = self.scaler.transform(seq.reshape(-1, 1)).reshape(-1)
        result = []
        for _ in range(steps):
            x = scaled_seq[-self.lookback:]
            x = x.reshape(1, self.lookback, 1)
            scaled_prediction = float(self.model.predict(x, verbose=0)[0, 0])
            prediction = float(self.scaler.inverse_transform([[scaled_prediction]])[0, 0])
            result.append(prediction)
            scaled_seq = np.append(scaled_seq, scaled_prediction)
        return np.asarray(result, dtype=float)
