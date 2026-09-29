import pandas as pd

from app.ml.feature_engineering import add_technical_indicators, build_feature_matrix, lag_features


def test_lag_generation():
    series = pd.Series([10, 11, 12, 13, 14, 15], index=pd.date_range('2024-01-01', periods=6, freq='D'))
    lags = lag_features(series, [1, 2, 3])
    assert list(lags.columns) == ['lag_1', 'lag_2', 'lag_3']
    assert lags['lag_1'].iloc[1] == 10
    assert lags['lag_2'].iloc[2] == 10


def test_technical_features():
    df = pd.DataFrame({
        'Close': [100, 101, 102, 103, 104, 105]
    }, index=pd.date_range('2024-01-01', periods=6, freq='D'))
    result = add_technical_indicators(df)
    assert 'SMA_20' in result.columns
    assert 'EMA_20' in result.columns
    assert 'daily_return' in result.columns
    assert 'rolling_volatility' in result.columns


def test_build_feature_matrix():
    df = pd.DataFrame({
        'Close': [100, 101, 102, 103, 104, 105, 106, 107]
    }, index=pd.date_range('2024-01-01', periods=8, freq='D'))
    features = build_feature_matrix(df)
    assert {'lag_1', 'lag_2', 'lag_3', 'lag_5', 'lag_7', 'lag_14', 'lag_30', 'SMA_20', 'EMA_20', 'daily_return', 'rolling_volatility'}.issubset(features.columns)
