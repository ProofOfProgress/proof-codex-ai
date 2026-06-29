# Register Windows scheduled task — start hub 45s after login (no button click).
param(
    [string]$RepoWin = ''
)

$ErrorActionPreference = 'Stop'
$TaskName = 'ProofCodexHubAutoStart'

if (-not $RepoWin) {
    $RepoWsl = (wsl.exe bash -lc 'readlink -f "$HOME/proof-codex-ai"').Trim()
    if (-not $RepoWsl) {
        Write-Error 'Could not find ~/proof-codex-ai in WSL'
    }
    $check = wsl.exe test -f "$RepoWsl/scripts/hub_one_click_start.sh"
    if ($LASTEXITCODE -ne 0) {
        Write-Error "Hub start script missing in WSL repo: $RepoWsl"
    }
    $RepoWin = (wsl.exe wslpath -w $RepoWsl).Trim()
}

if (-not (Test-Path -LiteralPath $RepoWin)) {
    Write-Error "Repo not found: $RepoWin"
}

$RepoWsl = (wsl.exe wslpath -u $RepoWin).Trim()
if (-not $RepoWsl) {
    Write-Error 'wslpath failed - is WSL installed?'
}

$WslUser = (wsl.exe whoami).Trim()
$LogRel = 'data/desktop_hub/hub_autostart.log'
$Inner = "sleep 45 && cd '$RepoWsl' && bash scripts/hub_one_click_start.sh >> $LogRel 2>&1"
$Arg = "-u $WslUser bash -lc ""$Inner"""

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
    -Description 'Proof Codex hub start after Windows login' `
    -Force | Out-Null

Write-Host ''
Write-Host "OK - scheduled task registered: $TaskName"
Write-Host 'Runs 45 seconds after Windows login.'
Write-Host "Log: $RepoWin\$LogRel"
Write-Host ''
Write-Host 'Run FIX HUB ONCE on Desktop once for passwordless sudo after reboot.'
Write-Host ''
