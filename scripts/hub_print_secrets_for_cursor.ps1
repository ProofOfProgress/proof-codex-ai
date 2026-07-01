# Print Cursor Cloud Agent secrets after gateway install.
# Run in PowerShell (Admin not required). Paste output into Cursor -> Cloud Agent -> Secrets.
param(
    [int]$SshPort = 2222
)

$ErrorActionPreference = 'SilentlyContinue'

Write-Host ''
Write-Host '=== Cursor Cloud Agent secrets (hub laptop) ==='
Write-Host ''

$winUser = $env:USERNAME
Write-Host "HUB_SSH_USER = $winUser"
Write-Host "HUB_SSH_PORT = $SshPort"

$tsExe = Join-Path ${env:ProgramFiles} 'Tailscale\tailscale.exe'
$tsIp = ''
if (Test-Path $tsExe) {
    $tsIp = (& $tsExe ip -4 2>$null).Trim()
}
if ($tsIp) {
    Write-Host "HUB_SSH_HOST = $tsIp"
    Write-Host '  (HP hub desktop-ler4vhb only - NOT laptup main PC)'
} else {
    Write-Host 'HUB_SSH_HOST = (install Tailscale Windows app + log in on THIS hub laptop)'
    Write-Host '  winget install Tailscale.Tailscale'
}

$sshd = Get-Service sshd -ErrorAction SilentlyContinue
if ($sshd -and $sshd.Status -eq 'Running') {
    Write-Host "OpenSSH Server: Running on port $SshPort"
} else {
    Write-Host 'OpenSSH Server: NOT running - run hub_repair_install.ps1 as Admin'
}

Write-Host ''
Write-Host 'HUB_SSH_PRIVATE_KEY = (unchanged - same key from hub_remote_setup.sh)'
Write-Host 'TAILSCALE_AUTH_KEY = (unchanged)'
Write-Host ''
Write-Host 'After updating secrets: start a NEW cloud agent run, then say: try hub verify'
Write-Host ''
