#!/usr/bin/env bash
set -euo pipefail

python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -e '.[dev]'

if [ ! -f .env ]; then
  cp .env.example .env
  echo '[MarketLoop] Created .env. Add your Alpaca PAPER API keys before running.'
fi

echo '[MarketLoop] Installation complete.'
echo 'Run: bash scripts/run_tailscale_macos.sh'
