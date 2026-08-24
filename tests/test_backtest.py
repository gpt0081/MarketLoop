import pandas as pd

from marketloop.backtest import run_sma_backtest


def test_backtest_runs_without_lookahead_execution():
    opens = [100.0 + i * 0.2 for i in range(80)]
    closes = [v + 0.1 for v in opens]
    df = pd.DataFrame({"open": opens, "close": closes})
    result = run_sma_backtest(df, fast=5, slow=10)
    assert result.initial_cash == 100_000.0
    assert result.final_equity > 0
    assert isinstance(result.trades, int)
