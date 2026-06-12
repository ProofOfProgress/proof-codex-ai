# Peripheral — how to reach the right audience on YouTube

**Assessed:** 2026-06-12  
**Companion:** `PERIPHERAL_CHANNEL_AUDIENCE_RESEARCH.md` (who we're for)  
**Applied:** `channel/brand/youtube_copy.txt` (live channel description + keywords)

---

## Executive summary

YouTube does **not** read your mind. It matches each Short to viewers using **layered signals** — channel identity, video metadata, **what is spoken**, **what is on screen**, and **who actually watches to the end**.

To reach **late-night horror Shorts scrollers**, every layer must say the same thing:

> *Faceless ~30s scary stories, hook immediately, payoff at the end.*

When title, first spoken line, captions, visuals, channel description, and retention **align**, YouTube expands the seed pool to similar viewers. When they **conflict**, you get random traffic that swipes away — and distribution dies.

---

## Part 1 — How YouTube picks WHO sees a Short

### 1.1 Shorts distribution funnel

```
Publish
  → Seed pool (50–500 viewers, ~70% non-subscribers)
  → Watch-through / retention gate (~65% on short clips)
  → Topic cluster match (horror · scary stories · your sub-niche)
  → Wider push + search/suggested (if cluster is clear)
```

**Implication:** Metadata gets you into the right **cluster**. Retention keeps you there.

### 1.2 Signals YouTube uses (2025–2026 synthesis)

| Layer | Signals | Weight for Shorts |
|-------|---------|-------------------|
| **Content** | Auto-transcript, on-screen text, visual AI | **Highest** — what the video *is* |
| **Behavior** | Watch-through, swipe-away, replays | **Highest** — did strangers finish? |
| **Video metadata** | Title, description line 1, hashtags | **High** — topic + intent |
| **Channel metadata** | Description first 150 chars, keywords | **Medium** — channel-level bucket |
| **Tags** | Backend tags | **Low** — disambiguation only |
| **Thumbnails** | Less critical on Shorts feed | First frame + title matter more |

YouTube **cross-checks**: if title says "security camera" but audio never mentions cam/motion/alone, cluster match weakens.

### 1.3 Topic clusters (thematic authority)

Channels that **rotate randomly** (horror → comedy → vlog) confuse the matcher.

**Peripheral strategy:**

- **One cluster:** faceless horror Shorts / scary stories  
- **Sub-clusters inside:** analog dread, reflection, alone-at-home, jumpscare finale  
- **Rotate pillar**, not genre — same cluster, different hook

---

## Part 2 — Channel-level: tell YouTube what the channel IS

### 2.1 Visible description (before "Show more")

~**125–150 characters** show on channel home + search snippets. This is your **elevator pitch**.

**Live opening (Peripheral):**

> Faceless horror Shorts for late-night scrollers — 30-second scary stories with a payoff at the end.

**Why this line:**

- **Who:** late-night scrollers (psychographic)  
- **What:** faceless horror Shorts (cluster)  
- **Length/promise:** 30s + payoff (retention contract)  
- **Keywords:** horror Shorts, scary stories (search phrases)

### 2.2 Full channel description structure

| Block | Job |
|-------|-----|
| Line 1 | Who + what + promise (visible fold) |
| Line 2–4 | "You're in the right place if…" — qualifies audience |
| Bullets | Format contract (hook, faceless, cadence) |
| Brand | Peripheral · don't blink |
| Trust | AI disclosed, volume warning |
| CTA | Comment story request |

Source of truth: `channel/brand/youtube_copy.txt`

### 2.3 Channel keywords (hidden, indexed)

Set via API in `KEYWORDS:` block — helps channel search + topic association.

Current set: horror shorts, scary stories, faceless horror, analog horror, creepy shorts, jumpscare, peripheral, etc.

**Do not keyword-stuff** video tags; channel keywords are one-time setup.

### 2.4 Visual brand (homepage "nice channel")

| Asset | Signal |
|-------|--------|
| **Name** | Peripheral ✓ |
| **Profile** | Line eye crop |
| **Banner** | Macro eye, white on black, no clutter |
| **Trailer** | Optional later — best 30s Short |
| **Pinned** | Best performer or hook reel |

---

## Part 3 — Video-level: every upload teaches the algorithm

### 3.1 Alignment checklist (mandatory before publish)

| # | Check | Example |
|---|-------|---------|
| 1 | **Title** = hook keyword, spoken in first 3s | "Your security camera flagged motion…" |
| 2 | **Description line 1** repeats topic + Peripheral | Same hook + brand line |
| 3 | **First VO line** matches title energy | No bait title |
| 4 | **Captions burned** — mute-first viewers | Word sync |
| 5 | **Visual beat 1** matches hook | Cam/mirror/knock visible early |
| 6 | **Length** 30–45s | Retention sweet spot |
| 7 | **Hashtags** 3–5, horror-specific | #HorrorShorts #ScaryStories |
| 8 | **Category** Entertainment (24) | Not wrong vertical |
| 9 | **Synthetic** disclosed | YPP trust |
| 10 | **Pillar** logged | Don't repeat same pillar back-to-back |

**Rule:** Say the **topic words** in the first 10 seconds (YouTube transcript signal).

### 3.2 Title rules (Shorts)

- Front-load hook in **first 40 characters** (visible on shelf)  
- Under **60 chars** when possible  
- No QA build suffix on public uploads  
- 🔊 prefix only when finale sting exists  

### 3.3 Description rules (per Short)

**First 100 characters** = same keyword as title + Peripheral:

```
Your security camera flagged motion at 3:12 AM — you live alone.

Peripheral — scary horror Shorts (~30s). Watch the whole thing.
don't blink.
```

Hashtags at end (max 5 shown above title on Shorts).

### 3.4 Spoken + visual alignment

| Hook type | Say early | Show early |
|-----------|-----------|------------|
| Security cam | motion, alone, cam, 3am | CCTV / hallway |
| Mirror | reflection, blink, mirror | mirror POV |
| Knock | knock, closet, alone | door/closet |
| Wrong text | text, delivered, phone | only if story needs it — prefer analog |
| Wrong time | timestamp, photo, clock | alarm clock |

### 3.5 Posting for seed audience

- **When:** Target viewer awake — test **Wed–Fri 3–5pm US Eastern** OR **9–11pm**; pick one for 10 uploads  
- **Cadence:** Max **1 public Short / 24h** (YPP); consistency > bursts  
- **First hour:** Retention in seed window drives wider push — don't edit title immediately after post  

---

## Part 4 — Pipeline: what we codify in the bot

| System | Audience delivery role |
|--------|------------------------|
| `channel/brand/youtube_copy.txt` | Channel description + keywords |
| `upload_meta.py` | Per-video title, desc, tags, hashtags |
| `drafts/generator.py` | Hook line 1, second-person, pillar |
| `captions` / transcript | Mute-readable + transcript signal |
| `scare_pillar.py` | Cluster variety without genre drift |
| `upload_guard` / YPP | No spam uploads that poison cluster |
| `upload_canonical_cli` | One clean public upload per draft |
| `post_upload` / analytics | Learn which hooks retain |

### 4.1 Future hardening (backlog)

- [ ] `audience_alignment_check()` — title vs first caption segment vs hook  
- [ ] Auto-insert pillar keyword in description line 1  
- [ ] Studio Audience tab weekly report → `data/LEARNED.md`  

---

## Part 5 — Common mistakes that send you to the WRONG audience

| Mistake | Result |
|---------|--------|
| Generic title ("Scary story #5") | Clustered with low-intent spam |
| Title ≠ first line | Swipe in 2s, wrong seed |
| Batch QA uploads same hook | YPP + confused matcher |
| No captions | Mute scrollers bounce |
| 60s slow burn | Wrong format for Shorts feed |
| Gore bait title, mild video | Reported / wrong viewers |
| Channel desc empty/vague | Channel search invisible |

---

## Part 6 — Verify it's working

| Week | Check |
|------|-------|
| 1 | Search YouTube: `peripheral horror shorts`, `faceless horror shorts` — do you appear? |
| 2 | Studio → Audience → Demographics vs Jordan persona |
| 3 | Studio → Content → retention at 3s, 20s, end |
| 4 | Comments: "I jumped" / "watched twice" = right audience |

**Fix order when wrong:** retention/hook first → then metadata → then audience hypothesis.

---

## TL;DR

1. **Channel description first line** = who + what + promise (done — live via API).  
2. **Every Short** = title, speech, captions, visuals all agree on one topic.  
3. **Retention** = proof you reached the right people.  
4. **Consistency** = same cluster 10+ uploads so YouTube trusts the match.

Apply brand anytime: `python3 -m shorts_bot.youtube.brand_cli` or operator command `apply brand`.
