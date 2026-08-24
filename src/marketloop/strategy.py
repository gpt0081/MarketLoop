from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

Signal = Literal["BUY", "HOLD", "SELL"]


@dataclass(frozen=True)
class SignalResult:
    signal: Signal
    close: float
    sma_fast: float | None
    sma_slow: float | None
    reason: str


def sma_trend_signal(df: pd.DataFrame, fast: int = 20, slow: int = 50) -> SignalResult:
    if df.empty or "close" not in df.columns:
        raise ValueError("close column is required")

    closes = pd.to_numeric(df["close"], errors="coerce").dropna()
    if closes.empty:
        raise ValueError("no valid close values")

    close = float(closes.iloc[-1])
    if len(closes) < slow:
        return SignalResult(
            signal="HOLD",
            close=close,
            sma_fast=None,
            sma_slow=None,
            reason=f"Need at least {slow} hourly candles; have {len(closes)}.",
        )

    fast_ma = float(closes.rolling(fast).mean().iloc[-1])
    slow_ma = float(closes.rolling(slow).mean().iloc[-1])
    prev_fast = float(closes.rolling(fast).mean().iloc[-2])
    prev_slow = float(closes.rolling(slow).mean().iloc[-2])

    if fast_ma > slow_ma and prev_fast <= prev_slow:
        return SignalResult("BUY", close, fast_ma, slow_ma, f"SMA{fast} crossed above SMA{slow}.")
    if fast_ma < slow_ma and prev_fast >= prev_slow:
        return SignalResult("SELL", close, fast_ma, slow_ma, f"SMA{fast} crossed below SMA{slow}.")

    trend = "above" if fast_ma >= slow_ma else "below"
    return SignalResult(
        "HOLD",
        close,
        fast_ma,
        slow_ma,
        f"No crossover. SMA{fast} remains {trend} SMA{slow}.",
    )
