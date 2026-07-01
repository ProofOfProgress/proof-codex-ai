# Windows SSH gateway -> WSL. Survives WSL sshd banner-timeout issues.
# Run as Administrator: INSTALL_HUB_GATEWAY.bat
param(
    [string]$RepoWin = (Split-Path -Parent $PSScriptRoot),
    [int]$SshPort = 2222
)

$ErrorActionPreference = 'Stop'

function Write-Step($msg) { Write-Host "[OK] $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "[!] $msg" -ForegroundColor Yellow }

Write-Host ""
Write-Host "=== Proof Codex - Hub Windows Gateway (port $SshPort) ==="
Write-Host ""

if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)) {
    Write-Error "Run as Administrator (right-click INSTALL_HUB_GATEWAY.bat)"
}

if (-not (Test-Path -LiteralPath $RepoWin)) {
    Write-Error "Repo not found: $RepoWin"
}

# --- OpenSSH Server ---
$cap = Get-WindowsCapability -Online | Where-Object { $_.Name -like 'OpenSSH.Server*' }
if ($cap.State -ne 'Installed') {
    Write-Warn "Installing OpenSSH Server..."
    Add-WindowsCapability -Online -Name $cap.Name | Out-Null
}
Start-Service sshd -ErrorAction SilentlyContinue
Set-Service -Name sshd -StartupType Automatic
Write-Step "OpenSSH Server installed + auto-start"

# Default shell = WSL bash (SSH lands in Ubuntu)
$openSshKey = 'HKLM:\SOFTWARE\OpenSSH'
if (-not (Test-Path $openSshKey)) { New-Item -Path $openSshKey -Force | Out-Null }
New-ItemProperty -Path $openSshKey -Name DefaultShell -Value "$env:WINDIR\System32\wsl.exe" -PropertyType String -Force | Out-Null
New-ItemProperty -Path $openSshKey -Name DefaultShellCommandOption -Value '-d Ubuntu -e bash -l' -PropertyType String -Force | Out-Null
Write-Step "SSH default shell -> WSL Ubuntu"

# --- sshd_config: port + pubkey ---
$SshdConfig = Join-Path $env:ProgramData 'ssh\sshd_config'
if (-not (Test-Path $SshdConfig)) {
    Write-Error "Missing $SshdConfig"
}

$backup = "$SshdConfig.bak-gateway-$(Get-Date -Format yyyyMMdd)"
Copy-Item $SshdConfig $backup -Force
Write-Step "Backed up sshd_config -> $backup"

$lines = Get-Content $SshdConfig
$out = New-Object System.Collections.Generic.List[string]
$seenPort = $false
foreach ($line in $lines) {
    if ($line -match '^\s*Port\s+') {
        if (-not $seenPort) {
            $out.Add("Port $SshPort")
            $seenPort = $true
        }
        continue
    }
    $out.Add($line)
}
if (-not $seenPort) { $out.Add("Port $SshPort") }
if (-not ($out -match 'PubkeyAuthentication yes')) {
    $out.Add('PubkeyAuthentication yes')
}
Set-Content -Path $SshdConfig -Value ($out -join "`n") -Encoding ASCII
Write-Step "sshd listens on port $SshPort"

# Firewall
$ruleName = "ProofCodex-OpenSSH-$SshPort"
if (-not (Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Action Allow -Protocol TCP -LocalPort $SshPort | Out-Null
}
Write-Step "Firewall rule for TCP $SshPort"

Restart-Service sshd
Write-Step "sshd restarted"

# --- Agent public key from WSL ---
$WslUser = (wsl.exe whoami).Trim()
$PubKey = (wsl.exe -u $WslUser bash -lc "cat ~/.ssh/cursor_agent_ed25519.pub 2>/dev/null" 2>$null).Trim()
if (-not $PubKey) {
    Write-Warn "No cursor_agent key in WSL - run: bash scripts/hub_remote_setup.sh"
} else {
    $WinUser = $env:USERNAME
    $AuthDir = Join-Path $env:USERPROFILE '.ssh'
    $AuthFile = Join-Path $AuthDir 'authorized_keys'
    New-Item -ItemType Directory -Force -Path $AuthDir | Out-Null
    $existing = @()
    if (Test-Path $AuthFile) { $existing = Get-Content $AuthFile }
    if ($existing -notcontains $PubKey) {
        Add-Content -Path $AuthFile -Value $PubKey
    }
    icacls $AuthDir /inheritance:r /grant "${WinUser}:F" | Out-Null
    icacls $AuthFile /inheritance:r /grant "${WinUser}:F" | Out-Null
    Write-Step "Agent SSH key installed for Windows user $WinUser"
}

# --- .wslconfig (no idle shutdown) ---
& (Join-Path $PSScriptRoot 'install_hub_wslconfig.ps1')

# --- Tailscale on Windows (recommended over WSL-only) ---
$tsExe = Join-Path ${env:ProgramFiles} 'Tailscale\tailscale.exe'
if (-not (Test-Path $tsExe)) {
    Write-Warn "Tailscale Windows app not found."
    Write-Host "    Install: winget install Tailscale.Tailscale"
    Write-Host "    Log in once in the tray icon - stays up when laptop is locked."
} else {
    Write-Step "Tailscale Windows app found"
    $tsIp = & $tsExe ip -4 2>$null
    if ($tsIp) {
        Write-Host ""
        Write-Host "Windows Tailscale IP: $tsIp"
        Write-Host "Update Cursor secret HUB_SSH_HOST = $tsIp"
        Write-Host "Update Cursor secret HUB_SSH_PORT = $SshPort"
        Write-Host "Start a NEW cloud agent run after updating secrets."
    } else {
        Write-Warn "Tailscale not logged in - open tray icon and connect"
    }
}

Write-Host ""
Write-Host "=== Gateway install done ==="
Write-Host "Cloud agent connects: Windows Tailscale IP, port $SshPort, user $env:USERNAME"
Write-Host "Also run: INSTALL_HUB_WATCHDOG.bat + INSTALL_HUB_NEVER_SLEEP.bat"
Write-Host "Doc: docs/FOR_OWNER_HUB_ALWAYS_ON.md"
Write-Host ""
