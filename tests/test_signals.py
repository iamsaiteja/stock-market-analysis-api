import numpy as np
import pandas as pd
import pytest
from app.services import prediction_service as service

def history(n=60):
    close = np.arange(100., 100. + n)
    return pd.DataFrame({'Close': close, 'High': close+1, 'Low': close-1, 'Volume': np.full(n, 1000.)})

def test_insufficient_or_invalid_data_is_rejected():
    with pytest.raises(ValueError): service.calculate_indicators(history(30))
    df = history(); df.loc[0, 'Close'] = np.nan
    with pytest.raises(ValueError): service.calculate_indicators(df)

def test_response_does_not_claim_probability_or_fixed_price_targets(monkeypatch):
    class Ticker:
        info = {'longName': 'Sample'}
        def history(self, **kwargs): return history()
    monkeypatch.setattr(service.yf, 'Ticker', lambda symbol: Ticker())
    result = service.get_prediction('SAMPLE').model_dump()
    assert 0 <= result['signal_strength'] <= 100
    assert result['evaluated_accuracy'] is None
    assert result['method'] == 'rule_based_technical_indicators'
    assert not {'confidence', 'risk_level', 'target_price', 'stop_loss'} & result.keys()
    assert result['timestamp'].tzinfo is not None

def test_relationship_is_not_mislabeled_as_crossover():
    indicators = service.calculate_indicators(history())
    signal, strength, reasons, condition = service.generate_signal(159, indicators)
    assert signal in {'BUY', 'SELL', 'HOLD'}
    assert 0 <= strength <= 100
    assert not any('cross' in reason.lower() for reason in reasons)
