# Fix Windows OpenSSH sshd start (host keys, config test, DefaultShell fallback).
param(
    [int]$SshPort = 2222
)

$ErrorActionPreference = 'Stop'

function Write-Ok($m) { Write-Host "[OK] $m" -ForegroundColor Green }
function Write-Warn($m) { Write-Host "[!] $m" -ForegroundColor Yellow }

function Resolve-OpenSshExe($name) {
    $paths = @(
        (Join-Path $env:WINDIR "System32\OpenSSH\$name"),
        (Join-Path ${env:ProgramFiles} "OpenSSH\$name")
    )
    foreach ($p in $paths) {
        if (Test-Path -LiteralPath $p) { return $p }
    }
    return $null
}

function Repair-SshdConfigPort {
    param(
        [string]$ConfigPath,
        [int]$Port
    )
    if (-not (Test-Path -LiteralPath $ConfigPath)) { return }

    $lines = Get-Content -LiteralPath $ConfigPath
    $clean = New-Object System.Collections.Generic.List[string]
    foreach ($line in $lines) {
        if ($line -match '^\s*Port\s+\d+') { continue }
        $clean.Add($line)
    }

    $out = New-Object System.Collections.Generic.List[string]
    $portAdded = $false
    for ($i = 0; $i -lt $clean.Count; $i++) {
        $line = $clean[$i]
        $out.Add($line)
        if (-not $portAdded -and $line -match '^\s*#Port\s+\d+') {
            $out.Add("Port $Port")
            $portAdded = $true
        }
    }
    if (-not $portAdded) {
        $out.Insert(0, "Port $Port")
        $portAdded = $true
    }

    $hasPubkey = $false
    $inMatch = $false
    foreach ($line in $out) {
        if ($line -match '^\s*Match\b') { $inMatch = $true }
        if (-not $inMatch -and $line -match '^\s*PubkeyAuthentication\s+yes') { $hasPubkey = $true }
    }
    if (-not $hasPubkey) {
        $insertAt = 0
        for ($j = 0; $j -lt $out.Count; $j++) {
            if ($out[$j] -match '^\s*Match\b') { break }
            $insertAt = $j + 1
        }
        $out.Insert($insertAt, 'PubkeyAuthentication yes')
    }

    $final = New-Object System.Collections.Generic.List[string]
    $hasListenAll = $false
    foreach ($line in $out) {
        if ($line -match '^\s*ListenAddress\s+127\.') { continue }
        if ($line -match '^\s*ListenAddress\s+0\.0\.0\.0') { $hasListenAll = $true }
        $final.Add($line)
    }
    if (-not $hasListenAll) {
        $listenAt = 0
        for ($j = 0; $j -lt $final.Count; $j++) {
            if ($final[$j] -match '^\s*Port\s+\d+') { $listenAt = $j + 1; break }
        }
        $final.Insert($listenAt, 'ListenAddress 0.0.0.0')
    }

    Set-Content -Path $ConfigPath -Value ($final -join "`n") -Encoding ASCII
    Write-Ok "sshd_config repaired (Port $Port at global scope)"
}

$sshdExe = Resolve-OpenSshExe 'sshd.exe'
$keygenExe = Resolve-OpenSshExe 'ssh-keygen.exe'
$SshdConfig = Join-Path $env:ProgramData 'ssh\sshd_config'

if (-not $sshdExe) {
    Write-Error 'OpenSSH Server not found. Run: Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0'
}

if (-not (Get-Service sshd -ErrorAction SilentlyContinue)) {
    Write-Error 'OpenSSH sshd service missing. Re-run INSTALL_HUB_ALL_LOCAL.ps1 as Admin.'
}

$hostKey = Join-Path $env:ProgramData 'ssh\ssh_host_ed25519_key'
if (-not (Test-Path $hostKey)) {
    Write-Warn 'Generating SSH host keys...'
    if ($keygenExe) {
        & $keygenExe -A 2>&1 | Out-Null
    }
}

Repair-SshdConfigPort -ConfigPath $SshdConfig -Port $SshPort

