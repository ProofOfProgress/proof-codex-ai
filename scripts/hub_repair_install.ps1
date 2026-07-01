# Repair hub install after partial failure (sshd, tasks, ASCII scripts).
# Run as Administrator: powershell -ExecutionPolicy Bypass -File C:\ProofCodexInstall\hub_repair_install.ps1
param(
    [string]$RepoWin = '',
    [int]$SshPort = 2222
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

Write-Host ''
Write-Host '=== Proof Codex - hub repair install ==='
Write-Host ''

$copyCmd = 'mkdir -p /mnt/c/ProofCodexInstall && cp ~/proof-codex-ai/scripts/install_hub_windows_gateway.ps1 ~/proof-codex-ai/scripts/install_hub_watchdog.ps1 ~/proof-codex-ai/scripts/install_hub_never_sleep.ps1 ~/proof-codex-ai/scripts/install_hub_wslconfig.ps1 ~/proof-codex-ai/scripts/hub_watchdog.ps1 ~/proof-codex-ai/scripts/hub_print_secrets_for_cursor.ps1 ~/proof-codex-ai/scripts/hub_fix_sshd.ps1 ~/proof-codex-ai/scripts/hub_repair_install.ps1 /mnt/c/ProofCodexInstall/'
wsl.exe bash -lc $copyCmd

Write-Host '[1/3] Gateway + sshd fix...'
powershell -NoProfile -ExecutionPolicy Bypass -File "$Dest\install_hub_windows_gateway.ps1" -RepoWin $RepoWin -SshPort $SshPort

Write-Host ''
Write-Host '[2/3] Watchdog + never sleep...'
powershell -NoProfile -ExecutionPolicy Bypass -File "$Dest\install_hub_watchdog.ps1" -RepoWin $RepoWin
powershell -NoProfile -ExecutionPolicy Bypass -File "$Dest\install_hub_never_sleep.ps1" -RepoWin $RepoWin

Write-Host ''
Write-Host '[3/3] Cursor secrets...'
powershell -NoProfile -ExecutionPolicy Bypass -File "$Dest\hub_print_secrets_for_cursor.ps1" -SshPort $SshPort
Write-Host ''
