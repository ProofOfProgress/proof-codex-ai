# What InVideo AI receives — master system prompt

**InVideo is the soul of the channel.** Every MCP call and Agent One message is prefixed with the full context in:

`shorts_bot/invideo/invideo_master_prompt.md`

Our code wraps your per-video brief automatically:

```python
from shorts_bot.invideo.system_context import wrap_invideo_prompt
full = wrap_invideo_prompt("30s NotebookLM review — Pay Skip Wait, 9:16, my twin")
```

---

## If you paste manually into Agent One

Open `shorts_bot/invideo/invideo_master_prompt.md`, copy all of it, then add:

```
--- VIDEO BRIEF ---

Review [PRODUCT]. Hook: [HOOK]. Verdict: Pay, Skip, or Wait. 9:16 Short, my AI twin.
```

---

## What it tells InVideo

| Area | Content |
|------|---------|
| Identity | AI product review channel, honest verdicts |
| Format | 9:16 YouTube Short, 25–35s, 4-beat script |
| Presenter | Owner's AI Twin always |
| Visuals | No widescreen stock in vertical (v1 lesson) |
| Tone | Skeptical but fair, no hype |
| Verdict | Pay / Skip / Wait every video |
| Avoid | Horror, listicles, fake tests, affiliate energy |
| Pipeline | Brief → InVideo writes script → Generate → export |

---

## Edit the prompt

Change `invideo_master_prompt.md` — all generate/agent commands pick it up on next run.

Do **not** confuse with `docs/CHANNEL_BOT_BRIEF.md` (that one is for **Cursor agents**, not InVideo).
