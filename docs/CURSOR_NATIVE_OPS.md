# Cursor native ops — run at scale without Git as the engine

Isaac triggers work from **Cursor chat**, **Agents Window**, or [cursor.com/agents](https://cursor.com/agents). The agent runs CLI on the cloud VM. **Commits/PRs are optional** — they sync config to the next VM, not execute posts or Kling jobs.

## Agent team (use this — not legacy one-off subagents)

**Primary doc:** `docs/FOR_OWNER_AGENT_TEAM.md`

| Layer | Path | Isaac uses |
|-------|------|------------|
| **CEO orchestrator** | `.cursor/agents/affiliate-ceo.md` | `/affiliate-ceo` or `/team` |
| **Specialists** | `video-editor`, `video-caption-writer`, `product-video-prompt-builder`, `module1-qc-runner` | Delegated by CEO |
| **Mission log** | `data/agent_ops/missions/` · `python3 -m shorts_bot.agent_ops status` | Watch CEO ↔ employees |

Official docs: [Subagents](https://cursor.com/docs/subagents) · [Cloud Agents](https://cursor.com/docs/cloud-agent)

## Cloud vs GitHub

| GitHub | Cursor agent |
|--------|----------------|
| Stores `.cursor/` config, Python factory, course | **Runs** scout, Kling, QC, Zernio on VM |
| PR merges update what next agent reads | Secrets at **agent launch** — new run after changes |
| Suggestions until merged | Execution in terminal every session |

## Bootstrap each cloud run

1. `docs/CLOUD_AGENT_START.md`
2. `bash scripts/install.sh` + `python3 -m shorts_bot.cloud_secrets`
3. `/affiliate-ceo make a clip for [product]` or natural language

## Higgsfield vs factory

| Path | When |
|------|------|
| `/higgs` plugin + MCP | Hands-on Module 4/5 in chat (OAuth) |
| `factory_cli` + Kling API | Automated scale via CEO + specialists |
