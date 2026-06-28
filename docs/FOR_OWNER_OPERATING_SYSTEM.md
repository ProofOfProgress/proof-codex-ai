# Operating system — tips, memory, and cheap QC

Plain English guide for how the bot **learns your rules** and **checks videos before publish** without wasting Cursor credits.

---

## Can the agent add plugins/MCP by itself?

| Thing | Agent can do alone | Needs you |
|-------|-------------------|-----------|
| **Skills** (`.cursor/skills/`) | Yes — commit to repo | Nothing |
| **Operating tips** (`data/operating_tips.json`) | Yes | You review tips |
| **Agent memory** (`memory_cli`, `MEMORY.md`) | Yes | You say what to remember |
| **Pre-publish Python gate** | Yes — blocks upload via repo code | Nothing |
| **Cursor rules** (`.cursor/rules/`) | Yes — always-on agent constraints | Nothing |
| **MCP marketplace plugins** | Add config to repo | **OAuth** in Cursor Desktop + Dashboard Integrations + new agent run |

### Two control planes (read this)

| Plane | Controls | Does **not** control |
|-------|----------|----------------------|
| **Python** (`upload_guard` in Zernio/TikTok upload functions) | Publish through `shorts_bot` upload code | Agent reasoning in chat; raw `curl` to Zernio |
| **Cursor** (`AGENTS.md`, `.cursor/rules/`, skills, tips) | How the agent should behave | A human running curl in a terminal |

MCP does not give “more memory.” **Tips + rules + skills** steer the agent; **upload_guard** blocks bad publishes when upload goes through the repo’s Python paths.

---

## Your 100 tips — how it works

1. **Add tips** to `data/operating_tips.json` (we started with 10 — copy the pattern).

2. **Each tip has:**
   - `id` — e.g. `T042`
   - `title` — short name
   - `content` — what to do
   - `applies_to` — `video`, `carousel`, `affiliate`, or `agent`
   - `enforcement` — `code` (bot blocks upload), `agent` (agent must follow), or `both`

3. **Sync tips into long-term memory** (optional):

```bash
python3 -m shorts_bot.operating.tips_cli sync-memory
```

4. **List tips:**

```bash
python3 -m shorts_bot.operating.tips_cli list
```

5. **Add one tip from terminal:**

```bash
python3 -m shorts_bot.operating.tips_cli add --id T011 --title "..." --content "..." \
  --applies-to carousel agent --enforcement both --code-check caption_bans
```

**Goal:** important rules are **code-blocked**; the rest are in memory/skills so the agent doesn’t “forget” without re-reading 50 pages of chat.

---

## Required pre-publish check (without burning compute)

**Wrong (expensive):** Agent watches video in chat every time.

**Right (cheap):** Python runs before upload:

```bash
# Bubble wrap — fast tier (no Gemini vision, ~seconds)
python3 scripts/pre_publish_gate.py --type carousel --tier fast \
  --slide1 slide1_hook.png --slide2 slide2_cta.png --account bubble_proof

# Affiliate video — standard tier (vision if enabled)
python3 scripts/pre_publish_gate.py --type video --tier standard \
  --video clip.mp4 --caption "..." --product "NAME"
```

**Tiers:**

| Tier | Cost | Checks |
|------|------|--------|
| **fast** | Lowest | Banned words, post spacing, 2-slide format, AIGC config |
| **standard** | Medium | fast + Gemini vision on frames (when enabled) |

**Env knobs:**

| Variable | Default | Meaning |
|----------|---------|---------|
| `PRE_PUBLISH_DEFAULT_TIER` | `standard` | Set to `fast` for daily bubble wrap |
| `PRE_PUBLISH_BLOCKS_UPLOAD` | `true` | Upload fails if gate fails |
| `MODULE1_VISION_QC_ENABLED` | `true` | Set `false` to skip vision everywhere |

Upload code (`post_clip`, `post_bubble_wrap_carousel`) calls the gate automatically.

---

## Agent memory (already in repo)

```bash
python3 -m shorts_bot.memory.memory_cli list
python3 -m shorts_bot.memory.memory_cli add "Always disclose AI" --category operating_rule --pin
python3 -m shorts_bot.memory.memory_cli export
```

Exports to `data/MEMORY.md` (gitignored) for agents to read at start.

---

## Skills added for agents

| Skill | Path |
|-------|------|
| Pre-publish gate | `.cursor/skills/pre-publish-gate/SKILL.md` |
| Owner operating system | `.cursor/skills/owner-operating-system/SKILL.md` |

---

## MCP marketplace (excluding Higgsfield / Slack / GitHub)

Worth considering later for **learning / knowledge**, not posting:

| Plugin | Why |
|--------|-----|
| **Notion** | If course notes live in Notion — agent queries live docs |
| **Linear** | Backlog of owner orders |
| **Playwright MCP** | Browser verify posts on TikTok profile (custom install) |

Still need your OAuth + new agent run for each MCP.

---

## Quick daily workflow

1. Agent generates slides/clips per `BUBBLE_WRAP.md`
2. `python3 scripts/pre_publish_gate.py --tier fast ...` (or batch script with `--confirm`)
3. Zernio upload
4. You add Mackenzie sound in TikTok app
5. New tip from group call → add to `operating_tips.json` → `sync-memory`
