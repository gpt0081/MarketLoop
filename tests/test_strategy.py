import pandas as pd

from marketloop.strategy import sma_trend_signal


def test_hold_when_history_is_short():
    df = pd.DataFrame({"close": [100.0] * 10})
    result = sma_trend_signal(df)
    assert result.signal == "HOLD"
    assert result.sma_slow is None


def test_buy_on_fresh_crossover():
    closes = [100.0] * 50 + [200.0]
    df = pd.DataFrame({"close": closes})
    result = sma_trend_signal(df, fast=2, slow=3)
    assert result.signal == "BUY"
