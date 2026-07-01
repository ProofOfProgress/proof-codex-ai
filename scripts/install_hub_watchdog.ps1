# Register hub watchdog — every 3 minutes + at login + on unlock.
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

$Triggers = @(
    (New-ScheduledTaskTrigger -AtLogOn),
    (New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 3) -RepetitionDuration ([TimeSpan]::MaxValue))
)

# Session unlock (same as never-sleep script)
$UnlockXml = @"
<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers>
    <SessionStateChangeTrigger>
      <Enabled>true</Enabled>
      <StateChange>SessionUnlock</StateChange>
    </SessionStateChangeTrigger>
  </Triggers>
  <Actions>
    <Exec>
      <Command>powershell.exe</Command>
      <Arguments>-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File "$Ps1" -RepoWin "$RepoWin"</Arguments>
    </Exec>
  </Actions>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <StartWhenAvailable>true</StartWhenAvailable>
  </Settings>
</Task>
"@

Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Triggers[0] -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable) -Description 'Proof Codex hub watchdog (WSL + sshd)' -Force | Out-Null

Register-ScheduledTask -TaskName "${TaskName}Interval" -Action $Action -Trigger $Triggers[1] -Settings (New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable) -Description 'Proof Codex hub watchdog every 3 min' -Force | Out-Null

Register-ScheduledTask -TaskName "${TaskName}Unlock" -Xml $UnlockXml -Force | Out-Null

Write-Host ""
Write-Host "OK - watchdog tasks registered:"
Write-Host "  - at login"
Write-Host "  - every 3 minutes"
Write-Host "  - on session unlock"
Write-Host ('Log: ' + (Join-Path $RepoWin 'data/desktop_hub/hub_watchdog.log'))
Write-Host ""