function Test-SshdConfig {
    & $sshdExe -t 2>&1 | Out-Null
    return ($LASTEXITCODE -eq 0)
}

if (-not (Test-SshdConfig)) {
    Write-Warn 'sshd config still invalid after repair - restoring latest gateway backup...'
    $backup = Get-ChildItem (Join-Path $env:ProgramData 'ssh\sshd_config.bak-gateway-*') -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1
    if ($backup) {
        Copy-Item $backup.FullName $SshdConfig -Force
        Repair-SshdConfigPort -ConfigPath $SshdConfig -Port $SshPort
    }
}

if (-not (Test-SshdConfig)) {
    $err = (& $sshdExe -t 2>&1 | Out-String).Trim()
    Write-Error "sshd config test failed: $err"
}

Write-Ok 'sshd config test passed'

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
        Write-Warn 'Remote commands auto-wrap via wsl.exe in hub_lib.sh'
    } catch {
        Write-Warn 'sshd still failed. Last 3 Application log events:'
        Get-WinEvent -LogName Application -MaxEvents 20 -ErrorAction SilentlyContinue |
            Where-Object { $_.ProviderName -like '*ssh*' -or $_.Message -like '*ssh*' } |
            Select-Object -First 3 |
            ForEach-Object { Write-Host $_.Message }
        throw $_
    }
}

# DefaultShell wsl.exe often resets inbound Tailscale SSH at kex — use cmd + wsl wrap instead.
if (Get-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell -ErrorAction SilentlyContinue) {
    Write-Warn 'Removing WSL DefaultShell for reliable Tailscale SSH...'
    Remove-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShell -ErrorAction SilentlyContinue
    Remove-ItemProperty -Path 'HKLM:\SOFTWARE\OpenSSH' -Name DefaultShellCommandOption -ErrorAction SilentlyContinue
    Try-StartSshd
    Write-Ok 'sshd restarted without DefaultShell (hub_run uses wsl.exe wrap)'
}

$listening = netstat -an | Select-String 'LISTENING' | Select-String ":$SshPort "
if ($listening) {
    Write-Ok "Port $SshPort is listening"
} else {
    Write-Warn "Port $SshPort not shown in netstat yet (may still be OK)"
}

# Firewall: allow SSH on all profiles (Tailscale = Public profile)
$ruleName = "ProofCodex-OpenSSH-$SshPort"
$existing = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
if ($existing) {
    Set-NetFirewallRule -DisplayName $ruleName -Profile Any -Enabled True | Out-Null
    Write-Ok "Firewall rule updated (all profiles)"
} else {
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -Action Allow -Protocol TCP -LocalPort $SshPort -Profile Any | Out-Null
    Write-Ok "Firewall rule created (all profiles)"
}

# Ensure cloud agent key in Windows authorized_keys
$WslUser = (wsl.exe whoami).Trim()
$PubKey = (wsl.exe -u $WslUser bash -lc 'cat ~/.ssh/cursor_agent_ed25519.pub 2>/dev/null' 2>$null)
if ($PubKey) {
    $PubKey = $PubKey.Trim()
    $AuthDir = Join-Path $env:USERPROFILE '.ssh'
    $AuthFile = Join-Path $AuthDir 'authorized_keys'
    New-Item -ItemType Directory -Force -Path $AuthDir | Out-Null
    $existingKeys = @()
    if (Test-Path $AuthFile) { $existingKeys = Get-Content $AuthFile }
    if ($existingKeys -notcontains $PubKey) {
        Add-Content -Path $AuthFile -Value $PubKey
        Write-Ok 'Agent SSH public key added to authorized_keys'
    } else {
        Write-Ok 'Agent SSH public key already in authorized_keys'
    }
    icacls $AuthDir /inheritance:r /grant "$($env:USERNAME):F" | Out-Null
    icacls $AuthFile /inheritance:r /grant "$($env:USERNAME):F" | Out-Null
} else {
    Write-Warn 'No cursor_agent key in WSL - run: bash scripts/hub_remote_setup.sh'
}
