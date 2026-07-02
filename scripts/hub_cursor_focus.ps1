# Bring Cursor main window to front (largest Cursor.exe window).
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
foreach ($proc in Get-Process -ErrorAction SilentlyContinue | Where-Object { $_.ProcessName -ieq 'Cursor' }) {
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
  Write-Error "Cursor not found - open Cursor on the hub (proof-codex-ai folder) and retry"
  exit 1
}
[Win32]::ShowWindow($best.MainWindowHandle, 9) | Out-Null
Start-Sleep -Milliseconds 250
[Win32]::SetForegroundWindow($best.MainWindowHandle) | Out-Null
Write-Output "OK"
