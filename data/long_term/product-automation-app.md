# Product idea: automation app (course + factory bundle)

**Status:** long-term — prove revenue on our own accounts first.

## One-liner

Operating system for TikTok Shop affiliates: connect accounts, generate compliant clips, QC before upload, schedule posts — paired with Momentum Academy (what actually converts).

## What we have today vs. product

| Layer | Today (operator factory) | Product version |
|--------|------------------------|-----------------|
| Connect | API keys in Cursor Secrets | “Connect TikTok” / “Connect Kling” wizards |
| Create | `factory_cli make-clip`, manual product pick | Product picker + one-tap “make clip” |
| QC | Module 1 gate (`module1_qc.py`) | Red/green checklist before post |
| Post | Zernio or phone ADB queue | “Post now” / daily schedule per account |
| Learn | Course + score API | Built-in SOPs + “why this failed” |

Package the **automation**, not Cursor. Cursor stays our dev superpower; customers get a clean product on the same pipeline.

## Wedge (why it’s not “another AI video tool”)

1. **Course + automation** — course teaches what to post; app does scout → image → Kling → edit → QC → queue.
2. **Module 1 QC as trust feature** — blocks upload on Shop rule violations vs. generic clip generators.
3. **Two tracks** — bubble warmup (carousels) → affiliate (Kling 5s). Most tools only know one lane.

Natural first buyers: **Momentum Academy students** paying for an “automation tier” instead of farm PC + terminal.

## Hard parts (don’t sell too early)

- **Usage costs** — Kling, images, Kalodata; pricing needs credits or usage tiers, not fantasy flat SaaS.
- **Posting reality** — serious affiliates want phones + LTE for Shop; product tiers: “cloud post” (Zernio) vs “send to my phone.”
- **Support** — bans, appeals, CTR coaching = humans + course, not just software.
- **IP split** — ~90% creative stays in course; app automates ops, doesn’t replace the course (bundle positioning).

## Realistic path

1. Prove on **2 bought affiliate accounts** — Shop revenue = proof pipeline works.
2. Dogfood UI — queue view, account cards, QC screen, “make clip” (FastAPI backend in `shorts_bot/web/` is a start).
3. First product = **course upsell** — “Momentum Automation” for students: installer or hosted + their API keys.
4. Scale “sellout” — white-label for other affiliate educators, or SaaS with credits, once support and pricing are boring.

## MVP screens (when we build)

1. Connect accounts (Zernio / OAuth)
2. Pick product (EchoTik / saved list)
3. Preview clip (raw + loop + caption)
4. Module 1 QC (pass/fail + reasons)
5. Post queue (per account, daily cap, privacy)

## Notes from chat (2026-06)

Isaac asked if we could “package you up as an app” with clean integrations and friendly UI as a sellout moment. Answer: yes, aligned with direction — but win is **course + automation bundle** for people already pursuing Shop affiliate income, not a generic App Store launch on day one.
