# Ms. Byte voice — light British (locked)

**Accent:** Light British English (RP-lite) — smart AI tutor, **not** cockney, **not** thick regional.  
**Why:** Memorable vs generic American explainer voices; still clear for product names and prices.

---

## InVideo (main path — use this)

When generating a Short in **Agent One**, set or prompt the narrator:

```
Voice: British English, female, young adult, upbeat and bubbly.
Light RP accent — clear, synthetic AI teacher, fast pacing for 30-second Shorts.
NOT American. NOT cockney. Crisp on tech product names.
```

If InVideo shows a voice picker: choose a **UK / British female** voice that sounds perky, not news-anchor stiff.

---

## ElevenLabs Voice Design (if you want a owned voice)

1. Go to https://elevenlabs.io → **Voices → Add voice → Voice Design**
2. Paste this prompt:

```
Native British English (light RP, not cockney). Female, young adult (22–28). Clean studio quality.
Persona: bubbly synthetic AI teacher host. Emotion: upbeat, warm, playful, confident.
Bright medium-high pitch. Fast but clear pacing for 30-second YouTube Shorts.
Slightly synthetic/digital undertone — clearly an AI voice, not pretending to be human.
Crisp pronunciation on tech product names: ChatGPT, Claude, Grok, Gemini.
```

3. Preview with:

```
Grok costs thirty a month — and it's built around live Twitter data.
I'm Ms. Byte — an AI — here's the one thing Grok actually does better.
But SuperGrok is thirty a month. ChatGPT Plus? Twenty.
Which tool next? You decide.
```

4. Save your favorite → copy **Voice ID** (tell the agent to wire `ELEVENLABS_VOICE_ID` when ready)

**TTS rule:** Say **Twitter** — never speak **"X"** as a word.

---

## Free fallback (bot only)

If Resemble is down, the bot uses **Microsoft edge-tts** with:

- Voice: `en-GB-SoniaNeural` (British female)
- Slightly faster rate for Shorts pacing

Set in Cursor secrets: `TTS_VOICE=en-GB-SoniaNeural`, `ALLOW_FREE_TTS_FALLBACK=true`

---

## Spec

Full host spec: `channel/brand/ms_byte.md`  
InVideo briefs auto-include voice rules via `shorts_bot/invideo/ms_byte.py`
