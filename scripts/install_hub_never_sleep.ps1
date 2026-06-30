# Keep hub laptop awake + restart hub on session unlock.
# Run as Administrator: INSTALL_HUB_NEVER_SLEEP.bat
param(
    [string]$RepoWin = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "=== Proof Codex — Hub Never Sleep ==="
Write-Host ""

# --- Power: no sleep / no hibernate on AC ---
powercfg /change standby-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change monitor-timeout-ac 0
powercfg /change monitor-timeout-dc 15
powercfg /change disk-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /hibernate off

$ultimate = 'e9a42b02-d5df-448d-aa00-03f14749eb61'
$high = '8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c'
$schemes = powercfg /list
if ($schemes -match $ultimate) {
    powercfg /setactive $ultimate | Out-Null
    Write-Host "[OK] Power plan: Ultimate Performance"
} else {
    powercfg /setactive $high | Out-Null
    Write-Host "[OK] Power plan: High performance"
}

reg add "HKLM\SYSTEM\CurrentControlSet\Control\Session Manager\Power" /v HiberbootEnabled /t REG_DWORD /d 0 /f | Out-Null
Write-Host "[OK] Fast Startup disabled"

if (-not (Test-Path -LiteralPath $RepoWin)) {
    Write-Error "Repo not found: $RepoWin"
}

$RepoWsl = (wsl.exe wslpath -u $RepoWin).Trim()
if (-not $RepoWsl) {
    Write-Error 'wslpath failed — is WSL installed?'
}

$WslUser = (wsl.exe whoami).Trim()
$LogRel = 'data/desktop_hub/hub_autostart.log'
$WslArg = "-u $WslUser bash -lc `"sleep 20 && cd '$RepoWsl' && bash scripts/hub_one_click_start.sh >> $LogRel 2>&1`""

# Session UNLOCK trigger — restarts hub after lock screen (not just reboot login)
$UnlockTask = 'ProofCodexHubOnUnlock'
$Xml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Proof Codex — restart hub after Windows unlock</Description>
  </RegistrationInfo>
  <Triggers>
    <SessionStateChangeTrigger>
      <Enabled>true</Enabled>
      <StateChange>SessionUnlock</StateChange>
    </SessionStateChangeTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <StartWhenAvailable>true</StartWhenAvailable>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>wsl.exe</Command>
      <Arguments>$WslArg</Arguments>
    </Exec>
  </Actions>
</Task>
"@

Register-ScheduledTask -TaskName $UnlockTask -Xml $Xml -Force | Out-Null
Write-Host "[OK] Scheduled task: $UnlockTask (on session unlock)"

Write-Host ""
Write-Host "DONE — hub should stay awake on AC power."
Write-Host "Keep laptop PLUGGED IN."
Write-Host "Settings -> Accounts -> Sign-in options -> Never require sign-in when away."
Write-Host "Also run INSTALL_HUB_AUTOSTART.bat if you have not (starts hub after reboot login)."
Write-Host "Doc: docs/FOR_OWNER_HUB_NEVER_SLEEP.md"
Write-Host ""
