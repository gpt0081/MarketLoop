from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from .strategy import SignalResult


class Storage:
    def __init__(self, path: str):
        self.path = Path(path)
        self._init_db()

    def connect(self) -> sqlite3.Connection:
        con = sqlite3.connect(self.path)
        con.row_factory = sqlite3.Row
        return con

    def _init_db(self) -> None:
        with self.connect() as con:
            con.execute(
                """
                CREATE TABLE IF NOT EXISTS decisions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    created_at TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    signal TEXT NOT NULL,
                    close REAL NOT NULL,
                    sma_fast REAL,
                    sma_slow REAL,
                    reason TEXT NOT NULL
                )
                """
            )

    def save_decision(self, symbol: str, result: SignalResult) -> None:
        with self.connect() as con:
            con.execute(
                """
                INSERT INTO decisions(created_at, symbol, signal, close, sma_fast, sma_slow, reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    datetime.now(timezone.utc).isoformat(),
                    symbol,
                    result.signal,
                    result.close,
                    result.sma_fast,
                    result.sma_slow,
                    result.reason,
                ),
            )

    def recent_decisions(self, limit: int = 20) -> list[dict]:
        with self.connect() as con:
            rows = con.execute(
                "SELECT * FROM decisions ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
        return [dict(row) for row in rows]
