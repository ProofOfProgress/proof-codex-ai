# Copy hub install scripts to C: and run (fixes WSL UNC parse errors).
# Run as Administrator: INSTALL_HUB_ALL_LOCAL.bat  OR  C:\ProofCodexInstall\INSTALL_HUB_ALL_LOCAL.ps1
param(
    [string]$RepoWin = ''
)

$ErrorActionPreference = 'Stop'
$Dest = 'C:\ProofCodexInstall'

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error 'Run as Administrator'
}

if (-not $RepoWin) {
    $RepoWin = (wsl.exe bash -lc "wslpath -w ~/proof-codex-ai 2>/dev/null").Trim()
}
if (-not $RepoWin -or -not (Test-Path -LiteralPath $RepoWin)) {
    Write-Error "WSL repo not found at ~/proof-codex-ai (RepoWin=$RepoWin)"
}

Write-Host ''
Write-Host '=== Proof Codex - hub install from C:\ProofCodexInstall ==='
Write-Host ('Repo: ' + $RepoWin)
Write-Host ''

New-Item -ItemType Directory -Force -Path $Dest | Out-Null

$copyCmd = 'mkdir -p /mnt/c/ProofCodexInstall && cp ~/proof-codex-ai/scripts/install_hub_windows_gateway.ps1 ~/proof-codex-ai/scripts/install_hub_watchdog.ps1 ~/proof-codex-ai/scripts/install_hub_never_sleep.ps1 ~/proof-codex-ai/scripts/install_hub_wslconfig.ps1 ~/proof-codex-ai/scripts/hub_watchdog.ps1 ~/proof-codex-ai/scripts/hub_print_secrets_for_cursor.ps1 /mnt/c/ProofCodexInstall/'
wsl.exe bash -lc $copyCmd

Write-Host '[OK] Scripts on C:\ProofCodexInstall'
Write-Host ''
Write-Host '=== Step 1/3: Gateway (SSH port 2222) ==='
powershell -NoProfile -ExecutionPolicy Bypass -File "$Dest\install_hub_windows_gateway.ps1" -RepoWin $RepoWin

Write-Host ''
Write-Host '=== Step 2/3: Watchdog ==='
powershell -NoProfile -ExecutionPolicy Bypass -File "$Dest\install_hub_watchdog.ps1" -RepoWin $RepoWin

Write-Host ''
Write-Host '=== Step 3/3: Never sleep ==='
powershell -NoProfile -ExecutionPolicy Bypass -File "$Dest\install_hub_never_sleep.ps1" -RepoWin $RepoWin

Write-Host ''
Write-Host '=== Cursor secrets (copy from here) ==='
powershell -NoProfile -ExecutionPolicy Bypass -File "$Dest\hub_print_secrets_for_cursor.ps1"
Write-Host ''
