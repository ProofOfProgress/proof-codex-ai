# Jumpscare roulette — Don't Blink retention

**Why:** If every Short scares at second 27, viewers swipe early. Russian-roulette timing keeps them watching.

## Profiles (rotate per `draft_id`)

| Profile | Draft % 5 | Scare beat | Viewer experience |
|---------|-----------|------------|-------------------|
| `finale` | 0 | Last segment | Classic — safe until the end |
| `early_snap` | 1 | ~40% | Hit early — "wait, already?" |
| `late_hold` | 2 | Last + sting at 94% | Maximum delay |
| `mid_twist` | 3 | ~55% | Twist mid, dread after |
| `double_tap` | 4 | Fake tease ~42% + real lunge last | Two scares |

## Wired into

- `jumpscare_timing.py` — plan per draft
- I2V — `jumpscare_lunge` on primary segment; `jumpscare_tease` on decoy
- Audio sting — `sting_start_seconds()` from manifest segment times
- TTS — `scare_sentence_indices()` for edge/resemble prosody
- Upload copy — profile-specific volume warning

## Draft map (launch queue)

| Draft | Profile (expected) |
|-------|-------------------|
| #2 LIVE | `late_hold` (draft_id % 5 = 2) |
| #3 | `mid_twist` |
| #4 | `double_tap` |
| #5 | `finale` |
| #6 | `early_snap` |
