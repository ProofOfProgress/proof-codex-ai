# Keep hub laptop awake + restart hub at Windows login.
# Run as Administrator: INSTALL_HUB_NEVER_SLEEP.bat
param(
    [string]$RepoWin = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'

Write-Host ""
Write-Host "=== Proof Codex - Hub Never Sleep ==="
Write-Host ""

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
    Write-Error 'wslpath failed - is WSL installed?'
}

$WslUser = (wsl.exe whoami).Trim()
$LogRel = 'data/desktop_hub/hub_autostart.log'
$BashCmd = "sleep 20 && cd '$RepoWsl' && bash scripts/hub_one_click_start.sh >> $LogRel 2>&1"
$WslArgs = "-u $WslUser bash -lc `"$BashCmd`""

$LoginTask = 'ProofCodexHubOnLogin'
$Action = New-ScheduledTaskAction -Execute 'wsl.exe' -Argument $WslArgs
$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
Register-ScheduledTask -TaskName $LoginTask -Action $Action -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Settings $Settings -Description 'Proof Codex hub start at Windows login' -Force | Out-Null
Write-Host "[OK] Scheduled task: $LoginTask (at login)"
Write-Host "[!] After unlock (not reboot): double-click HUB_RECOVERY.bat if agent offline"

Write-Host ""
Write-Host "DONE - hub should stay awake on AC power."
Write-Host "Keep laptop PLUGGED IN."
Write-Host "Settings -> Accounts -> Sign-in options -> Never require sign-in when away."
Write-Host "Also run INSTALL_HUB_AUTOSTART.bat if you have not (starts hub after reboot login)."
Write-Host "Doc: docs/FOR_OWNER_HUB_NEVER_SLEEP.md"
Write-Host ""
