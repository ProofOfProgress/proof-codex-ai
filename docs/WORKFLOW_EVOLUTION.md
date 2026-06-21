# Workflow evolution — north star pillar

The daily loop is not a fixed script. **Steps and parameters evolve** from run outcomes and YouTube analytics — the same idea as [EvoAgentX](https://github.com/EvoAgentX/EvoAgentX) (self-evolving agent workflows), applied to our InVideo → YouTube factory.

## What evolves (no LLM weight training)

| Layer | What changes | Trigger |
|-------|----------------|---------|
| **Step params** | Hook template, render wait time | Hook punish → rotate template; render timeout → +600s wait |
| **Step proposals** | Add Drive-fetch fallback, reorder steps | InVideo credit/paywall failures |
| **Content rules** | `avoid:*`, `repeat:*`, agent memory | Existing self-training (draft + sync) |

We keep the base LLM frozen. Learning = **workflow JSON version bumps** + **training rules** + **episodes**.

## Default workflow

Seed file: `data/workflows/daily_invideo_v1.json`

Steps (in order):

1. `pick_topic` — product rotation  
2. `build_brief` — hook template + Pay/Skip/Wait brief  
3. `save_draft`  
4. `auto_approve`  
5. `invideo_project` — MCP start  
6. `invideo_render` — browser ship/download  
7. `youtube_upload`  

Active version lives in SQLite `channel_state` key `workflow:daily_invideo:active`. Each mutation bumps `version`.

## Inspect

```bash
python3 -m shorts_bot.learning.workflow_cli status
python3 -m shorts_bot.learning.workflow_cli history
python3 -m shorts_bot.learning.workflow_cli json
```

## Config

```env
WORKFLOW_EVOLUTION_ENABLED=true   # default on
SELF_TRAINING_ENABLED=true        # rules + episodes (companion loop)
```

## Loop diagram

```
Daily tick → run enabled steps → record workflow_runs
                    ↓
         evolve_after_daily_run (params + proposals)
                    ↓
YouTube sync → rewards → evolve_from_rewards (hook template)
                    ↓
         reflect_after_sync (rules → agent memory)
                    ↓
         Next tick uses workflow vN+1
```

## Public GitHub references (research)

- **EvoAgentX** — workflow + prompt + topology evolution  
- **EverOS / Memento** — episodic memory (we use `learning_episodes`)  
- **Reflexio** — learn from corrections (maps to draft Yes/No)  

See also `docs/AUTONOMOUS_SELF_TRAINING_RESEARCH.md` and `docs/SELF_LEARNING.md`.

## Not yet autonomous

- No automatic step reorder without improvement approval (except safe numeric params)  
- No A/B workflow variants in parallel  
- Structural steps (e.g. `drive_fetch`) are proposed, not auto-inserted  

Those are the next increment after credits + uploads flow again.
