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

$p = Get-Process Cursor -ErrorAction SilentlyContinue |
  Where-Object { $_.MainWindowTitle -like "*Cursor*" } |
  Select-Object -First 1
if (-not $p) { Write-Error "Cursor window not found"; exit 1 }

[Win32]::ShowWindow($p.MainWindowHandle, 9) | Out-Null
[Win32]::SetForegroundWindow($p.MainWindowHandle) | Out-Null

$r = New-Object Win32+RECT
[void][Win32]::GetWindowRect($p.MainWindowHandle, [ref]$r)
$w = $r.Right - $r.Left
$h = $r.Bottom - $r.Top

$ix = [int]($r.Left + $w * 0.45)
$iy = [int]($r.Top + $h * 0.90)
$sx = [int]($r.Left + $w * 0.78)
$sy = [int]($r.Top + $h * 0.90)
Write-Output "$ix $iy $sx $sy"
