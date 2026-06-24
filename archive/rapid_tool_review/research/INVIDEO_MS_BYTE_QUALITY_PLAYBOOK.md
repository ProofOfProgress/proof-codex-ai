# InVideo + Ms. Byte — Quality Playbook (2026-06)

**Channel:** Rapid Tool Review · **@RapidToolReview**  
**Host:** **Ms. Byte** (always full name — never shorten to “Byte”)  
**Codex law:** Jenny Hoyos rules in `course/files/` (02 hook, 05 mute, 06 retention, 09 CTA)  
**Goal:** Blow up the channel with **trustworthy, bingeable ~30s Shorts** — one real AI product per video, strengths + weaknesses, viewer decides.

---

## Executive summary

InVideo is our **production soul** — not a side tool. We send **creative briefs** (not finished films); InVideo writes script, picks stock, captions, and renders. Quality comes from **three layers aligned**:

1. **Jenny structure** — curiosity hook first, 8 beats, CTA before payoff, mute-readable overlays  
2. **Ms. Byte brand** — bubbly AI teacher, **45–55% on-screen** (library character `RTR_MsByte`), not a 5-second cameo  
3. **InVideo mechanics** — MCP `generate-video-from-script`, Basic tier ≤10 credits, vertical-native stock, no AI Twin

**Do NOT use:** Pay/Skip/Wait stamps, AI Twin (20 credits/min), horizontal stock letterboxed into 9:16, horror/jumpscare framing (retired niche).

---

## InVideo API / MCP — how we actually call it

### Endpoint

| Item | Value |
|------|-------|
| MCP URL | `https://mcp.invideo.io/mcp` |
| Auth | `Authorization: Bearer <INVIDEO_API_KEY>` |
| Protocol | MCP JSON-RPC over HTTP + SSE |
| Primary tool | `generate-video-from-script` |

### Tool arguments (official)

```json
{
  "script": "<creative brief OR full VO script>",
  "topic": "Grok (xAI) — $30/month live Twitter data breakdown",
  "vibe": "upbeat, skeptical-but-fair, teacher energy",
  "targetAudience": "AI-curious adults considering paid AI tools",
  "platform": "YouTube Shorts"
}
```

**Important:** The `script` field accepts either a finished voiceover **or** our structured brief. InVideo expands briefs into scenes. We always prepend `invideo_master_prompt.md` via `wrap_invideo_prompt()`.

### What MCP does NOT do

- No direct MP4 download URL in the API response — returns a **project URL**
- No credit quote in MCP response — use browser quote flow or `quote_cli`
- Render + export = Playwright browser automation (`ship_cli`, `download.py`) with owner session

### Code paths (use the right one)

| Command | Brief builder | When |
|---------|---------------|------|
| `python3 -m shorts_bot.invideo.autonomous_ship_cli --draft-id N` | `ms_byte_brief()` | **Best path** — full ship |
| `python3 -m shorts_bot.invideo.generate` / daily workflow | `ms_byte_brief()` (after this PR) | Automated daily |
| Manual Agent One paste | `invideo_master_prompt.md` + `--- VIDEO BRIEF ---` | Owner hand-tweak |

### Connectivity check

```bash
python3 -c "from shorts_bot.invideo.mcp_client import probe_mcp; print(probe_mcp())"
python3 -m shorts_bot.invideo.auth_cli status
```

---

## Credit guard (Basic tier only)

| Rule | Why |
|------|-----|
| Target **≤8–10 credits** per Short | Basic/stock tier; owner budget |
| **NO AI Twin** | ~20 credits/min — burns budget, wrong presenter |
| Stock + UI B-roll majority | Cheaper, faster, looks pro when vertical-native |
| `RTR_MsByte` library character | Reuse — no regenerate host every video |

`shorts_bot/invideo/credit_guard.py` enforces max credits on ship path. Always pick **Basic / licensed stock** in Agent One before Generate.

---

## Prompt architecture (what InVideo receives)

Every MCP call sends:

```
[invideo_master_prompt.md — channel identity, visual law, Jenny beats]
--- VIDEO BRIEF ---
[ms_byte_brief() — product, hook, strength/weakness hints, VO skeleton]
```

### Front-load (InVideo prioritizes prompt start)

1. **Format:** 9:16 vertical, 25–35s, YouTube Shorts ONLY  
2. **Host:** Ms. Byte — `RTR_MsByte`, anime/cel-shaded, clearly synthetic  
3. **Structure:** Jenny 8 beats — hook → setup → strength → but → tradeoff → CTA → payoff  
4. **Negative constraints:** NO twin, NO Pay/Skip/Wait, NO horizontal letterbox, NO horror  

