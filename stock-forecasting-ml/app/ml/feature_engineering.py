from __future__ import annotations

import pandas as pd


def lag_features(series: pd.Series, lags: list[int] | None = None) -> pd.DataFrame:
    if lags is None:
        lags = [1, 2, 3, 5, 7, 14, 30]
    result = pd.DataFrame(index=series.index)
    for lag in lags:
        result[f"lag_{lag}"] = series.shift(lag)
    return result


def add_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    frame = df.copy()
    frame["SMA_20"] = frame["Close"].rolling(window=20, min_periods=1).mean()
    frame["SMA_50"] = frame["Close"].rolling(window=50, min_periods=1).mean()
    frame["SMA_200"] = frame["Close"].rolling(window=200, min_periods=1).mean()
    frame["EMA_20"] = frame["Close"].ewm(span=20, adjust=False).mean()
    frame["daily_return"] = frame["Close"].pct_change().fillna(0)
    frame["rolling_volatility"] = frame["Close"].pct_change().rolling(window=20, min_periods=1).std().fillna(0)
    return frame


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    feature_df = df.copy()
    if "Close" not in feature_df.columns:
        raise ValueError("Input dataframe must include a Close column.")
    feature_df = feature_df.sort_index()
    for lag in [1, 2, 3, 5, 7, 14, 30]:
        feature_df[f"lag_{lag}"] = feature_df["Close"].shift(lag)
    feature_df["SMA_20"] = feature_df["Close"].rolling(window=20, min_periods=1).mean()
    feature_df["SMA_50"] = feature_df["Close"].rolling(window=50, min_periods=1).mean()
    feature_df["SMA_200"] = feature_df["Close"].rolling(window=200, min_periods=1).mean()
    feature_df["EMA_20"] = feature_df["Close"].ewm(span=20, adjust=False).mean()
    feature_df["daily_return"] = feature_df["Close"].pct_change().fillna(0)
    feature_df["rolling_volatility"] = feature_df["Close"].pct_change().rolling(window=20, min_periods=1).std().fillna(0)
    returns = feature_df["Close"].pct_change()
    feature_df["return_lag_1"] = returns.shift(1)
    feature_df["return_lag_5"] = returns.shift(5)
    feature_df["return_lag_10"] = returns.shift(10)
    feature_df["return_lag_20"] = returns.shift(20)
    feature_df["momentum_20"] = feature_df["Close"].pct_change(20)
    feature_df["volatility_60"] = returns.rolling(window=60, min_periods=20).std()
    feature_df["price_to_sma_20"] = feature_df["Close"] / feature_df["SMA_20"] - 1.0
    feature_df["price_to_sma_50"] = feature_df["Close"] / feature_df["SMA_50"] - 1.0
    feature_df["price_to_sma_200"] = feature_df["Close"] / feature_df["SMA_200"] - 1.0
    feature_df = feature_df.replace([float("inf"), -float("inf")], float("nan")).dropna()
    return feature_df
