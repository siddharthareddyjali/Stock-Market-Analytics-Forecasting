function formatCurrency(value) {
  if (value === null || value === undefined || Number.isNaN(Number(value))) return '--';
  return `$${Number(value).toFixed(2)}`;
}

function subtractMonths(dateValue, months) {
  const date = new Date(dateValue);
  date.setMonth(date.getMonth() - months);
  return date.toISOString().slice(0, 10);
}

function buildHistoricalChart(historyData, range = '5') {
  const latestDate = historyData[historyData.length - 1]?.date;
  const closeTrace = {
    x: historyData.map((point) => point.date),
    y: historyData.map((point) => point.close),
    type: 'scatter',
    mode: 'lines',
    name: 'Historical Close Price',
    line: { color: '#1f5a94', width: 2.5 },
  };

  return {
    data: [closeTrace],
    layout: {
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff',
      margin: { l: 50, r: 18, t: 18, b: 40 },
      font: { color: '#172b4d', family: 'Inter, sans-serif' },
      xaxis: {
        rangeslider: { visible: true, thickness: 0.08 },
        rangeselector: {
          active: 1,
          bgcolor: '#eef4fb',
          activecolor: '#1f5a94',
          bordercolor: '#c6d7e8',
          font: { color: '#172b4d' },
          buttons: [
            { count: 3, label: '3M', step: 'month', stepmode: 'backward' },
            { count: 5, label: '5M', step: 'month', stepmode: 'backward' },
            { count: 1, label: '1Y', step: 'year', stepmode: 'backward' },
            { count: 2, label: '2Y', step: 'year', stepmode: 'backward' },
            { step: 'all', label: 'All' },
          ],
        },
        range: latestDate ? [subtractMonths(latestDate, range === 'all' ? 120 : Number(range)), latestDate] : undefined,
        showgrid: false,
        type: 'date',
      },
      yaxis: { showgrid: true, gridcolor: '#e7edf4', tickprefix: '$', fixedrange: false, zeroline: false },
      hovermode: 'x unified',
    },
    config: {
      responsive: true,
      displayModeBar: true,
      scrollZoom: true,
      dragmode: 'pan',
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
    },
  };
}

function buildForecastChart(historyData, forecastPoints) {
  const historicalX = historyData.map((point) => point.date);
  const historicalY = historyData.map((point) => point.close);
  const forecastX = [historicalX[historicalX.length - 1], ...forecastPoints.map((point) => point.date)];
  const ensembleY = [historicalY[historicalY.length - 1], ...forecastPoints.map((point) => point.ensemble_prediction)];
  const arimaY = [historicalY[historicalY.length - 1], ...forecastPoints.map((point) => point.arima_prediction)];
  const rfY = [historicalY[historicalY.length - 1], ...forecastPoints.map((point) => point.random_forest_prediction)];
  const lstmY = [historicalY[historicalY.length - 1], ...forecastPoints.map((point) => point.lstm_prediction)];

  const traces = [
    { x: historicalX, y: historicalY, type: 'scatter', mode: 'lines', name: 'Historical Price', line: { color: '#1f5a94', width: 2.5 }, hoverlabel: { bordercolor: '#1f5a94' } },
    { x: forecastX, y: ensembleY, type: 'scatter', mode: 'lines+markers', name: 'Ensemble Forecast', line: { color: '#16834b', width: 4 }, marker: { color: '#16834b', size: 5 }, hoverlabel: { bordercolor: '#16834b' } },
    { x: forecastX, y: arimaY, type: 'scatter', mode: 'lines', name: 'ARIMA', visible: 'legendonly', line: { color: '#c97900', width: 2, dash: 'dot' }, hoverlabel: { bordercolor: '#c97900' } },
    { x: forecastX, y: rfY, type: 'scatter', mode: 'lines', name: 'Random Forest', visible: 'legendonly', line: { color: '#d62f45', width: 2, dash: 'dash' }, hoverlabel: { bordercolor: '#d62f45' } },
    { x: forecastX, y: lstmY, type: 'scatter', mode: 'lines', name: 'LSTM', visible: 'legendonly', line: { color: '#6b4db3', width: 2, dash: 'longdash' }, hoverlabel: { bordercolor: '#6b4db3' } },
  ];

  return {
    data: traces,
    layout: {
      paper_bgcolor: '#ffffff',
      plot_bgcolor: '#ffffff',
      margin: { l: 50, r: 18, t: 18, b: 40 },
      font: { color: '#172b4d', family: 'Inter, sans-serif' },
      xaxis: {
        showgrid: false,
        type: 'date',
        rangeslider: { visible: true, thickness: 0.08 },
        rangeselector: {
          bgcolor: '#eef4fb',
          activecolor: '#1f5a94',
          bordercolor: '#c6d7e8',
          font: { color: '#172b4d' },
          buttons: [
            { count: 1, label: '1M', step: 'month', stepmode: 'backward' },
            { count: 3, label: '3M', step: 'month', stepmode: 'backward' },
            { step: 'all', label: 'All' },
          ],
        },
      },
      yaxis: { showgrid: true, gridcolor: '#e7edf4', tickprefix: '$', fixedrange: false, zeroline: false },
      hovermode: 'x unified',
      hoverlabel: {
        bgcolor: '#17243f',
        bordercolor: '#4ea1ff',
        font: { color: '#edf4ff', family: 'Inter, sans-serif', size: 13 },
        align: 'left',
      },
      legend: { orientation: 'h', yanchor: 'bottom', y: 1.18, xanchor: 'left', x: 0 },
      shapes: forecastX.length > 1 ? [{
        type: 'line',
        x0: forecastX[1],
        x1: forecastX[1],
        y0: 0,
        y1: 1,
        yref: 'paper',
        line: { color: '#16834b', width: 2, dash: 'dash' },
      }] : [],
      annotations: forecastX.length > 1 ? [{
        x: forecastX[1],
        y: 1,
        yref: 'paper',
        text: 'Forecast begins',
        showarrow: false,
        yshift: 12,
        font: { color: '#16834b', size: 11 },
      }] : [],
    },
    config: {
      responsive: true,
      displayModeBar: true,
      scrollZoom: true,
      dragmode: 'pan',
      displaylogo: false,
      modeBarButtonsToRemove: ['lasso2d', 'select2d', 'autoScale2d'],
    },
  };
}
