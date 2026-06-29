# Install desktop helper Python deps on Windows PowerShell.
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
Set-Location $Root
python -m pip install -r scripts/desktop_helper/requirements.txt
Write-Host "Desktop helper deps installed."
Write-Host "Next: set DESKTOP_HELPER_TOKEN and run scripts/desktop_helper_start.ps1"
