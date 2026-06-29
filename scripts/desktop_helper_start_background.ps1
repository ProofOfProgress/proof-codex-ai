# Start Windows desktop helper in background (called from WSL or Task Scheduler).
$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $Root

$EnvFile = Join-Path $Root "data\desktop_hub\helper.env"
if (Test-Path $EnvFile) {
    Get-Content $EnvFile | ForEach-Object {
        if ($_ -match '^\s*#' -or $_ -notmatch '=') { return }
        $name, $value = $_ -split '=', 2
        $name = $name.Trim()
        $value = $value.Trim().Trim('"').Trim("'")
        if ($name -and -not (Get-Item "Env:$name" -ErrorAction SilentlyContinue)) {
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

if (-not $env:DESKTOP_HELPER_TOKEN) {
    Write-Error "Missing DESKTOP_HELPER_TOKEN — copy data/desktop_hub/helper.env.example to helper.env"
}

$LogDir = Join-Path $Root "data\desktop_hub"
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$LogFile = Join-Path $LogDir "daemon.log"
$PidFile = Join-Path $LogDir "daemon.pid"

$Daemon = Join-Path $Root "scripts\desktop_helper\daemon.py"
$Args = @($Daemon)

Start-Process -FilePath "python" -ArgumentList $Args -WorkingDirectory $Root `
    -WindowStyle Hidden -RedirectStandardOutput $LogFile -RedirectStandardError $LogFile

Start-Sleep -Seconds 2
Write-Host "Desktop helper started (log: $LogFile)"
