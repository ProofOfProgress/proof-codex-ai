# Keep hub alive — run every 3 min via scheduled task (login + unlock + interval).
param(
    [string]$RepoWin = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'SilentlyContinue'
$LogDir = Join-Path $RepoWin 'data\desktop_hub'
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$Log = Join-Path $LogDir 'hub_watchdog.log'

function Log($msg) {
    $line = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') $msg"
    Add-Content -Path $Log -Value $line
}

# Wake WSL (prevents idle VM shutdown)
wsl.exe -e true | Out-Null

$RepoWsl = (wsl.exe wslpath -u $RepoWin 2>$null).Trim()
if ($RepoWsl) {
    wsl.exe bash -lc "cd '$RepoWsl' && bash scripts/hub_wsl_fix_all.sh --quiet" | Out-Null
}

# Windows sshd on gateway port
$svc = Get-Service sshd -ErrorAction SilentlyContinue
if ($svc -and $svc.Status -ne 'Running') {
    Start-Service sshd
    Log 'started sshd'
}

# Windows Tailscale tray app — cannot restart headless; log if missing
$tsExe = Join-Path ${env:ProgramFiles} 'Tailscale\tailscale.exe'
if (Test-Path $tsExe) {
    $ip = & $tsExe ip -4 2>$null
    if (-not $ip) { Log 'Tailscale Windows not connected' }
}

Log 'tick ok'
