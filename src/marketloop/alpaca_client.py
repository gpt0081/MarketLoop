from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pandas as pd
from alpaca.data.enums import DataFeed
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient

from .config import Settings


class AlpacaGateway:
    def __init__(self, settings: Settings):
        if not settings.alpaca_configured:
            raise RuntimeError("Alpaca credentials are missing. Copy .env.example to .env and add paper API keys.")
        self.settings = settings
        self.data = StockHistoricalDataClient(settings.alpaca_api_key, settings.alpaca_secret_key)
        # Deliberately paper-only. No live-trading mode exists in this gateway.
        self.trading = TradingClient(settings.alpaca_api_key, settings.alpaca_secret_key, paper=True)

    def _feed(self) -> DataFeed:
        return DataFeed.SIP if self.settings.data_feed == "sip" else DataFeed.IEX

    def hourly_bars(self, symbol: str, days: int = 30) -> pd.DataFrame:
        end = datetime.now(timezone.utc)
        start = end - timedelta(days=days)
        request = StockBarsRequest(
            symbol_or_symbols=[symbol],
            timeframe=TimeFrame.Hour,
            start=start,
            end=end,
            feed=self._feed(),
        )
        bars = self.data.get_stock_bars(request)
        df = bars.df.copy()
        if df.empty:
            return pd.DataFrame(columns=["timestamp", "open", "high", "low", "close", "volume"])

        df = df.reset_index()
        if "symbol" in df.columns:
            df = df[df["symbol"] == symbol].copy()
        keep = [c for c in ["timestamp", "open", "high", "low", "close", "volume"] if c in df.columns]
        return df[keep].sort_values("timestamp").reset_index(drop=True)

    def paper_account(self) -> dict[str, str | float | bool]:
        account = self.trading.get_account()
        return {
            "status": str(account.status),
            "currency": str(account.currency),
            "cash": float(account.cash),
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "trading_blocked": bool(account.trading_blocked),
        }
