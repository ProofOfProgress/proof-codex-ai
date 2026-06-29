# Start desktop helper in background (Windows).
$ErrorActionPreference = "Stop"
. (Join-Path $PSScriptRoot "desktop_helper\_python.ps1")

$Root = Get-RepoRoot
Set-Location -LiteralPath $Root

if (-not (Test-HelperEnv -Root $Root)) { exit 1 }
Import-HelperEnv -Root $Root | Out-Null

if (-not $env:DESKTOP_HELPER_TOKEN) {
    Write-Error "DESKTOP_HELPER_TOKEN empty in data\desktop_hub\helper.env"
}

$pyInfo = Find-PythonExe
if (-not $pyInfo) {
    Write-Host "ERROR: Python not found. Run scripts\INSTALL_DESKTOP_HELPER.bat first."
    exit 1
}

$LogDir = Join-Path $Root "data\desktop_hub"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir "daemon.log"
$Daemon = Join-Path $Root "scripts\desktop_helper\daemon.py"
$pyArgs = @($pyInfo.LauncherArgs + @($Daemon))

Start-Process -FilePath $pyInfo.Launcher -ArgumentList $pyArgs -WorkingDirectory $Root `
    -WindowStyle Hidden -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile

Start-Sleep -Seconds 2
Write-Host "Desktop helper started."
Write-Host "Log: $LogFile"
