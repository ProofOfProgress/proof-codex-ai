# What InVideo AI receives — master system prompt

**InVideo is the soul of the channel.** Every MCP call and Agent One message is prefixed with the full context in:

`shorts_bot/invideo/invideo_master_prompt.md`

Our code wraps your per-video brief automatically:

```python
from shorts_bot.invideo.system_context import wrap_invideo_prompt
from shorts_bot.invideo.ms_byte import ms_byte_brief

brief = ms_byte_brief(product="Grok (xAI)", hook="Thirty bucks for Grok — most shouldn't pay.")
full = wrap_invideo_prompt(brief)
```

**Deep playbook:** `data/research/INVIDEO_MS_BYTE_QUALITY_PLAYBOOK.md`

---

## If you paste manually into Agent One

Open `shorts_bot/invideo/invideo_master_prompt.md`, copy all of it, then add:

```
--- VIDEO BRIEF ---

HOST: Ms. Byte — RTR_MsByte. Jenny 8-beat. ONE strength + ONE weakness. NO Pay/Skip/Wait.
Review [PRODUCT]. Hook: [CURIOSITY HOOK FIRST]. 9:16 Short. Basic ≤10 credits. Say "Twitter" not "X" in VO.
```

---

## What it tells InVideo

| Area | Content |
|------|---------|
| Identity | Rapid Tool Review — AI explains AI tools |
| Format | 9:16 YouTube Short, 25–35s, Jenny 8-beat script |
| Presenter | **Ms. Byte** — library character `RTR_MsByte`, 45–55% on screen |
| Visuals | Vertical-native stock + UI; no widescreen letterbox |
| Tone | Bubbly teacher + skeptical honesty |
| Verdict | Strength + weakness — **viewer decides** (no Pay/Skip/Wait) |
| TTS | Say "Twitter" — never speak "X" as a word |
| Avoid | Horror, listicles, AI Twin, fake tests, affiliate energy |
| Pipeline | Brief → InVideo writes script → Generate → export |

---

## Edit the prompt

Change `invideo_master_prompt.md` — all generate/agent commands pick it up on next run.

Do **not** confuse with `docs/CHANNEL_BOT_BRIEF.md` (that one is for **Cursor agents**, not InVideo).
