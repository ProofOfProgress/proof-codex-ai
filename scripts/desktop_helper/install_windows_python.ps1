# Install Python 3.12 on Windows silently (hub laptop). Run from WSL via hub SSH.
$ErrorActionPreference = "Stop"

Write-Host "Installing Python 3.12 for Windows (needed for desktop helper)..."

$winget = Get-Command winget -ErrorAction SilentlyContinue
if ($winget) {
    winget install Python.Python.3.12 --accept-package-agreements --accept-source-agreements --disable-interactivity
    Write-Host "winget install finished."
    exit 0
}

Write-Host "winget not found - downloading python.org installer..."
$installer = Join-Path $env:TEMP "python-3.12-installer.exe"
$url = "https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe"
Invoke-WebRequest -Uri $url -OutFile $installer -UseBasicParsing
Start-Process -FilePath $installer -ArgumentList "/quiet InstallAllUsers=0 PrependPath=1 Include_launcher=1" -Wait
Write-Host "Python installer finished."
