const tickerInput = document.getElementById('tickerInput');
const forecastDaysSelect = document.getElementById('forecastDays');
const forecastSelect = document.getElementById('forecastSelect');
const generateBtn = document.getElementById('generateBtn');
const statusBanner = document.getElementById('statusBanner');

const currentPriceEl = document.getElementById('currentPrice');
const forecastPriceEl = document.getElementById('forecastPrice');
const projectedChangeEl = document.getElementById('projectedChange');
const forecastHorizonEl = document.getElementById('forecastHorizon');
const modelMetricsTable = document.getElementById('modelMetricsTable');
const modelWeights = document.getElementById('modelWeights');
const forecastTableBody = document.getElementById('forecastTableBody');
const recentForecastsBody = document.getElementById('recentForecastsBody');
let latestHistoryData = [];

const selectTrigger = forecastSelect.querySelector('.select-trigger');
const selectMenu = forecastSelect.querySelector('.select-menu');
const selectLabel = selectTrigger.querySelector('span');

selectTrigger.addEventListener('click', () => {
  const isOpen = forecastSelect.classList.toggle('open');
  selectTrigger.setAttribute('aria-expanded', String(isOpen));
});

selectMenu.querySelectorAll('button').forEach((option) => {
  option.addEventListener('click', () => {
    forecastDaysSelect.value = option.dataset.value;
    selectLabel.textContent = option.textContent;
    selectMenu.querySelectorAll('button').forEach((item) => item.setAttribute('aria-selected', 'false'));
    option.setAttribute('aria-selected', 'true');
    forecastSelect.classList.remove('open');
    selectTrigger.setAttribute('aria-expanded', 'false');
  });
});

document.addEventListener('click', (event) => {
  if (!forecastSelect.contains(event.target)) {
    forecastSelect.classList.remove('open');
    selectTrigger.setAttribute('aria-expanded', 'false');
  }
});

function showStatus(message, type = 'info') {
  statusBanner.textContent = message;
  statusBanner.classList.remove('hidden', 'show-error', 'show-success');
  if (type === 'error') {
    statusBanner.classList.add('show-error');
  } else if (type === 'success') {
    statusBanner.classList.add('show-success');
  }
}

function setLoading(isLoading) {
  generateBtn.disabled = isLoading;
  generateBtn.textContent = isLoading ? 'Generating forecast...' : 'Generate Forecast';
  const steps = [
    'Preparing historical data...',
    'Training forecasting models...',
    'Evaluating models...',
    'Generating forecast...',
    'Preparing dashboard...'
  ];
  if (isLoading) {
    let stepIndex = 0;
    showStatus(steps[0], 'info');
    window.__forecastLoadingTimer = setInterval(() => {
      stepIndex = (stepIndex + 1) % steps.length;
      showStatus(steps[stepIndex], 'info');
    }, 1800);
  } else {
    clearInterval(window.__forecastLoadingTimer);
  }
}

function renderMetrics(metrics = []) {
  modelMetricsTable.innerHTML = '';
  metrics.forEach((metric) => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${metric.model_name}</td>
      <td>${Number(metric.mae ?? 0).toFixed(4)}</td>
      <td>${Number(metric.rmse ?? 0).toFixed(4)}</td>
      <td>${Number(metric.mape ?? 0).toFixed(2)}%</td>
    `;
    modelMetricsTable.appendChild(row);
  });
}

function renderWeights(weights = []) {
  modelWeights.innerHTML = '';
  weights.forEach((entry) => {
    const row = document.createElement('div');
    row.className = 'weight-row';
    row.innerHTML = `
      <span class="weight-name">${entry.model_name}</span>
      <span class="weight-value">${(Number(entry.weight) * 100).toFixed(1)}%</span>
    `;
    modelWeights.appendChild(row);
  });
}

function renderForecastTable(rows = []) {
  forecastTableBody.innerHTML = '';
  rows.forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.date}</td>
      <td>${formatCurrency(row.ensemble_prediction)}</td>
      <td>${formatCurrency(row.arima_prediction)}</td>
      <td>${formatCurrency(row.random_forest_prediction)}</td>
      <td>${formatCurrency(row.lstm_prediction)}</td>
    `;
    forecastTableBody.appendChild(tr);
  });
}

function renderRecentForecasts(rows = []) {
  recentForecastsBody.innerHTML = '';
  rows.forEach((row) => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.ticker}</td>
      <td>${row.forecast_days || '--'} days</td>
      <td>${formatCurrency(row.predicted_price)}</td>
      <td>${row.created_at || '--'}</td>
    `;
    recentForecastsBody.appendChild(tr);
  });
}

function updateSummary(data) {
  currentPriceEl.textContent = formatCurrency(data.current_price);
  forecastPriceEl.textContent = formatCurrency(data.predicted_price);
  projectedChangeEl.textContent = `${data.predicted_change >= 0 ? '+' : ''}${formatCurrency(data.predicted_change)}`;
  forecastHorizonEl.textContent = `${data.forecast_days} Days`;
}

function renderDashboard(payload) {
  const historyData = payload.histories || [];
  const forecastRows = payload.forecast_points || [];
  latestHistoryData = historyData;

  updateSummary(payload);
  renderMetrics(payload.model_metrics || []);
  renderWeights(payload.model_weights || []);
  renderForecastTable(forecastRows);

  const historicalChart = buildHistoricalChart(historyData, '5');
  const forecastChart = buildForecastChart(historyData, forecastRows);

  Plotly.newPlot('historicalChart', historicalChart.data, historicalChart.layout, historicalChart.config);
  Plotly.newPlot('forecastChart', forecastChart.data, forecastChart.layout, forecastChart.config);
  window.addEventListener('resize', () => {
    Plotly.Plots.resize('historicalChart');
    Plotly.Plots.resize('forecastChart');
  });
}

function updateHistoricalRange(range, button) {
  document.querySelectorAll('.range-btn').forEach((item) => item.classList.remove('active'));
  button.classList.add('active');
  if (!latestHistoryData.length) return;
  const chart = buildHistoricalChart(latestHistoryData, range);
  Plotly.react('historicalChart', chart.data, chart.layout, chart.config);
}

async function handleGenerateForecast() {
  const ticker = tickerInput.value.trim().toUpperCase();
  const forecastDays = Number(forecastDaysSelect.value);
  if (!ticker) {
    showStatus('Please enter a valid stock ticker.', 'error');
    return;
  }
  setLoading(true);
  try {
    const data = await fetchForecast(ticker, forecastDays);
    renderDashboard(data);
    showStatus(`Forecast generated for ${ticker}.`, 'success');
  } catch (error) {
    showStatus(error.message || 'Forecast request failed.', 'error');
  } finally {
    setLoading(false);
  }
}

generateBtn.addEventListener('click', handleGenerateForecast);

document.querySelectorAll('.range-btn').forEach((button) => {
  button.addEventListener('click', () => updateHistoricalRange(button.dataset.months, button));
});

tickerInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    handleGenerateForecast();
  }
});

window.addEventListener('DOMContentLoaded', async () => {
  try {
    const recentData = await fetchRecentForecasts();
    renderRecentForecasts(recentData);
  } catch (error) {
    renderRecentForecasts([]);
  }
  handleGenerateForecast();
});
