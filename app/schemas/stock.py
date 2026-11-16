from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class StockPrice(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    previous_close: float
    change: float
    change_percent: float
    day_high: float
    day_low: float
    volume: int
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    timestamp: datetime


class HistoricalData(BaseModel):
    symbol: str
    period: str
    data: list[dict]


class TechnicalIndicators(BaseModel):
    symbol: str
    rsi: Optional[float] = None
    macd: Optional[float] = None
    macd_signal: Optional[float] = None
    sma_20: Optional[float] = None
    sma_50: Optional[float] = None
    ema_20: Optional[float] = None
    bollinger_upper: Optional[float] = None
    bollinger_lower: Optional[float] = None


class PredictionResult(BaseModel):
    symbol: str
    company_name: str
    current_price: float
    signal: str
    signal_strength: float = Field(ge=0, le=100, description="Normalized manual rule score, not probability or measured accuracy")
    method: str = "rule_based_technical_indicators"
    evaluated_accuracy: Optional[float] = None
    reasons: list[str]
    indicator_condition: str
    indicators: TechnicalIndicators
    timestamp: datetime


class ErrorResponse(BaseModel):
    error: str
    detail: str
