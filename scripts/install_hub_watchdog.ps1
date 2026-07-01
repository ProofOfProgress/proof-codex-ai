# Register hub watchdog - at login + every 3 minutes.
param(
    [string]$RepoWin = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$TaskName = 'ProofCodexHubWatchdog'
$Ps1 = Join-Path $PSScriptRoot 'hub_watchdog.ps1'

if (-not (Test-Path -LiteralPath $Ps1)) {
    Write-Error "Missing $Ps1"
}

$Action = New-ScheduledTaskAction -Execute 'powershell.exe' `
    -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$Ps1`" -RepoWin `"$RepoWin`""

$Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger (New-ScheduledTaskTrigger -AtLogOn) -Settings $Settings -Description 'Proof Codex hub watchdog at login' -Force | Out-Null

# Every 3 min for 30 days (re-run install monthly or rely on login trigger)
$intervalTrigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 3) -RepetitionDuration (New-TimeSpan -Days 30)
try {
    Register-ScheduledTask -TaskName "${TaskName}Interval" -Action $Action -Trigger $intervalTrigger -Settings $Settings -Description 'Proof Codex hub watchdog every 3 min' -Force | Out-Null
} catch {
    Write-Warn "Interval task skipped (login watchdog still OK): $($_.Exception.Message)"
}

Write-Host ""
Write-Host "OK - watchdog tasks registered:"
Write-Host "  - at login"
Write-Host "  - every 3 minutes (30 day window)"
Write-Host ('Log: ' + (Join-Path $RepoWin 'data/desktop_hub/hub_watchdog.log'))
Write-Host ""
