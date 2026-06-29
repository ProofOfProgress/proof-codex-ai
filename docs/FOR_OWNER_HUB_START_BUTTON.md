# One-click hub start after Windows reboot

**What this does:** one double-click starts everything the cloud agent needs:

- SSH (so the agent can reach Ubuntu)
- Tailscale (private network)
- Desktop helper (keyboard/mouse + KeyFreeze unlock)

**What it does NOT do:** log you into Windows — you still enter your PIN after reboot once.

---

## Install the button (one time)

1. Log into **Windows**
2. Open the repo `scripts` folder in File Explorer  
   (`\\wsl$\Ubuntu\home\isaac\proof-codex-ai\scripts` or your path)
3. Double-click **`INSTALL_HUB_START_BUTTON.bat`**

That puts on your **Desktop**:

| Shortcut | What it looks like |
|----------|-------------------|
| **START HUB (Proof Codex).bat** | Green text window — always works |
| **START HUB Button.pyw** | Big green **START HUB** button (needs Windows Python) |

---

## After every reboot

1. Log into Windows (PIN)
2. Double-click **START HUB (Proof Codex)** on the Desktop
3. If Ubuntu asks for a password — type it **once**, press Enter
4. Wait for **HUB READY**

Then tell the agent: **“hub’s back”**

---

## Can the agent log in for me?

**No.** The agent cannot type your Windows PIN or unlock the lock screen.

After **you** log in and click **START HUB**, the agent can:

- SSH into Ubuntu
- Run bubble batch generation
- Lock/unlock KeyFreeze (if desktop helper is up)

---

## Generate 10 bubble clips (stored only)

No TikTok. No Zernio. Files sit in `data/bubble_wrap/slides/`.

From **Ubuntu** on the hub (saves Cursor agent quota):

```bash
cd ~/proof-codex-ai
python3 -m shorts_bot.tiktok_shop.factory_cli bubble-batch --count 10
```

Review the manifest path it prints (`data/bubble_wrap/batches/batch_*.json`).

**Tip:** With low Cursor auto-usage left, run this **on the hub** — it uses **Gemini API** (your image key), not the cloud agent chat quota.

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| “Ubuntu password” every time | Normal first click after reboot — or set up passwordless sudo later |
| Desktop helper failed | Windows must be logged in — run `START_DESKTOP_HELPER.bat` once |
| Green button does nothing | Use the `.bat` shortcut instead — it always opens a visible window |

---

## Related

- Remote hub SSH: `FOR_OWNER_REMOTE_HUB_SSH.md`
- Desktop helper: `FOR_OWNER_DESKTOP_HELPER.md`
- Bubble format: `data/research/course/BUBBLE_WRAP.md`
