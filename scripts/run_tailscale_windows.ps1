$ErrorActionPreference = "Stop"

$tailscale = Get-Command tailscale -ErrorAction SilentlyContinue
if ($tailscale) {
    $tailscaleExe = $tailscale.Source
} elseif (Test-Path "C:\Program Files\Tailscale\tailscale.exe") {
    $tailscaleExe = "C:\Program Files\Tailscale\tailscale.exe"
} else {
    throw "Tailscale CLI was not found. Install Tailscale and sign in first."
}

$tailscaleIp = (& $tailscaleExe ip -4 | Select-Object -First 1).Trim()
if (-not $tailscaleIp) {
    throw "No Tailscale IPv4 address was found. Check that Tailscale is connected."
}

$python = ".\.venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    throw "Virtual environment not found. Run scripts\install_windows.ps1 first."
}

Write-Host "[MarketLoop] Tailnet-only dashboard"
Write-Host "Phone URL: http://${tailscaleIp}:8765"
Write-Host "Keep this window open while testing."

& $python -m marketloop.cli web --host $tailscaleIp --port 8765
