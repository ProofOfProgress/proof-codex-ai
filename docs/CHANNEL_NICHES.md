# Channel niche — Peripheral (horror Shorts)

**Peripheral** — faceless horror micro-stories (~30s) with **jumpscare on finale beats** (most uploads). Merch tagline: *don't blink*. Audience research: `data/research/PERIPHERAL_CHANNEL_AUDIENCE_RESEARCH.md`.

## World (The Gap)

- Recordings lag reality by one beat; movement happens when you stop watching
- 3:12 AM = systems glitch (motion alerts, impossible timestamps, dead-contact texts)
- Same liminal apartment grammar every upload — hallway, mirror, phone, security cam
- Bible: `channel/brand/world.md` · code: `shorts_bot/production/world.py`

## Positioning

Another alone-at-night night in The Gap → tension builds → jumpscare at the end. AI full-motion clips (I2V). Not cosy self-help, not creepypasta listicles.

## Scare pillars (rotate)

| Pillar | Example hook |
|--------|----------------|
| Wrong reflection | Mirror blinked one second after you did |
| Wrong place | Security cam flagged motion — you live alone |
| Wrong text | Last text showed delivered — phone was off |
| Wrong sound | Knock came from inside the closet |
| Wrong time | Photo timestamp from next week |

## Production stack

1. **Deep research** — `data/research/LAUNCH_VIDEO_*_SEO_HOOKS.md`
2. **Draft** — second-person horror script (`drafts/generator.py`)
3. **Paid pipeline** — Resemble/edge VO + Gemini transcript + Replicate I2V
4. **Upload** — vision QC ≥ 7.5, 1 Short/day, rotate scare pillar

## Launch calendar (first 4)

1. Mirror blink (live)
2. Security cam motion (draft #3)
3. Closet knock (research prep)
4. Wrong text delivered (playbook)

See `data/PRIORITIES.md` and `data/PRIORITY_14_NOW.md`.
