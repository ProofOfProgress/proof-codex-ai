# Cursor rules — for the owner

**What this is:** Instructions Cursor’s AI reads automatically so every agent chat follows your business rules — launch timing, FastMoss, QC gates, plain English with you.

Official Cursor docs: https://cursor.com/docs/rules

---

## Where rules live

| Location | What |
|----------|------|
| `.cursor/rules/*.mdc` | **Project rules** — in git, shared with every cloud agent |
| `AGENTS.md` | Short map — agents read this first |
| Your **User Rules** in Cursor settings | Personal style (optional) |

Rules are **not** secrets. They’re policy — safe to commit.

---

## How they turn on

Each rule file has a **type** (set in Cursor **Customize → Rules** or in the file frontmatter):

| Type | When it applies |
|------|-----------------|
| **Always Apply** | Every chat — your core business context |
| **Apply Intelligently** | When the task matches (e.g. “pick products”, “launch budget”) |
| **Apply to Specific Files** | When editing matching paths (e.g. QC code, course files) |
| **Apply Manually** | When you `@`-mention the rule in chat |

You don’t need to memorize this — agents pick them up. To force one: type `@module1-qc-gate` (or the rule name) in chat.

---

## Your rule catalog (2026)

### Always on

| Rule | Purpose |
|------|---------|
| `00-core-always` | North star, dead lanes, CEO model, FastMoss, launch gates |
| `system-dissection` | Fix bugs via full pipeline dissection — never one-off clip patches |

### Launch & money

| Rule | Purpose |
|------|---------|
| `launch-ops` | LAUNCH_TODO order, midnight post, $1k week-1 bonus |
| `budget-runway` | $2,283 cash, FastMoss ~$59, 2-month runway |
| `owner-communication` | Plain English, one next step, status format |

### Affiliate pipeline

| Rule | Purpose |
|------|---------|
| `affiliate-pipeline-flow` | Scout → Kling → edit → QC → post |
| `ceo-orchestration` | Mission logs, employee roster, parallel work |
| `fastmoss-research` | FastMoss only — no EchoTik/Kalodata |
| `module1-qc-gate` | Zero violations before upload |
| `module5-6-creative` | Prompt builder, pan loop, captions |

### Code & ops

| Rule | Purpose |
|------|---------|
| `tiktok-shop-factory` | When editing `shorts_bot/tiktok_shop/` |
| `cloud-agent-bootstrap` | New VM: install, secrets, long jobs |
| `secrets-security` | Never paste keys in chat |
| `course-creative` | When editing `data/research/course/` |

### Parallel track

| Rule | Purpose |
|------|---------|
| `bubble-wrap-parallel` | 4 phones, Mackenzie slideshows — doesn’t block affiliate |

---

## When to add a new rule

Add one when agents **keep making the same mistake** — not for every idea.

Good examples for you later:

- Week-1 commission tracking format  
- Zernio account wiring checklist  
- Appeal workflow after a violation (Module 8)

Bad: copying the whole course into a rule (point to `data/research/course/` instead).

---

## How to create or change a rule

**In chat:** Ask the cloud agent — *“Add a Cursor rule that …”* — or use `/create-rule` if available.

**In Cursor app:** **Customize → Rules → Add Rule** → saves a new `.mdc` file.

**After changes:** Commit to git so every future agent run gets them.

---

## Team rules (optional later)

On Cursor **Team / Enterprise**, admins can add **Team Rules** in the dashboard that apply to all repos. Your project rules in git already cover this repo; Team Rules help if you add more repos later.

---

## Quick test

Start a new agent chat and ask:

> *What research tool do we use and what blocks launch?*

You should get: **FastMoss**, affiliate account, Module 1 QC — not EchoTik or “buy phones first.”

If not, check **Customize → Rules** that project rules are enabled.
