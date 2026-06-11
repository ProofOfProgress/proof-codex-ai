# Don't Blink — horror lane (locked)

## Primary: **Analog horror**

Found-footage grammar — night-vision CCTV, security-app phone feeds, VHS grain, timestamp glitches, degraded signal at **3:12 AM**. The scare lives in the **lag between reality and the recording**.

## Secondary: **Psychological horror**

Alone-at-night uncanny dread. You rationalize the gap as glitch, lag, or tired eyes — earned tension, not random noise.

## Color rule (non-negotiable)

| Shot type | Palette |
|-----------|---------|
| POV room / hallway (no feed) | Cold blue-black `#1A2A3A`, underexposed |
| Wall-mounted CCTV or in-phone feed rect | Night-vision green grain **only inside that rect** |

Never wash the full frame in green on a POV shot.

## Lanes we do **not** pursue

Creature features, occult rituals, folklore entities, gore slashers, cosmic exposition, daylight crowd horror, cosy aesthetic.

## Code

`shorts_bot/production/horror_lane.py` — injected into scripts, I2V prompts, and Gemini QC context.
