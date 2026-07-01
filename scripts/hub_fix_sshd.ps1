# Fix Windows OpenSSH sshd start (host keys, config test, DefaultShell fallback).
param(
    [int]$SshPort = 2222
)

$ErrorActionPreference = 'Stop'

function Write-Ok($m) { Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }

$sshdExe = Join-Path $env:ProgramFiles 'OpenSSH\sshd.exe'
$keygenExe = Join-Path $env:ProgramFiles 'OpenSSH\ssh-keygen.exe'
$SshdConfig = Join-Path $env:ProgramData 'ssh\sshd_config'

if (-not (Test-Path $sshdExe)) {
    Write-Error "OpenSSH Server not installed. Run INSTALL_HUB_ALL_LOCAL.ps1 first."
}

# Host keys (missing keys prevent sshd start on fresh install)
$hostKey = Join-Path $env:ProgramData 'ssh\ssh_host_ed25519_key'
if (-not (Test-Path $hostKey)) {
    Write-Warn 'Generating SSH host keys...'
    if (Test-Path $keygenExe) {
        & $keygenExe -A 2>&1 | Out-Null
    }
}

# Ensure port in config
if (Test-Path $SshdConfig) {
    $text = Get-Content $SshdConfig -Raw
    if ($text -notmatch "(?m)^Port\s+$SshPort\s*$") {
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
        $hasPubkey = $false
        foreach ($line in $out) {
            if ($line -match '^\s*PubkeyAuthentication\s+yes') { $hasPubkey = $true }
        }
        if (-not $hasPubkey) { $out.Add('PubkeyAuthentication yes') }
        Set-Content -Path $SshdConfig -Value ($out -join "`n") -Encoding ASCII
    }
}

$configTest = & $sshdExe -t 2>&1 | Out-String
if ($LASTEXITCODE -ne 0) {
    Write-Warn "sshd config test failed:"
    Write-Host $configTest
}

function Try-StartSshd {
    Stop-Service sshd -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Start-Service sshd -ErrorAction Stop
    $svc = Get-Service sshd
    if ($svc.Status -ne 'Running') {
        throw "sshd status is $($svc.Status)"
    }
}

try {
    Try-StartSshd
    Write-Ok "sshd running on port $SshPort"
} catch {
    Write-Warn "sshd failed with WSL default shell: $($_.Exception.Message)"
    Write-Warn 'Removing DefaultShell registry (retry plain OpenSSH)...'
    Remove-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShellCommandOption -ErrorAction SilentlyContinue
    try {
        Try-StartSshd
        Write-Ok "sshd running on port $SshPort (cmd default shell)"
        Write-Warn 'SSH lands in cmd first. Agent can run: wsl.exe bash -lc "..."'
    } catch {
        Write-Warn 'sshd still failed. Last 3 Application log events:'
        Get-WinEvent -LogName Application -MaxEvents 20 -ErrorAction SilentlyContinue |
            Where-Object { $_.ProviderName -like '*ssh*' -or $_.Message -like '*ssh*' } |
            Select-Object -First 3 |
            ForEach-Object { Write-Host $_.Message }
        throw $_
    }
}

$listening = netstat -an | Select-String "LISTENING" | Select-String ":$SshPort "
if ($listening) {
    Write-Ok "Port $SshPort is listening"
} else {
    Write-Warn "Port $SshPort not shown in netstat yet (may still be OK)"
}
