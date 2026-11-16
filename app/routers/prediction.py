from fastapi import APIRouter, HTTPException
from app.services.prediction_service import get_prediction
from app.schemas.stock import PredictionResult

router = APIRouter(prefix="/predict", tags=["🤖 Indicator signals"])


@router.get(
    "/{symbol}",
    response_model=PredictionResult,
    summary="Rule-based Buy/Sell/Hold signal",
    description="""
    Technical Analysis ఆధారంగా stock కోసం rule-based signal ఇస్తుంది.

    **Indicators used:**
    - RSI (Relative Strength Index)
    - MACD (Moving Average Convergence Divergence)
    - SMA 20 & SMA 50 (Simple Moving Averages)
    - Bollinger Bands
    - Volume Analysis

    **Signal:** BUY 🟢 | SELL 🔴 | HOLD 🟡

    ⚠️ **Disclaimer:** ఇవి educational purposes కోసం మాత్రమే. Real investment decisions కోసం financial advisor ని consult చేయండి.
    """,
)
def predict_stock(symbol: str):
    try:
        return get_prediction(symbol)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Indicator calculation failed; please retry.")


@router.post(
    "/bulk",
    summary="Bulk Indicator signals",
    description="Multiple stocks కోసం ఒకేసారి predictions తీసుకోవడం. Max 5 symbols.",
)
def bulk_predictions(symbols: list[str]):
    if len(symbols) > 5:
        raise HTTPException(
            status_code=400, detail="Maximum 5 symbols మాత్రమే allowed (heavy computation)."
        )

    results = []
    for sym in symbols:
        try:
            pred = get_prediction(sym)
            results.append({"success": True, "data": pred.model_dump()})
        except Exception as e:
            results.append({"success": False, "symbol": sym, "error": "Indicator calculation failed for this symbol."})

    return results
