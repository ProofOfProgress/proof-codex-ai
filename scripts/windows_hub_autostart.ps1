# Register Windows scheduled task — start hub 45s after login (no button click).
param(
    [string]$RepoWin = (Split-Path -Parent $PSScriptRoot)
)

$ErrorActionPreference = 'Stop'
$TaskName = 'ProofCodexHubAutoStart'

if (-not (Test-Path -LiteralPath $RepoWin)) {
    Write-Error "Repo not found: $RepoWin"
}

$RepoWsl = (wsl.exe wslpath -u $RepoWin).Trim()
if (-not $RepoWsl) {
    Write-Error 'wslpath failed — is WSL installed?'
}

$WslUser = (wsl.exe whoami).Trim()
$LogRel = 'data/desktop_hub/hub_autostart.log'
$Arg = "-u $WslUser bash -lc `"sleep 45 && cd '$RepoWsl' && bash scripts/hub_one_click_start.sh >> $LogRel 2>&1`""

$Action = New-ScheduledTaskAction -Execute 'wsl.exe' -Argument $Arg
$Trigger = New-ScheduledTaskTrigger -AtLogOn
$Trigger.Delay = 'PT45S'
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Hours 1)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $Action `
    -Trigger $Trigger `
    -Settings $Settings `
    -Description 'Proof Codex — SSH + Tailscale + desktop helper after Windows login' `
    -Force | Out-Null

Write-Host ""
Write-Host "OK — scheduled task registered: $TaskName"
Write-Host "Runs 45 seconds after you log into Windows."
Write-Host "Log: $RepoWin\$LogRel"
Write-Host ""
Write-Host "Also run FIX_HUB_ONCE.bat once if you never did sudo setup."
Write-Host ""
