# Start Windows desktop helper daemon (run in PowerShell on hub laptop, logged into Windows).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

if (-not $env:DESKTOP_HELPER_TOKEN) {
    Write-Host "Generate a random token, add DESKTOP_HELPER_TOKEN to Cursor Secrets, then:"
    Write-Host '  $env:DESKTOP_HELPER_TOKEN = "your-token-here"'
    exit 1
}

Set-Location $Root
Write-Host "Starting desktop helper on port $(if ($env:DESKTOP_HELPER_PORT) { $env:DESKTOP_HELPER_PORT } else { '9876' })..."
python scripts/desktop_helper/daemon.py
