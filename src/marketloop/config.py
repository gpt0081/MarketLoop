from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    alpaca_api_key: str = os.getenv("ALPACA_API_KEY", "").strip()
    alpaca_secret_key: str = os.getenv("ALPACA_SECRET_KEY", "").strip()
    symbol: str = os.getenv("SYMBOL", "SPY").strip().upper() or "SPY"
    data_feed: str = os.getenv("DATA_FEED", "iex").strip().lower() or "iex"
    database_path: str = os.getenv("MARKETLOOP_DB", "marketloop.db").strip() or "marketloop.db"

    @property
    def alpaca_configured(self) -> bool:
        return bool(self.alpaca_api_key and self.alpaca_secret_key)


settings = Settings()
