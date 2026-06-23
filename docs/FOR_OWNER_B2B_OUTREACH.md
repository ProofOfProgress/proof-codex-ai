# B2B outreach — plain English

**What we sell:** 30-second honest AI tool Shorts (Ms. Byte host). Pilot for startups.

**Who sends messages:** **You** (Kim / your real Twitter or email). Not a bot account. Not Ms. Byte in DMs.

---

## How we keep messages from sounding AI

The bot **drafts**. You **send**. That alone fixes 80% of it.

### 1. Send as a real person
- Your Twitter / LinkedIn / email
- Your profile photo
- First name sign-off (`Kim` not `Best regards, The Rapid Tool Review Team`)

### 2. One specific detail per message
Bad: *"Love what you're building!"*  
Good: *"Saw your $29/mo tier added last week on the pricing page."*

The bot asks for `--detail` — paste something you actually noticed.

### 3. Short and casual
- **DM:** ~3–5 sentences, one question at the end
- **Email:** ~6–8 lines max, no bullet lists

### 4. Banned “AI smell” phrases
We auto-reject drafts containing things like:
- "I hope this finds you well"
- "I'm reaching out because"
- "synergy", "leverage", "excited to connect"
- Em dashes and corporate blocks

### 5. You tweak before send
Change one word, add a typo fix, swap "Hey" → "Hi" — human fingerprint.

### 6. If they ask “did AI write this?”
**Don't lie.** Say: *"I draft fast with tools, but I read every message before it goes out."*  
The **video** host is openly AI (Ms. Byte). The **sales** conversation is you.

---

## Commands

**Draft a Twitter DM:**
```bash
python3 -m shorts_bot.b2b.outreach_cli draft \
  --company "SomeStartup" \
  --product "SomeTool" \
  --detail "your launch thread on Tuesday about the API" \
  --channel dm
```

**Draft an email:**
```bash
python3 -m shorts_bot.b2b.outreach_cli draft \
  --company "SomeStartup" \
  --product "SomeTool" \
  --detail "Product Hunt #3 yesterday" \
  --channel email \
  --sender "Kim"
```

**Save to prospect list:**
```bash
python3 -m shorts_bot.b2b.outreach_cli save \
  --company "SomeStartup" \
  --product "SomeTool" \
  --detail "..." \
  --contact "@founderhandle"
```

List lives at `data/b2b/prospects.json`.

---

## Daily habit (10 min)

1. Bot researches 5 new AI tools (or you pick from Product Hunt)
2. Bot drafts 5 DMs with `--detail` filled in
3. You read each, tweak one line, paste-send from **your** account
4. Mark replies in the JSON (`status: replied`)

**Goal:** 5 outbound/day → 1–2 replies/week → 1 pilot/month.

---

## Sample offer (pilot)

*"One 30s vertical Short — script + Ms. Byte host + captions — you approve before publish. Pilot $250–400. Sample: [Grok Short link]."*

Adjust price when you're ready.
