# Voiceover — human vs generated audio

## Will YouTube ban the channel?

**No** — using text-to-speech alone does not get channels banned. Bans are for spam, scams, copyright abuse, or repeated policy violations.

What people worry about is **monetization** and **reach**, not instant bans.

## Risk ladder (lowest → highest)

| Method | Ban risk | Monetization / reach |
|--------|----------|----------------------|
| **Your own voice** | Lowest | Best — authentic, highest trust |
| **Free neural TTS** (`edge-tts`, bot command below) | Very low | Fine for new channels; sounds human-ish |
| **Paid AI voice clones / mass AI slop** | Low ban, higher demonetization | Repetitive faceless AI farms get limited |

Soft Continuity is **one helpful script at a time**, not a spam farm — that matters more than TTS vs human for policy.

## Bot: generate voiceover (optional)

Free, local, no API key — Microsoft Edge neural voices:

```bash
python3 -m shorts_bot.production.voice_cli --draft-id 6
```

Output: `data/production/draft_6/voiceover.mp3`

Then CapCut: import `voiceover.mp3` + `images/` per `CAPCUT_TIMELINE.md`.

**Tip:** If you use TTS, re-run `produce` with TurboScribe timestamps after upload for tighter image sync.

## Recommendation

- **First Short:** your voice if you can (2 minutes, phone mic)
- **Backup:** bot-generated `voiceover.mp3` when you're tired or testing the pipeline
