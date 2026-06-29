# Install desktop helper deps on Windows (Python + pip required on Windows).
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "desktop_helper\_python.ps1")

$Root = Get-RepoRoot
Set-Location $Root
Write-Host "Repo folder:"
Write-Host "  $Root"
Write-Host ""

$pyInfo = Find-PythonExe
if (-not $pyInfo) {
    Write-Host "ERROR: Python not found on Windows."
    Write-Host ""
    Write-Host "Fix (one time):"
    Write-Host "  1. Open https://www.python.org/downloads/ in your browser"
    Write-Host "  2. Install Python 3.11+ for Windows"
    Write-Host "  3. CHECK the box: Add python.exe to PATH"
    Write-Host "  4. Run this installer again"
    Write-Host ""
    Write-Host "Or from Ubuntu (WSL) app run:"
    Write-Host "  cd ~/proof-codex-ai && bash scripts/desktop_helper/install_from_ubuntu.sh"
    exit 1
}

Write-Host "Using Python: $($pyInfo.Exe)"
$req = Join-Path $Root "scripts\desktop_helper\requirements.txt"
$launcher = $pyInfo.Launcher
$launchArgs = @($pyInfo.LauncherArgs + @("-m", "pip", "install", "--upgrade", "pip"))
& $launcher @launchArgs
$launchArgs = @($pyInfo.LauncherArgs + @("-m", "pip", "install", "-r", $req))
& $launcher @launchArgs

Write-Host ""
Write-Host "OK - desktop helper deps installed."
Write-Host "Next: copy data\desktop_hub\helper.env.example to helper.env and paste your token."
Write-Host 'Then double-click: scripts\START_DESKTOP_HELPER.bat'
