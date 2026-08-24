#!/usr/bin/env bash
set -euo pipefail

if ! command -v tailscale >/dev/null 2>&1; then
  echo 'Tailscale CLI was not found. Install Tailscale and sign in first.' >&2
  exit 1
fi

TAILSCALE_IP="$(tailscale ip -4 | head -n 1)"
if [ -z "$TAILSCALE_IP" ]; then
  echo 'No Tailscale IPv4 address was found. Check that Tailscale is connected.' >&2
  exit 1
fi

if [ ! -x .venv/bin/python ]; then
  echo 'Virtual environment not found. Run scripts/install_macos.sh first.' >&2
  exit 1
fi

echo '[MarketLoop] Tailnet-only dashboard'
echo "Phone URL: http://${TAILSCALE_IP}:8765"
echo 'Keep this terminal open while testing.'

.venv/bin/python -m marketloop.cli web --host "$TAILSCALE_IP" --port 8765
