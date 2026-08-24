# MarketLoop

MarketLoop is an hourly market-research and paper-trading laboratory. It runs on a computer, keeps Alpaca credentials and SQLite data local, and exposes a read-only mobile dashboard through Tailscale.

## v0.1 scope

- Alpaca historical/recent US stock data
- Confirmed 1-hour candles
- Baseline SMA20/SMA50 trend signal
- No-lookahead backtest: a signal observed at one candle close executes at the next candle open
- Configurable slippage in the backtest
- Local SQLite decision history
- Alpaca Paper account status
- Mobile-responsive FastAPI dashboard
- Tailnet-only launch scripts for Windows and macOS
- No live-trading mode and no order endpoint in the mobile dashboard

## Architecture

```text
Alpaca Market Data
        |
        v
  AlpacaGateway  -----> Alpaca Paper account (read only in dashboard)
        |
        v
  Hourly Strategy
        |
        +------> SQLite decision log
        |
        +------> Backtest engine
        |
        v
   FastAPI dashboard
        |
   Tailscale address
        |
        v
     Phone browser
```

## Windows installation

```powershell
git clone https://github.com/gpt0081/MarketLoop.git
cd MarketLoop
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
```

Open `.env` and add **Alpaca Paper** credentials:

```env
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
SYMBOL=SPY
DATA_FEED=iex
```

Check the connection:

```powershell
.\.venv\Scripts\marketloop.exe check
```

Start the Tailnet-only dashboard:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\run_tailscale_windows.ps1
```

The script prints a URL such as:

```text
http://100.x.y.z:8765
```

Open that URL on a phone signed in to the same Tailscale network.

## macOS installation

```bash
git clone https://github.com/gpt0081/MarketLoop.git
cd MarketLoop
bash scripts/install_macos.sh
nano .env
bash scripts/run_tailscale_macos.sh
```

## Commands

```bash
marketloop check
marketloop backtest --days 365 --cash 100000
marketloop web --host 127.0.0.1 --port 8765
```

For remote mobile testing, prefer the supplied Tailscale launcher. It discovers the host computer's Tailscale IPv4 address and binds the web server to that address only, rather than exposing it on every network interface.

## Safety boundaries

`AlpacaGateway` constructs `TradingClient(..., paper=True)` unconditionally. MarketLoop v0.1 contains no live-account switch. The web UI is read-only and has no order API. API keys are read from `.env`, which is excluded by `.gitignore`.

This project is an experiment platform, not evidence that the baseline strategy is profitable. Compare every result with Buy & Hold and include trading costs before drawing conclusions.

See `docs/mobile-testing.md` for the phone test procedure.
