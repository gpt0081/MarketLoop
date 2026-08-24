from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class BacktestResult:
    initial_cash: float
    final_equity: float
    return_pct: float
    buy_hold_pct: float
    trades: int
    max_drawdown_pct: float

    def as_dict(self) -> dict[str, float | int]:
        return {
            "initial_cash": round(self.initial_cash, 2),
            "final_equity": round(self.final_equity, 2),
            "return_pct": round(self.return_pct, 2),
            "buy_hold_pct": round(self.buy_hold_pct, 2),
            "trades": self.trades,
            "max_drawdown_pct": round(self.max_drawdown_pct, 2),
        }


def run_sma_backtest(
    df: pd.DataFrame,
    initial_cash: float = 100_000.0,
    fast: int = 20,
    slow: int = 50,
    slippage_bps: float = 2.0,
) -> BacktestResult:
    if len(df) < slow + 2:
        raise ValueError(f"Need at least {slow + 2} bars for backtest")

    data = df.copy().reset_index(drop=True)
    data["close"] = pd.to_numeric(data["close"], errors="coerce")
    data["open"] = pd.to_numeric(data["open"], errors="coerce")
    data = data.dropna(subset=["open", "close"]).reset_index(drop=True)
    data["fast"] = data["close"].rolling(fast).mean()
    data["slow"] = data["close"].rolling(slow).mean()

    cash = float(initial_cash)
    shares = 0.0
    trades = 0
    equity_curve: list[float] = []
    slip = slippage_bps / 10_000.0

    # Signal is observed at bar i close and executed at bar i+1 open.
    for i in range(slow, len(data) - 1):
        prev = data.iloc[i - 1]
        cur = data.iloc[i]
        next_open = float(data.iloc[i + 1]["open"])

        cross_up = cur["fast"] > cur["slow"] and prev["fast"] <= prev["slow"]
        cross_down = cur["fast"] < cur["slow"] and prev["fast"] >= prev["slow"]

        if cross_up and shares == 0 and cash > 0:
            fill = next_open * (1.0 + slip)
            shares = cash / fill
            cash = 0.0
            trades += 1
        elif cross_down and shares > 0:
            fill = next_open * (1.0 - slip)
            cash = shares * fill
            shares = 0.0
            trades += 1

        mark = float(data.iloc[i + 1]["close"])
        equity_curve.append(cash + shares * mark)

    if shares > 0:
        cash = shares * float(data.iloc[-1]["close"]) * (1.0 - slip)
        shares = 0.0
        trades += 1

    final_equity = cash
    return_pct = (final_equity / initial_cash - 1.0) * 100.0
    buy_hold_pct = (float(data.iloc[-1]["close"]) / float(data.iloc[slow]["close"]) - 1.0) * 100.0

    peak = initial_cash
    max_dd = 0.0
    for equity in equity_curve:
        peak = max(peak, equity)
        drawdown = (equity / peak - 1.0) * 100.0
        max_dd = min(max_dd, drawdown)

    return BacktestResult(
        initial_cash=initial_cash,
        final_equity=final_equity,
        return_pct=return_pct,
        buy_hold_pct=buy_hold_pct,
        trades=trades,
        max_drawdown_pct=max_dd,
    )
