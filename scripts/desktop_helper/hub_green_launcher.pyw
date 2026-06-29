"""Big green desktop button — START HUB (Windows, no terminal needed)."""

from __future__ import annotations

import subprocess
import tkinter as tk
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
START_SH = ROOT / "scripts" / "hub_one_click_start.sh"


def _wsl_repo() -> str:
    return "~/proof-codex-ai"


def start_hub() -> None:
    cmd = f"cd {_wsl_repo()} && bash scripts/hub_one_click_start.sh"
    subprocess.Popen(
        ["wsl.exe", "bash", "-lc", cmd],
        creationflags=getattr(subprocess, "CREATE_NEW_CONSOLE", 0),
    )
    status_var.set("Starting… check the green window for progress.")
    btn.config(state=tk.DISABLED)
    root.after(8000, lambda: btn.config(state=tk.NORMAL))


root = tk.Tk()
root.title("Proof Codex Hub")
root.geometry("360x260")
root.configure(bg="#0f172a")
root.resizable(False, False)

title = tk.Label(
    root,
    text="Proof Codex",
    font=("Segoe UI", 14),
    fg="#94a3b8",
    bg="#0f172a",
)
title.pack(pady=(16, 4))

status_var = tk.StringVar(value="One click after reboot — agent can connect.")
status = tk.Label(
    root,
    textvariable=status_var,
    font=("Segoe UI", 9),
    fg="#64748b",
    bg="#0f172a",
    wraplength=320,
)
status.pack(pady=(0, 12))

btn = tk.Button(
    root,
    text="START HUB",
    font=("Segoe UI", 22, "bold"),
    bg="#22c55e",
    fg="white",
    activebackground="#16a34a",
    activeforeground="white",
    relief=tk.FLAT,
    cursor="hand2",
    width=14,
    height=2,
    command=start_hub,
)
btn.pack(pady=8)

hint = tk.Label(
    root,
    text="SSH · Tailscale · Desktop helper",
    font=("Segoe UI", 9),
    fg="#475569",
    bg="#0f172a",
)
hint.pack(pady=(8, 12))

root.mainloop()
