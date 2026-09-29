# Stock Market Analytics & Forecasting

A full-stack stock forecasting application that downloads roughly 10 years of daily market data, stores it in MySQL, trains multiple time-series models, evaluates them, computes ensemble weights, and serves an interactive dashboard with historical and forecast visuals.

## Overview

The app is designed for a student portfolio or interview project. The user only enters a stock ticker and a forecasting horizon. The backend handles:

- data retrieval from Yahoo Finance
- MySQL caching and upserts
- preprocessing and feature engineering
- chronological validation
- ARIMA, Random Forest, and LSTM training
- model evaluation
- validation-based ensemble weighting
- final forecast generation and dashboard display

## Features

- FastAPI backend with Python
- MySQL persistence through SQLAlchemy
- yfinance data download and caching
- feature engineering with lags and technical indicators
- ARIMA, Random Forest, and lightweight LSTM models
- ensemble forecasting based on validation metrics
- interactive Plotly dashboard
- testing with pytest

## Architecture

```text
frontend/          # HTML, CSS, JavaScript, Plotly charts
app/               # FastAPI app, models, services, ML logic
sql/               # MySQL DDL schema
artifacts/         # optional model artifacts and scalers
tests/             # pytest cases
```

## Tech Stack

- Python
- FastAPI
- SQLAlchemy 2.x
- PyMySQL
- MySQL
- yfinance
- pandas
- numpy
- statsmodels
- scikit-learn
- TensorFlow/Keras
- Plotly
- pytest

## Project Structure

```text
stock-forecasting-ml/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   └── database.py
│   ├── models/
│   │   ├── stock.py
│   │   ├── stock_price.py
│   │   ├── forecast_run.py
│   │   ├── forecast_prediction.py
│   │   ├── model_metric.py
│   │   └── model_weight.py
│   ├── schemas/
│   │   ├── stock.py
│   │   ├── forecast.py
│   │   └── response.py
│   ├── api/
│   ├── services/
│   ├── ml/
│   └── utils/
├── frontend/
│   ├── index.html
│   ├── css/
│   └── js/
├── artifacts/
├── tests/
├── sql/
├── .env.example
├── .gitignore
├── requirements.txt
├── README.md
├── run.py
└── stock-forecasting-ml.zip
```

## Database Setup

1. Install MySQL.
2. Create a database named `stock_forecasting`.
3. Configure `DATABASE_URL` in `.env` based on `.env.example`.

Example:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/stock_forecasting
DEBUG=false
LOG_LEVEL=INFO
```

The application initializes tables on startup if they do not exist.

## Environment Variables

Create a `.env` file in the project root. Use placeholders only:

```env
DATABASE_URL=mysql+pymysql://root:password@localhost:3306/stock_forecasting
DEBUG=false
LOG_LEVEL=INFO
```

Never commit real credentials.

## Installation

From the project root:

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Running MySQL

Start MySQL locally. A common setup is:

```bash
mysql -u root -p
CREATE DATABASE IF NOT EXISTS stock_forecasting;
```

If you use a service like XAMPP or MySQL Workbench, ensure the database is active and the connection URL matches your configuration.

## Running Backend

Start the FastAPI app:

```bash
python run.py
```

Then open:

```text
http://localhost:8000
```

## Opening Frontend

The frontend is served by the FastAPI app directly. Open the root URL above. The dashboard loads from the static files in `frontend/`.

## API Endpoints

```text
GET /health
GET /api/stocks
GET /api/forecast?ticker=AAPL&forecast_days=30
GET /api/forecast-history
```

## ML Pipeline

The application automatically retrieves data, cleans it, creates lag and technical features, trains forecasting models, validates them chronologically, and builds an ensemble forecast.

### ARIMA

ARIMA is used for linear time-series modeling. It is trained on recent historical close prices and used to forecast the next horizon based on the model fit.

### Random Forest

Random Forest builds a non-linear regression model from lagged and technical features. It is trained on feature-engineered historical data and used to predict future prices.

### LSTM

The LSTM model learns short and medium-term patterns from the last sequence of close prices. It is a lightweight Keras model designed to run on a regular laptop.

### Ensemble

The ensemble combines individual model outputs using validation-based weights. Lower-error models receive larger weights, and the final forecast is a weighted blend of ARIMA, Random Forest, and LSTM predictions.

### Multi-step forecasting notes

The Random Forest and LSTM models predict next-session returns and recursively convert those returns into prices. This avoids reusing one single next-price prediction for every forecast date. The LSTM is standardized using training data only and inverse-transformed before metrics are calculated. Random Forest uses lagged prices, moving averages, EMA, returns, and rolling volatility without future leakage. Validation is chronological and uses the same recursive strategy as production forecasting.

ARIMA is fitted to log prices with first differencing, a small AIC-selected order search, and a linear drift term. This keeps the model appropriate for non-stationary price levels while allowing a validated drift instead of forcing every future value to equal the last price. ARIMA forecasts can still become nearly flat at longer horizons when the fitted series has little persistent signal; that remains a mathematically valid result rather than an artificial trend. Ensemble weights are based on validation error with a small equal-weight shrinkage so one model cannot completely eliminate the other independently evaluated forecasts.

Further reading:

- [Forecasting: Principles and Practice](https://otexts.com/fpp3/)
- [Why do my forecasts look flat?](https://robjhyndman.com/hyndsight/flat-forecasts/)
- [scikit-learn TimeSeriesSplit](https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.TimeSeriesSplit.html)
- [TensorFlow time-series forecasting](https://www.tensorflow.org/tutorials/structured_data/time_series)

## Testing

Run:

```bash
pytest -q
```

The tests check health, validation, lag generation, technical features, metrics, ensemble calculations, and basic API behavior without contacting live Yahoo Finance.

## Troubleshooting

- If MySQL is unavailable: ensure the database is started and the `DATABASE_URL` is correct.
- If Yahoo Finance fails: check your internet connection and Yahoo Finance service status.
- If TensorFlow fails to initialize: verify the environment supports the installed package.
- If the dashboard does not render: ensure the backend is running on port 8000 and the static frontend assets are present.

## Limitations

- Forecasts are statistical and educational in nature.
- Real market behavior can differ significantly from model predictions.
- This project is designed for a portfolio or coursework application and is intentionally lightweight.

## Disclaimer

This application provides statistical/model-based forecasts for educational and analytical purposes. Forecasts are uncertain and should not be treated as guaranteed future prices or financial advice.
