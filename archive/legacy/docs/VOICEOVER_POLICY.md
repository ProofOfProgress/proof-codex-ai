# Voiceover for monetized Shorts (no mic required)

## Yes — you can monetize without recording your voice

YouTube **does not ban** channels for using TTS. YPP cares whether content is **original and valuable**, not whether a human recorded the audio.

What gets **demonetized** (not banned):

- Mass-produced slideshows with the same template every upload
- Generic AI scripts with no unique angle
- Repetitive “spam farm” channels at scale

**Soft Continuity is fine** if each Short has a distinct, helpful script (sleep, focus, boundaries) and you are not blasting 10 identical uploads per day.

Official policy name: **inauthentic content** (formerly repetitious).  
Source: [YouTube channel monetization policies](https://support.google.com/youtube/answer/1311392)

## How the bot handles voice (default: automatic)

`make video 6` now also creates **`voiceover.mp3`** (free neural TTS via edge-tts).

```bash
python3 -m shorts_bot.production.voice_cli --draft-id 6
# or: make voice 6  /  !voice 6
```

Output: `data/production/draft_6/voiceover.mp3`

CapCut: import `voiceover.mp3` + `images/` → follow `CAPCUT_TIMELINE.md` → upload.

Turn off auto-TTS in `.env`:

```
AUTO_GENERATE_VOICE=false
```

## Monetization checklist (TTS channel)

1. **Unique scripts** — bot drafts + your approvals (not copy-paste templates)
2. **Real help** — each Short solves one concrete problem
3. **Varied topics** — don’t upload the same hook 20 times
4. **Human editorial layer** — you approve/reject drafts (counts as creative input)
5. **Quality bar** — calm pacing, clean edit, not robotic spam cadence
6. **After upload** — run `sync` so the bot learns from analytics

## Voice quality settings (`.env`)

```
TTS_VOICE=en-US-AriaNeural
TTS_RATE=-8%
```

Slower rate sounds calmer and more “human” on Shorts.

## If YPP flags a video

Appeal with: original script, educational self-help value, non-repetitive format.  
Switching to your own voice is **not required** for reinstatement if the issue was “inauthentic” — fixing script originality usually is.
