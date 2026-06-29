# Desktop helper — keyboard/mouse on your HP laptop (Windows)

**Do not type `\\wsl.localhost\...` paths in PowerShell.** Use the steps below.

---

## What went wrong (if you saw errors)

| Error | Meaning |
|-------|---------|
| `CD \\wsl.localhost\... does not exist` | Don't `cd` to WSL paths manually in PowerShell — use the `.bat` files below |
| `pip is not recognized` | Python isn't installed on **Windows** yet (WSL Python is separate) |
| Token errors | Open `helper.env` — token must be **one line, no spaces** |

---

## Setup — pick ONE path

### Path A — easiest (Ubuntu app on the laptop)

1. Open **Ubuntu** from the Start menu  
2. Run:

```bash
cd ~/proof-codex-ai
git pull
bash scripts/desktop_helper/install_from_ubuntu.sh
```

3. Copy token file:

```bash
cp data/desktop_hub/helper.env.example data/desktop_hub/helper.env
nano data/desktop_hub/helper.env
```

Paste your token on the `DESKTOP_HELPER_TOKEN=` line — **no spaces**. Save (Ctrl+O, Enter, Ctrl+X).

4. In **Windows File Explorer**, open the folder the script printed (under `scripts`), double-click:

- **`INSTALL_DESKTOP_HELPER.bat`** — if install didn't finish  
- **`START_DESKTOP_HELPER.bat`** — starts the helper  

---

### Path B — Windows only (File Explorer)

1. Install **Python for Windows**: https://www.python.org/downloads/  
   - Check **"Add python.exe to PATH"** during install  

2. In File Explorer address bar, try **one** of these until a folder opens:

```
\\wsl.localhost\Ubuntu\home\isaac\proof-codex-ai\scripts
```

or

```
\\wsl$\Ubuntu\home\isaac\proof-codex-ai\scripts
```

*(Use your real Linux username if not `isaac` — in Ubuntu run `whoami`.)*

3. Double-click **`INSTALL_DESKTOP_HELPER.bat`**  
4. Copy `helper.env.example` → `helper.env` in `data\desktop_hub\` — paste token (**no spaces**)  
5. Double-click **`START_DESKTOP_HELPER.bat`**

---

## helper.env format (important)

```
DESKTOP_HELPER_TOKEN=abc123yourtokenhere
```

- No spaces around `=`  
- No spaces inside the token  
- Same token as **Cursor → Cloud Agent → Secrets**

---

## Check it worked

From **Ubuntu**:

```bash
cd ~/proof-codex-ai
python3 -m shorts_bot.desktop_hub.cli ping
```

Should say `desktop helper alive`. If not, open `data/desktop_hub/daemon.log` on Windows.

---

## Daily pre-launch CEO mission

See **`docs/FOR_OWNER_DAILY_PRELAUNCH.md`** — the scheduled click sends the cloud agent your daily video plan.

---

## Agent can start helper remotely

```bash
python3 -m shorts_bot.desktop_hub.cli ensure --via-hub
```

(Still needs Python + helper installed on Windows first.)

---

## Related

- Phone hub: `FOR_OWNER_PHONE_HUB.md`  
- Daily CEO mission: `FOR_OWNER_DAILY_PRELAUNCH.md`
