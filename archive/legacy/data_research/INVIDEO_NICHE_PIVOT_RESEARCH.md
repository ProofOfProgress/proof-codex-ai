# InVideo pivot + niche research (2026-06)

**Owner goal:** Prompt → ~95% finished MP4 → QC → upload. Stop homemade pipeline breakage.

**Channel:** Same YouTube channel — **AI/tech rebrand**. Peripheral horror **retired**.

**Strategy doc:** `data/research/CHANNEL_NICHE_STRATEGY.md`  
**Purge plan:** `docs/PURGE_MANIFEST.md`

---

## InVideo AI — production target

| Feature | For us |
|---------|--------|
| AI Twins | Same presenter every video |
| Voice clone | Narrate any script |
| API / MCP | Agent: script → generate → poll → download |

**Gate:** Owner validates twin manually, says **"invideo pass"**, then agent wires API.

---

## Architecture (target)

```
Topic/script (Gemini + slim memory)
    → InVideo API (twin + stock + captions)
    → QC
    → YouTube upload
    → analytics → learning rules
```

**Turn OFF daily path:** Recraft, Replicate I2V, TurboScribe, ffmpeg beat-sync, Blender.

**Keep:** YouTube upload, analytics, draft scripts, QC gate, agent memory, Codex search.

---

## Agent niche pick

**AI / Tech → AI tools for normal people → "I tested it so you don't have to"**

See strategy doc for alternatives (Myths Busted, Workflow Lab).
