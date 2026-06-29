# One phone first — finish 90% of hub development

**Yes.** Almost all phone code is shared. Wire **one phone**, prove **one slot** end-to-end, and phones 2–5 are mostly copy-paste (serial + optional coord tweaks).

---

## Which phone first?

| Priority | Slot | Why |
|----------|------|-----|
| **Start here** | **`phone_1`** (bubble / gspgsgsorip1) | Account + Zernio already live — full cloud → inbox → Mackenzie path works **today** |
| Later | **`phone_5`** (affiliate) | Needs purchased account (~$630) — same worker, different steps (product link) |

Use **Moto #2** (or whichever is logged into **gspgsgsorip1** bubble TikTok) as `phone_1`.

---

## One-time setup (hub laptop Ubuntu)

1. Plug phone into USB (direct cable OK until Amazon hub arrives)
2. On phone: **Settings → Developer options → USB debugging ON**
3. Unlock screen, tap **Allow** when USB debugging prompt appears

Then run:

```bash
cd ~/proof-codex-ai
bash scripts/hub_one_phone_setup.sh phone_1
```

That script:
- Installs ADB if needed
- Auto-binds the connected phone serial → `phone_1`
- Creates `data/phone_hub/ui_coords.json` with default taps
- Runs a **dry-run** smoke test (no real TikTok taps)

---

## Manual commands (same thing step-by-step)

```bash
python3 -m shorts_bot.phone_hub.cli setup-phone --slot phone_1
python3 -m shorts_bot.phone_hub.cli readiness --slot phone_1
python3 -m shorts_bot.phone_hub.cli test-job --slot phone_1 --run
```

---

## Real bubble test (when slides exist)

```bash
# Cloud or hub — builds carousel + Zernio inbox draft
python3 -m shorts_bot.tiktok_shop.factory_cli bubble-slides --subject frog
python3 -m shorts_bot.tiktok_shop.factory_cli post-carousel \
  --account bubble_gspgsgsorip1 --slide1 PATH/slide1.jpg --slide2 PATH/slide2.jpg --confirm

# Hub — finish on phone (Mackenzie + publish)
python3 -m shorts_bot.phone_hub.cli tick --slot phone_1 --confirm
```

---

## What's already coded (all 5 phones)

| Step | Bubble (`phone_1`) | Affiliate (`phone_5`) |
|------|-------------------|----------------------|
| Zernio → inbox draft | ✅ | ✅ (when account wired) |
| Hub job queue | ✅ | ✅ |
| Open TikTok → Inbox → Draft | ✅ | ✅ |
| Mackenzie sound | ✅ | — |
| Product link (orange cart) | — | ✅ |
| Publish | ✅ | ✅ |

**Only per-phone differences:** `adb_serial` in `devices.json` + optional coord tweaks in `ui_coords.json`.

---

## When Amazon hub arrives

1. Plug all phones into **powered USB hub**
2. Run `setup-phone` once per slot (or `bind-serial --slot phone_2 --serial SERIAL`)
3. Same worker — `tick --only-connected` skips unplugged slots

---

## Related

- Full 5-phone map: `FOR_OWNER_PHONE_HUB.md`
- Hub SSH: `FOR_OWNER_REMOTE_HUB_SSH.md`
