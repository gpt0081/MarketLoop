from __future__ import annotations

import argparse

import uvicorn

from .alpaca_client import AlpacaGateway
from .backtest import run_sma_backtest
from .config import settings
from .strategy import sma_trend_signal


def cmd_check() -> int:
    if not settings.alpaca_configured:
        print("Alpaca credentials are not configured. Copy .env.example to .env first.")
        return 2
    gateway = AlpacaGateway(settings)
    bars = gateway.hourly_bars(settings.symbol, 30)
    if bars.empty:
        print("Connected, but no hourly bars were returned.")
        return 1
    signal = sma_trend_signal(bars)
    account = gateway.paper_account()
    print(f"symbol={settings.symbol} close={signal.close:.2f} signal={signal.signal}")
    print(f"reason={signal.reason}")
    print(f"paper_equity={account['equity']:.2f} buying_power={account['buying_power']:.2f}")
    return 0


def cmd_backtest(days: int, cash: float) -> int:
    gateway = AlpacaGateway(settings)
    bars = gateway.hourly_bars(settings.symbol, days)
    result = run_sma_backtest(bars, initial_cash=cash)
    for key, value in result.as_dict().items():
        print(f"{key}={value}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(prog="marketloop")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("check", help="Test Alpaca paper credentials and fetch recent hourly data")

    p_web = sub.add_parser("web", help="Run the read-only dashboard")
    p_web.add_argument("--host", default="127.0.0.1")
    p_web.add_argument("--port", default=8765, type=int)

    p_bt = sub.add_parser("backtest", help="Run the baseline SMA crossover backtest")
    p_bt.add_argument("--days", type=int, default=365)
    p_bt.add_argument("--cash", type=float, default=100_000.0)

    args = parser.parse_args()
    if args.command == "check":
        raise SystemExit(cmd_check())
    if args.command == "backtest":
        raise SystemExit(cmd_backtest(args.days, args.cash))
    if args.command == "web":
        uvicorn.run("marketloop.web:app", host=args.host, port=args.port, reload=False)


if __name__ == "__main__":
    main()
