from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get('/health')
    assert response.status_code in (200, 503)
    payload = response.json()
    assert 'status' in payload


def test_ticker_validation():
    response = client.get('/api/forecast', params={'ticker': 'INVALID TICKER', 'forecast_days': 30})
    assert response.status_code == 400


def test_forecast_period_validation():
    response = client.get('/api/forecast', params={'ticker': 'AAPL', 'forecast_days': 12})
    assert response.status_code == 400


def test_api_schemas():
    from app.schemas.forecast import ForecastRequest
    request = ForecastRequest(ticker='aapl', forecast_days=30)
    assert request.ticker == 'AAPL'
    assert request.forecast_days == 30
