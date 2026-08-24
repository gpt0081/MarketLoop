$ErrorActionPreference = "Stop"

Write-Host "[MarketLoop] Creating virtual environment..."
py -3 -m venv .venv

Write-Host "[MarketLoop] Installing package..."
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]"

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[MarketLoop] Created .env. Add your Alpaca PAPER API keys before running."
}

Write-Host "[MarketLoop] Installation complete."
Write-Host "Run: powershell -ExecutionPolicy Bypass -File scripts\run_tailscale_windows.ps1"
