# MarketLoop

MarketLoop is a paper-trading research system for hourly market signals.

## Goals

- Pull historical and recent market data from Alpaca
- Evaluate strategies on confirmed 1-hour candles
- Keep trading in paper mode only by default
- Store decisions and portfolio snapshots locally
- Expose a mobile-friendly dashboard over the local network or Tailscale

## Mobile access over Tailscale

1. Install Tailscale on the computer running MarketLoop and on your phone.
2. Start MarketLoop with `marketloop web --host 0.0.0.0 --port 8765`.
3. On the computer, run `tailscale ip -4` or use its MagicDNS hostname.
4. From the phone, open `http://<TAILSCALE-IP>:8765`.

Alpaca API keys stay on the computer in `.env`; the browser never receives them.

## Status

Initial implementation in progress.
