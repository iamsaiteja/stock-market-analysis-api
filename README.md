# Stock Market Analysis API

# 📈 Stock Market Analysis API

FastAPI-powered Stock Market Analysis API for NSE/BSE with provider market data, technical indicators, and rule-based indicator scores.

[![Live Demo](https://img.shields.io/badge/Live-Demo-brightgreen)](https://stock-market-frontend-nine.vercel.app/)
[![GitHub Repo](https://img.shields.io/badge/GitHub-Repository-black)](https://github.com/iamsaiteja/stock-market-api)

[![Python](https://img.shields.io/badge/Python-3.10+-blue)]()
[![FastAPI](https://img.shields.io/badge/FastAPI-Backend-009688)]()
[![yfinance](https://img.shields.io/badge/yfinance-Market_Data-blue)]()
[![Pandas](https://img.shields.io/badge/Pandas-Data_Analysis-purple)]()
[![NumPy](https://img.shields.io/badge/NumPy-Scientific_Computing-blue)]()
[![REST API](https://img.shields.io/badge/REST-API-red)]()

---

## 📸 Screenshots

### Dashboard

![Dashboard](stock.png)

FastAPI + yfinance build **NSE/BSE Stock Analysis API**.

##  Features
- Live stock prices (NSE & BSE)
- Rule-based Buy/Sell/Hold signals
- Technical indicators: RSI, MACD, Bollinger Bands, SMA
- Historical OHLCV data
- Bulk operations

## ⚡ Quick Start

```bash
# 1. Dependencies install 
pip install -r requirements.txt

# 2. Server start ం
uvicorn app.main:app --reload --port 8000

# 3. Docs open ం
# http://localhost:8000/docs
```

##  API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/stocks/{symbol}/price` | Live price |
| GET | `/api/v1/stocks/{symbol}/history` | Historical data |
| GET | `/api/v1/stocks/popular/nse` | Top 10 NSE stocks |
| POST | `/api/v1/stocks/bulk` | Multiple prices |
| GET | `/api/v1/predict/{symbol}` | rule-based signal |
| POST | `/api/v1/predict/bulk` | Bulk predictions |

##  Example Usage

```bash
# Reliance live price
curl http://localhost:8000/api/v1/stocks/RELIANCE/price

# TCS rule-based signal
curl http://localhost:8000/api/v1/predict/TCS

# Historical data (6 months)
curl http://localhost:8000/api/v1/stocks/INFY/history?period=6mo

# Bulk prices
curl -X POST http://localhost:8000/api/v1/stocks/bulk \
  -H "Content-Type: application/json" \
  -d '["RELIANCE", "TCS", "INFY"]'
```

## Rule-based signal Response Example

```json
{
  "symbol": "EXAMPLE.NS",
  "signal": "BUY",
  "signal_strength": 71.4,
  "indicator_condition": "NORMAL_RSI",
  "method": "rule_based_technical_indicators",
  "evaluated_accuracy": null
}
```
Illustrative response excerpt; not a measured trading result.




## What the signal means
This is a deterministic technical-indicator demonstration, not a trained AI prediction model. `signal_strength` is the absolute weighted indicator score divided by its maximum, expressed from 0 to 100. It is not a probability, confidence interval, measured accuracy or investment risk assessment. `evaluated_accuracy` is null because no out-of-sample evaluation has been performed. Comparing two moving averages on one date does not establish that a crossover occurred.

The previous `confidence`, `risk_level`, `target_price` and `stop_loss` response fields have been removed. Clients should use `signal_strength` and `indicator_condition`; fixed 3%/5% prices were not forecasts. At least 50 complete observations are required. Data comes from yfinance and may be delayed; the response timestamp records calculation time.

## Reproducible local setup (Python 3.12)
```sh
git clone https://github.com/iamsaiteja/stock-market-analysis-api.git
cd stock-market-analysis-api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```
Windows activation: `.venv\Scripts\activate`. Docs: http://127.0.0.1:8000/docs.
Tests: `pip install pytest httpx` then `python -m pytest -q`. Tests use synthetic historical data and mock the provider; they do not establish trading accuracy.
