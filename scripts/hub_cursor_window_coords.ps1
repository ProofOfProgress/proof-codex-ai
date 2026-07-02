# Output: input_x input_y send_x send_y (space-separated) for Cursor composer.
Add-Type @"
using System;
using System.Runtime.InteropServices;
public class Win32 {
  [StructLayout(LayoutKind.Sequential)] public struct RECT { public int Left, Top, Right, Bottom; }
  [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr hWnd, out RECT r);
  [DllImport("user32.dll")] public static extern bool SetForegroundWindow(IntPtr hWnd);
  [DllImport("user32.dll")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);
}
"@

$best = $null
$bestArea = 0
foreach ($proc in Get-Process Cursor -ErrorAction SilentlyContinue) {
  if ($proc.MainWindowHandle -eq [IntPtr]::Zero) { continue }
  $r = New-Object Win32+RECT
  if (-not [Win32]::GetWindowRect($proc.MainWindowHandle, [ref]$r)) { continue }
  $w = $r.Right - $r.Left
  $h = $r.Bottom - $r.Top
  if ($w -le 0 -or $h -le 0) { continue }
  $area = $w * $h
  if ($area -gt $bestArea) {
    $best = $proc
    $bestArea = $area
  }
}
if (-not $best) {
  Write-Error "Cursor window not found - open Cursor on the hub and try again"
  exit 1
}

[Win32]::ShowWindow($best.MainWindowHandle, 9) | Out-Null
Start-Sleep -Milliseconds 200
[Win32]::SetForegroundWindow($best.MainWindowHandle) | Out-Null
Start-Sleep -Milliseconds 200

$r = New-Object Win32+RECT
[void][Win32]::GetWindowRect($best.MainWindowHandle, [ref]$r)
$w = $r.Right - $r.Left
$h = $r.Bottom - $r.Top
if ($w -le 100 -or $h -le 100) {
  Write-Error "Cursor window too small - restore/maximize Cursor and try again"
  exit 1
}

$ix = [int]($r.Left + $w * 0.45)
$iy = [int]($r.Top + $h * 0.90)
$sx = [int]($r.Left + $w * 0.78)
$sy = [int]($r.Top + $h * 0.90)
Write-Output "$ix $iy $sx $sy"
