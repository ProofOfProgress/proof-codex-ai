# Cloud Agent model cost — owner guide

**Problem:** Cloud Agent runs can burn **Cursor subscription usage** fast if the wrong chat model is selected (e.g. GPT-5.3 Codex, Opus, GPT-5.5). That is **separate** from Kling/Gemini pipeline API bills.

**Pipeline (already cheap on this VM):** `GEMINI_MODEL=gemini-2.5-flash-lite` for QC/scripts · Kling for video. Those are **not** Cursor chat charges.

---

## Two different “Auto” things (don’t mix them up)

| What | Where | Billing |
|------|-------|---------|
| **Cursor IDE “Auto”** | Desktop chat model picker | Generous Auto + Composer pool on Pro |
| **Cloud Agent model** | [cursor.com/agents](https://cursor.com/agents) or Desktop → Cloud | **No Auto** — you pick a model; charged at that model’s API rate |

Cloud Agents always run in **Max Mode**. Long agent runs (terminal, grep, edits) = many tokens.

---

## What to use for handoff (recommended default)

| Job | Model | Why |
|-----|-------|-----|
| **Daily CEO runs** (scout, clips, QC, git, PRs) | **Composer 2.5** or **Composer 2.5 Fast** | Best cost/quality for coding agents |
| Quick questions / docs only | **Ask mode** + Composer | No file edits = fewer tool loops |
| One hard architecture call | Sonnet or Codex **once** | Don’t leave this as default |

**Avoid as default:** GPT-5.5, Opus, GPT-5.3 Codex — often **3–10×** Composer output cost on long runs.

---

## How to change the default (do all three)

### 1. Dashboard default

1. Open [cursor.com/dashboard/cloud-agents](https://cursor.com/dashboard/cloud-agents)
2. **Environments** / default settings
3. Set **Default model** → **Composer 2.5** (or Composer 2.5 Fast)

### 2. Before every new Cloud Agent run (important)

Known issue: dashboard default sometimes **resets** to an expensive model.

1. Start a new Cloud Agent run
2. Open the **model picker** in the task box
3. Confirm it says **Composer 2.5** — not Codex / Opus / GPT-5.5
4. Then send the task

### 3. Watch usage weekly

[cursor.com/dashboard/usage](https://cursor.com/dashboard/usage) — if you see spikes on Codex/Opus, the picker was wrong.

Set **spend limits / alerts** in Cursor billing so handoff doesn’t surprise you.

---

## Subagents (employee team)

All `.cursor/agents/*` use **`model: inherit`** — they use whatever the **parent** Cloud Agent picked. If parent is Composer, employees stay cheap. If parent is Codex, **every** background employee costs more too.

**Rule:** pick Composer on the CEO run before dispatching `/product-research`, `/visual-review`, etc.

---

## API / scheduled automations (later)

If you trigger Cloud Agents via API, pass an explicit cheap model — never `"auto"`:

```json
"model": { "id": "composer-2", "params": [{ "id": "fast", "value": "true" }] }
```

List models: `GET https://api.cursor.com/v1/models` with `CURSOR_API_KEY`.

---

## Local vs Cloud split (optional savings)

| At your desk | Use |
|--------------|-----|
| “What does this file do?” | **Local IDE + Auto** |
| Long pipeline (Kling, pytest, PR, hub SSH) | **Cloud Agent on Composer 2.5** |

---

## Repo secrets (pipeline only — not Cursor chat)

| Secret | Default | Pays for |
|--------|---------|----------|
| `GEMINI_MODEL` | `gemini-2.5-flash-lite` | Module 1 QC vision, scripts |
| `OPENAI_MODEL` | `gpt-4o-mini` (optional fallback) | Only if no Gemini key |

Changing these does **not** change Cloud Agent chat model — that’s only in Cursor dashboard + per-run picker.

---

## Handoff checklist

- [ ] Dashboard default = **Composer 2.5**
- [ ] Verify model picker **every** new Cloud Agent run
- [ ] Spend limit set on Cursor account
- [ ] One mission per run (don’t stack “launch + scout + 3 clips” in one mega-run)
- [ ] Check usage dashboard once a week

Full Cursor docs: [Models & pricing](https://cursor.com/docs/models-and-pricing) · [Cloud Agent settings](https://cursor.com/docs/cloud-agent/settings)
