# Report whether KeyFreeze process is running (for WSL agent).
$proc = Get-Process *KeyFreeze* -ErrorAction SilentlyContinue
if ($proc) {
    Write-Output 'running'
    exit 0
}
Write-Output 'stopped'
exit 1
