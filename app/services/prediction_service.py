import yfinance as yf
import pandas as pd
from datetime import datetime, timezone
from typing import Tuple
import ta

from app.schemas.stock import PredictionResult, TechnicalIndicators
from app.services.stock_service import format_nse_symbol


def calculate_indicators(df: pd.DataFrame) -> dict:
    required = ['Close', 'High', 'Low', 'Volume']
    if len(df) < 50 or any(column not in df for column in required):
        raise ValueError('At least 50 complete OHLCV observations are required.')
    import numpy as np
    if not np.isfinite(df[required].to_numpy(dtype=float)).all():
        raise ValueError('Historical prices contain missing or non-finite values.')
    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]
    indicators = {}

    rsi = ta.momentum.RSIIndicator(close=close, window=14)
    indicators["rsi"] = round(float(rsi.rsi().iloc[-1]), 2)

    macd_ind = ta.trend.MACD(close=close)
    indicators["macd"] = round(float(macd_ind.macd().iloc[-1]), 2)
    indicators["macd_signal"] = round(float(macd_ind.macd_signal().iloc[-1]), 2)

    indicators["sma_20"] = round(float(close.rolling(20).mean().iloc[-1]), 2)
    indicators["sma_50"] = round(float(close.rolling(50).mean().iloc[-1]), 2) if len(close) >= 50 else None
    indicators["ema_20"] = round(float(ta.trend.EMAIndicator(close=close, window=20).ema_indicator().iloc[-1]), 2)

    bb = ta.volatility.BollingerBands(close=close, window=20)
    indicators["bollinger_upper"] = round(float(bb.bollinger_hband().iloc[-1]), 2)
    indicators["bollinger_lower"] = round(float(bb.bollinger_lband().iloc[-1]), 2)

    indicators["volume_ma"] = round(float(volume.rolling(20).mean().iloc[-1]), 0)
    indicators["current_volume"] = int(volume.iloc[-1])

    return indicators


def generate_signal(price: float, indicators: dict) -> Tuple[str, float, list, str]:
    score = 0
    reasons = []
    max_score = 7

    rsi = indicators.get("rsi", 50)
    macd = indicators.get("macd", 0)
    macd_signal = indicators.get("macd_signal", 0)
    sma_20 = indicators.get("sma_20")
    sma_50 = indicators.get("sma_50")
    bb_upper = indicators.get("bollinger_upper")
    bb_lower = indicators.get("bollinger_lower")
    vol = indicators.get("current_volume", 0)
    vol_ma = indicators.get("volume_ma", 1)

    if rsi < 30:
        score += 2
        reasons.append(f"✅ RSI {rsi:.1f} — Oversold zone, rule contributes to BUY score")
    elif rsi > 70:
        score -= 2
        reasons.append(f"⚠️ RSI {rsi:.1f} — Overbought zone, rule contributes to SELL score")
    else:
        reasons.append(f"📊 RSI {rsi:.1f} — Normal range")

    if macd > macd_signal:
        score += 1.5
        reasons.append(f"✅ MACD ({macd:.2f}) > Signal ({macd_signal:.2f}) — MACD above signal line")
    else:
        score -= 1.5
        reasons.append(f"⚠️ MACD ({macd:.2f}) < Signal ({macd_signal:.2f}) — MACD at or below signal line")

    if sma_20:
        if price > sma_20:
            score += 1
            reasons.append(f"✅ Price ₹{price:.1f} > SMA20 ₹{sma_20:.1f} — Uptrend లో ఉంది")
        else:
            score -= 1
            reasons.append(f"⚠️ Price ₹{price:.1f} < SMA20 ₹{sma_20:.1f} — Downtrend లో ఉంది")

    if sma_20 and sma_50:
        if sma_20 > sma_50:
            score += 1
            reasons.append(f"✅ SMA20 > SMA50 — SMA20 above SMA50")
        else:
            score -= 1
            reasons.append(f"⚠️ SMA20 < SMA50 — SMA20 at or below SMA50")

    if bb_lower and bb_upper:
        if price <= bb_lower:
            score += 1
            reasons.append(f"✅ Price Bollinger lower band దగ్గర — BUY chance")
        elif price >= bb_upper:
            score -= 1
            reasons.append(f"⚠️ Price Bollinger upper band దగ్గర — SELL consider చేయండి")

    if vol_ma > 0:
        vol_ratio = vol / vol_ma
        if vol_ratio > 1.5 and score > 0:
            score += 0.5
            reasons.append(f"✅ Volume {vol_ratio:.1f}x average — Strong buying volume")

    signal_strength = round(min(abs(score) / max_score * 100, 100), 1)

    if score >= 2:
        signal = "BUY"
    elif score <= -2:
        signal = "SELL"
    else:
        signal = "HOLD"

    indicator_condition = 'EXTREME_RSI' if rsi > 70 or rsi < 30 else 'NORMAL_RSI'
    return signal, signal_strength, reasons, indicator_condition


def get_prediction(symbol: str) -> PredictionResult:
    fmt_symbol = format_nse_symbol(symbol)
    ticker = yf.Ticker(fmt_symbol)
    hist = ticker.history(period="6mo")

    if len(hist) < 50:
        raise ValueError(f"'{symbol}' కోసం sufficient data లేదు.")

    info = ticker.info
    current_price = float(hist["Close"].iloc[-1])
    company_name = info.get("longName") or info.get("shortName") or symbol

    ind_values = calculate_indicators(hist)
    signal, signal_strength, reasons, indicator_condition = generate_signal(current_price, ind_values)

    return PredictionResult(
        symbol=fmt_symbol,
        company_name=company_name,
        current_price=round(current_price, 2),
        signal=signal,
        signal_strength=signal_strength,
        reasons=reasons,
        indicator_condition=indicator_condition,
        indicators=TechnicalIndicators(
            symbol=fmt_symbol,
            rsi=ind_values.get("rsi"),
            macd=ind_values.get("macd"),
            macd_signal=ind_values.get("macd_signal"),
            sma_20=ind_values.get("sma_20"),
            sma_50=ind_values.get("sma_50"),
            ema_20=ind_values.get("ema_20"),
            bollinger_upper=ind_values.get("bollinger_upper"),
            bollinger_lower=ind_values.get("bollinger_lower"),
        ),
        timestamp=datetime.now(timezone.utc),
    )