### Per-video brief must include

- **Product name** in first 2 seconds (visual + VO)
- **Curiosity hook** before host intro (Jenny 02 — not “class is in session” first)
- **One strength + one weakness** — feature-level, not marketing copy
- **Optional tradeoff** vs one named competitor
- **Exact VO lines** when we have a Jenny-compliant script (e.g. Grok draft 10)
- **Overlay text** for mute viewers (Jenny 05)
- **TTS lexicon** — see below

---

## Ms. Byte “rich” — what that means on screen

**Old mistake:** Ms. Byte as ~5s cameo while stock carries everything → feels like a generic stock channel.

**Target mix:**

| Layer | Share | Content |
|-------|-------|---------|
| **Ms. Byte (`RTR_MsByte`)** | **45–55%** | Hook wave, strength thumbs-up, weakness reaction, tradeoff shrug, outro |
| **Stock + product UI** | **45–55%** | Vertical-native B-roll, pricing screenshots, app UI, comparison splits |

**Cut pattern:** Alternate every 2–4s — stock/UI explains the feature, Ms. Byte delivers the lesson beat. **8 beats total**, fast cuts, bold captions.

**Poses (library):** hook wave · strength · weakness · tradeoff · outro — see `channel/brand/assets/ms_byte/`

**Character CLI (one-time setup):**

```bash
python3 -m shorts_bot.invideo.ms_byte_character_cli
```

Library name: **`RTR_MsByte`**. Style: anime/cel-shaded — NOT photoreal, NOT AI twin face clone.

---

## Jenny 8-beat template (Ms. Byte format)

| Beat | Time | Content |
|------|------|---------|
| **1 HOOK** | 0–2s | Shock/curiosity FIRST — price, claim, tension. **Not** classroom warm-up first |
| **2 SETUP** | 2–5s | *Then* “I'm Ms. Byte — an AI…” + product name + payoff promise |
| **3 STRENGTH** | 5–8s | One specific win — **what the tool does well** (feature fact) |
| **4 SO** | 8–11s | Deepen the feature — how/why it works (**NOT** who should buy) |
| **5 BUT** | 11–14s | Price, limit, or flaw |
| **6 CONFLICT** | 14–17s | **So** — what that weakness costs (limits, lock-in, missing feature) |
| **7 CTA** | 17–19s | Comment/subscribe card **before** final reveal (Jenny 09) |
| **7–8 TRADEOFF + PAYOFF** | 17–27s | vs competitor on one axis → **best line last** |
| **OUT** | 27–30s | “You decide — comment below.” End within 2s of payoff |

**Cause-and-effect chain:** claim → strength → *so* → *but* → *so* → tradeoff → payoff → CTA → cut.

---

## Voice (locked 2026-06)

**Light British English (RP-lite)** — female, young adult, bubbly synthetic AI teacher. NOT American default, NOT cockney. Fast clear Shorts pacing. InVideo + ElevenLabs prompts: `docs/FOR_OWNER_MS_BYTE_VOICE.md`

---

## TTS lexicon (critical)

AI voice engines misread certain tokens. **Rules for all scripts and briefs:**

| Avoid (spoken) | Use instead |
|----------------|-------------|
| **“X”** as a standalone word (Twitter rebrand) | **“Twitter”**, “the social app”, “Elon’s platform”, “trending posts” |
| “X person or not” | **“Twitter person or not”** |
| “live X posts” | **“live Twitter posts”** |
| “trends on X” | **“trends on Twitter”** |
| “If X isn't your job” | **“If Twitter isn't your job”** |

**Overlays may abbreviate** (e.g. `LIVE TWITTER`) — VO must never say the letter “X” as a word.

Other TTS tips:
- Spell out prices: “thirty a month” not “$30/mo” in VO
- Say **Ms. Byte** (two words) — never “MsByte” or “Byte” alone
- Avoid slash chains: “ChatGPT Plus at twenty vs Grok at thirty”

---

## Visual rules (v1 failures we never repeat)

| Failure | Fix |
|---------|-----|
| Widescreen stock cropped into 9:16 | Vertical-native stock OR tight center crop only |
| Long talking-head blocks | Ms. Byte chest-up, 2–4s per beat, cut away to UI |
| Slow Ken Burns on static images | Max 5–6 visual beats, hard cuts |
| Captions under YouTube UI | Bold bottom third, Shorts safe zone |
| Generic stock (handshakes, skyscrapers) | Tech-specific: phones, laptops, typing, pricing pages |

