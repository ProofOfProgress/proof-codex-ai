# Cursor native ops — run at scale without Git as the engine

Isaac triggers work from **Cursor chat**, **Agents Window**, or [cursor.com/agents](https://cursor.com/agents). The agent runs CLI on the cloud VM. **Commits/PRs are optional** — they sync config to the next VM, not execute posts or Kling jobs.

## Four layers (use all four)

| Layer | Path | Isaac uses |
|-------|------|------------|
| **Rules** | `.cursor/rules/*.mdc`, `AGENTS.md` | Auto — always on |
| **Skills** | `.cursor/skills/*/SKILL.md` | `/affiliate-make-clip` or agent picks |
| **Commands** | `.cursor/commands/*.md` | `/scout-products`, `/make-clip` |
| **Subagents** | `.cursor/agents/*.md` | `/echotik-researcher`, `/video-pipeline` |

Official docs: [Subagents](https://cursor.com/docs/subagents) · [Skills](https://cursor.com/docs/skills) · [Rules](https://cursor.com/docs/rules) · [Cloud Agents](https://cursor.com/docs/cloud-agent)

## Subagents for scale (required minimum)

| Subagent | File | Job |
|----------|------|-----|
| Product research | `.cursor/agents/echotik-researcher.md` | EchoTik scout, plain-English top 3 |
| Video development | `.cursor/agents/video-pipeline.md` | Kling → caption → QC (background) |

Invoke: `/echotik-researcher scout middle core` or `/video-pipeline make clip for [product]`

Cloud handoff: `/in-cloud` runs next task on cloud VM without tying up local chat.

## Cloud vs GitHub

| GitHub | Cursor agent |
|--------|----------------|
| Stores `.cursor/` config, Python factory, course | **Runs** scout, Kling, QC, Zernio on VM |
| PR merges update what next agent reads | Secrets at **agent launch** — new run after changes |
| Suggestions until merged | Execution in terminal every session |

## Bootstrap each cloud run

1. `docs/CLOUD_AGENT_START.md`
2. `bash scripts/install.sh` + `python3 -m shorts_bot.cloud_secrets`
3. Natural language or `/scout-products` / `/make-clip`

## Higgsfield vs factory

| Path | When |
|------|------|
| `/higgs` plugin + MCP | Hands-on Module 4/5 in chat (OAuth) |
| `factory_cli` + Kling API | Automated scale (`affiliate-make-clip` skill) |

Both are valid; skill/subagents default to **factory CLI**.
