# TikTok posting — use Zernio (recommended)

**Skip direct TikTok API OAuth** unless you have no choice. It’s developer portal, redirect URLs, token files per account, unaudited-app limits — a pain.

**Use Zernio instead:** connect TikTok accounts in their dashboard once; the bot posts with one API key.

---

## Why Zernio for bubble wrap (3–5 accounts)

| Direct TikTok API | Zernio |
|-------------------|--------|
| TikTok developer app + OAuth per account | Log in each TikTok in Zernio UI |
| Paste redirect URLs, token JSON files | Copy one `account_id` per account into `accounts.json` |
| Unaudited app → often private-only posts | Uses their approved integration |
| You maintain tokens / refresh | They handle connection |

Our code **defaults to Zernio** (`post_via: "zernio"` in `accounts.json`).

---

## Setup (one time)

### 1. Zernio account

1. Open https://zernio.com and sign up  
2. **Connect TikTok** for each bubble-wrap account (log in as that user in the browser when prompted)  
3. Repeat for account 2, 3, 4, 5…  

### 2. API key

Zernio dashboard → **API** → copy key  

Cursor → Secrets → add:

| Secret | Value |
|--------|--------|
| `ZERNIO_API_KEY` or `ZERNIO_API_TOKEN` | your key |

Then:

```bash
bash scripts/install.sh
```

### 3. List connected accounts (on VM)

```bash
python3 -c "
from shorts_bot.zernio.client import list_accounts
for a in list_accounts():
    print(a.get('platform'), a.get('_id') or a.get('id'), a.get('username') or a.get('name'))
"
```

Copy each TikTok **account id** into `data/tiktok_shop/accounts.json`.

### 4. Example — 3 bubble accounts

Copy `data/tiktok_shop/accounts.example.json` → `data/tiktok_shop/accounts.json`:

```json
{
  "accounts": [
    {
      "id": "bubble_1",
      "label": "Bubble account 1",
      "daily_limit": 10,
      "post_via": "zernio",
      "zernio_account_id": "PASTE_ZERNIO_ID_1"
    },
    {
      "id": "bubble_2",
      "label": "Bubble account 2",
      "daily_limit": 1,
      "post_via": "zernio",
      "zernio_account_id": "PASTE_ZERNIO_ID_2"
    },
    {
      "id": "bubble_3",
      "label": "Bubble account 3",
      "daily_limit": 5,
      "post_via": "zernio",
      "zernio_account_id": "PASTE_ZERNIO_ID_3"
    }
  ]
}
```

---

## Posting

```bash
python3 -m shorts_bot.tiktok_shop.factory_cli post --account bubble_1 --video PATH --caption "..."
```

---

## Sound + photo carousels (bubble wrap)

Zernio uses the same TikTok limits underneath:

- **Specific sound (Mackenzie):** use **ADB Lead 3** on a logged-in Android phone — `python3 -m shorts_bot.tiktok.adb_carousel_cli post --slide1 ... --slide2 ...` (opens Mackenzie deep link → Use sound → 2 photos). Or inbox draft + manual finish in app.
- **2-photo manual swipe:** needs photo carousel support (we’re building this; today both paths are mostly video)

---

## When to use direct TikTok API

Only if Zernio doesn’t work for you or you need a feature they lack. See `docs/FOR_OWNER_TIKTOK_SETUP.md` (hard mode).