**Mute test (Jenny 05):** A viewer with sound off should follow the story from **text overlays + UI screenshots alone**.

---

## End-to-end pipeline (owner + agent)

```
1. Research product → data/research/<product>.md
2. Write Jenny script → channel/brand/scripts/<product>_draft_N.md
3. script_qc (Ms. Byte rubric) — must pass before credits burn
4. autonomous_ship_cli OR generate_from_prompt
   → MCP creates InVideo project
5. ship_cli — browser Generate (Basic) → download MP4
6. Local QC (vision + ffmpeg)
7. upload_canonical_cli → YouTube public
8. Analytics sync → learning rules
```

### Grok example (draft 10)

```bash
python3 -m shorts_bot.invideo.autonomous_ship_cli --draft-id 10
```

Script: `channel/brand/scripts/grok_xai_draft_10.md`  
Meta: `data/draft_meta/draft_10_grok.json`

---

## InVideo Agent One — manual refinement

When MCP output needs a human pass:

1. Open project URL in browser (logged into InVideo)
2. **Agent mode** — scene-by-scene, not blind Autopilot
3. Fix stock crops → swap for vertical-native
4. Increase Ms. Byte screen time if cameo-only
5. Verify captions sync + overlay text matches VO
6. Select **Basic** tier → Generate → Export MP4

**Follow-up prompts (iterate in Agent chat):**

- “Replace horizontal stock with vertical tech B-roll”
- “More Ms. Byte on hook and weakness beats — use RTR_MsByte library”
- “Bold STRENGTH / WEAKNESS cards on screen during those beats”
- “Move comment CTA card to 17–19s before payoff line”
- “Remove any Pay Skip Wait stamp graphics”

---

## Growth checklist (blow up the channel)

| Lever | Action |
|-------|--------|
| **Hook** | First line = price shock or contrarian claim — not host intro |
| **Retention** | but/so chain every video; payoff = sharpest line |
| **Mute** | Every beat has readable overlay |
| **Comments** | Specific prompt: “Twitter person or not?” not “what do you think?” |
| **Consistency** | Same host look (`RTR_MsByte`), same beat structure, different products |
| **Uniqueness** | Pull facts from **the product** — pricing, limits, UI — not generic AI hype |
| **Cadence** | 1 Short / 24h max (YPP-safe); quality > volume |
| **Cross-post** | TikTok + Facebook via Zernio after YouTube canonical |

---

## Common mistakes (prompt drift audit — fixed 2026-06)

| Drift source | Was | Now |
|--------------|-----|-----|
| `invideo_master_prompt.md` | AI Twin + Pay/Skip/Wait | Ms. Byte + Jenny 8-beat + strength/weakness |
| `prompts.py` / daily workflow | `shorts_product_brief()` | `ms_byte_brief()` |
| `script_qc.py` | Required Pay/Skip/Wait | Requires strength/weakness + Jenny hook |
| `ms_byte.md` | “~5s on screen” | 45–55% Ms. Byte + stock/UI |
| Research CLI | Horror/jumpscare framing | Ignore — use this playbook + product research |

---

## Reference files

| File | Purpose |
|------|---------|
| `shorts_bot/invideo/invideo_master_prompt.md` | Channel system context for InVideo |
| `shorts_bot/invideo/ms_byte.py` | `ms_byte_brief()` template |
| `shorts_bot/invideo/mcp_client.py` | MCP client |
| `shorts_bot/invideo/autonomous_ship_cli.py` | One-shot ship |
| `channel/brand/ms_byte.md` | Host spec |
| `course/files/02_idea_hook_viral.md` | Hook law |
| `course/files/06_story_retention_payoff.md` | Retention law |
| `docs/FOR_OWNER_INVIDEO_SETUP.md` | Owner setup steps |
| `docs/INVIDEO_AI_PROMPT.md` | Quick reference |

---

## Quick commands

```bash
# Ms. Byte character in library
python3 -m shorts_bot.invideo.ms_byte_character_cli

# Full autonomous ship (best path)
python3 -m shorts_bot.invideo.autonomous_ship_cli --draft-id 10

# MCP probe
python3 -c "from shorts_bot.invideo.mcp_client import probe_mcp; print(probe_mcp())"

# Codex hook search
python3 -m shorts_bot.codex search "hook retention Short CTA payoff"
```

---

*Last updated: 2026-06-13 — aligned with Rapid Tool Review / Ms. Byte / Jenny Codex.*
