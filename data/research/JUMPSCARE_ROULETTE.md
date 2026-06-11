# Jumpscare timing — Don't Blink

**Policy (owner):** Scare at the **end** — a couple seconds before the video ends. **Not every video.**

## Profiles (rotate per `draft_id`)

| Profile | When (`draft_id % 3`) | Scare | Viewer experience |
|---------|----------------------|-------|-------------------|
| `finale` | 1, 2, 4, 5, 7, 8… (most) | Last beat + sting ~2s before end | Classic Don't Blink — earn the lunge |
| `suspense_replay` | 0, 3, 6, 9… (every 3rd) | **None** | Dread hold → Shorts auto-replay bait |

Removed: `early_snap`, `mid_twist`, `double_tap`, `late_hold` (scares mid-video broke VO/visual sync and felt random).

## Wired into

- `jumpscare_timing.py` — `has_jumpscare`, `sting_start_seconds()` → `total_duration - ~2s`
- I2V — `jumpscare_lunge` on finale last beat; `suspense_replay_hold` on replay drafts
- Render — visual flash/zoom only when `has_jumpscare`; slow hold on replay drafts
- TTS — jumpscare prosody on **last sentence only** (finale)
- Upload copy — volume warning only on finale drafts

## Draft map (launch queue)

| Draft | Profile |
|-------|---------|
| #2 LIVE | `finale` |
| #3 | `suspense_replay` |
| #4 | `finale` |
| #5 | `finale` |
| #6 | `suspense_replay` |
