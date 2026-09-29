const API_BASE = window.location.origin;

async function fetchForecast(ticker, forecastDays) {
  const url = new URL('/api/forecast', API_BASE);
  url.searchParams.set('ticker', ticker);
  url.searchParams.set('forecast_days', String(forecastDays));

  const response = await fetch(url, { method: 'GET' });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.detail || 'Unable to generate forecast.');
  }
  return payload;
}

async function fetchRecentForecasts() {
  const response = await fetch('/api/forecast-history');
  if (!response.ok) {
    throw new Error('Unable to load recent forecasts.');
  }
  return response.json();
}
