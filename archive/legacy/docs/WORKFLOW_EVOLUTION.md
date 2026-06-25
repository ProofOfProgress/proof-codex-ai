# Workflow evolution — public learning stack

The daily loop uses **public systems** for memory and evolution (not freestyle if/else).

## Installed stack

| System | Package | Role |
|--------|---------|------|
| **Mem0** | `mem0ai` | Long-term semantic memory — hooks, workflow failures, rewards |
| **TextGrad** | `textgrad` | Prompt/hook template optimization (same engine EvoAgentX uses) |
| **LiteLLM** | `litellm` | Routes TextGrad to Gemini/OpenAI |

Optional full framework: `pip install -r requirements-learning.txt` includes notes for EvoAgentX (heavy — torch). We use **TextGrad directly** instead of pulling the full EvoAgentX dependency tree into daily ops.

## What was removed (Phase 2 purge)

Homemade render and Peripheral horror production code:

- Blender, Kling, Recraft, Replicate I2V, `render_video.py`
- Horror lane, world lore, jumpscare clip pipeline
- TurboScribe-first render path

**Kept:** InVideo (`shorts_bot/invideo/`), YouTube upload, `RewardEngine`, `workflow_runner`, SQLite drafts/uploads.

## Config

```env
MEM0_ENABLED=true
TEXTGRAD_EVOLUTION_ENABLED=true
WORKFLOW_EVOLUTION_ENABLED=true
PIPELINE_BACKEND=invideo
```

Mem0 stores vectors under `data/mem0/` (local Qdrant). Uses Gemini when `GEMINI_API_KEY` is set.

## Flow

```
Daily run → workflow_runner → record run
         → Mem0 remembers failures
         → TextGrad evolves hook on analytics punish (fallback: rotate pool)

Analytics sync → RewardEngine → TextGrad + Mem0 + training rules
Draft context ← Mem0 recall + SQLite rules
```

## Inspect

```bash
python3 -m shorts_bot.learning.workflow_cli status
python3 -m shorts_bot.memory.memory_cli list
```

## Legacy pipeline

Calling homemade render raises `LegacyPipelineRetired`. Use:

```bash
python3 -m shorts_bot.production.invideo_daily_cli
python3 -m shorts_bot.production.upload_canonical_cli --draft-id N --video ...
```
