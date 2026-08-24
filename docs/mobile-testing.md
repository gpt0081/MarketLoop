# Mobile testing over Tailscale

MarketLoop runs on the computer. The phone is only a browser client.

## Security model

- Alpaca keys live only in the host computer's `.env` file.
- `AlpacaGateway` is hard-coded to `paper=True`.
- The mobile dashboard exposes no order endpoint or order button.
- The Tailscale launcher binds Uvicorn to the computer's Tailscale IPv4 address instead of `0.0.0.0`.

## Windows

```powershell
git clone https://github.com/gpt0081/MarketLoop.git
cd MarketLoop
powershell -ExecutionPolicy Bypass -File scripts\install_windows.ps1
notepad .env
powershell -ExecutionPolicy Bypass -File scripts\run_tailscale_windows.ps1
```

The launcher prints a URL similar to `http://100.x.y.z:8765`. Open it on a phone signed in to the same Tailnet.

## macOS

```bash
git clone https://github.com/gpt0081/MarketLoop.git
cd MarketLoop
bash scripts/install_macos.sh
nano .env
bash scripts/run_tailscale_macos.sh
```

Open the printed `http://100.x.y.z:8765` URL from the phone.

## First checks

1. `marketloop check` should show the symbol, latest price, signal and paper account equity.
2. The dashboard should show `Alpaca 연결됨`.
3. Refreshing the dashboard must not create orders.
4. A new decision record is written only when a new hourly candle appears.
5. Use the dashboard's 365-day backtest button to verify that the API path works.
