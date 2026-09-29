CREATE TABLE IF NOT EXISTS stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL UNIQUE,
    company_name VARCHAR(255),
    exchange VARCHAR(80),
    currency VARCHAR(20),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_stocks_ticker (ticker)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS stock_prices (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    trade_date DATE NOT NULL,
    open_price DOUBLE,
    high_price DOUBLE,
    low_price DOUBLE,
    close_price DOUBLE,
    adjusted_close DOUBLE,
    volume BIGINT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_stock_price_date (stock_id, trade_date),
    INDEX idx_stock_price_stock_id (stock_id),
    INDEX idx_stock_price_trade_date (trade_date),
    CONSTRAINT fk_stock_prices_stock FOREIGN KEY (stock_id) REFERENCES stocks(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS forecast_runs (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    stock_id INT NOT NULL,
    forecast_days INT NOT NULL,
    current_price DOUBLE NOT NULL,
    predicted_price DOUBLE NOT NULL,
    predicted_change DOUBLE NOT NULL,
    predicted_change_percent DOUBLE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_forecast_runs_stock_id (stock_id),
    CONSTRAINT fk_forecast_runs_stock FOREIGN KEY (stock_id) REFERENCES stocks(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS forecast_predictions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    forecast_run_id BIGINT NOT NULL,
    forecast_date DATE NOT NULL,
    arima_prediction DOUBLE,
    random_forest_prediction DOUBLE,
    lstm_prediction DOUBLE,
    ensemble_prediction DOUBLE,
    INDEX idx_forecast_predictions_run_id (forecast_run_id),
    INDEX idx_forecast_predictions_date (forecast_date),
    CONSTRAINT fk_forecast_predictions_run FOREIGN KEY (forecast_run_id) REFERENCES forecast_runs(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS model_metrics (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    forecast_run_id BIGINT NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    mae DOUBLE,
    rmse DOUBLE,
    mape DOUBLE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_metrics_run_id (forecast_run_id),
    CONSTRAINT fk_model_metrics_run FOREIGN KEY (forecast_run_id) REFERENCES forecast_runs(id)
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS model_weights (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    forecast_run_id BIGINT NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    weight DOUBLE NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_model_weights_run_id (forecast_run_id),
    CONSTRAINT fk_model_weights_run FOREIGN KEY (forecast_run_id) REFERENCES forecast_runs(id)
) ENGINE=InnoDB;
