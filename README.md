This repository provides resources for automating Proof of Progress content generation and AI advisor functionality.

## codexadvisor.py Module

The `codexadvisor.py` module analyzes channel metrics and comment trends to generate actionable recommendations backed by Codex laws.

### Usage

```bash
python codexadvisor.py

Reads metrics from data/metrics.json and comments from data/comments.json. Recommendations cite lines from Proof_AI_Advisor_Protocol.txt to justify each suggestion.

AutoTextGenerator Utility
src/autotextgenerator.py builds draft hooks, codex updates, CTAs, pull-request summaries, README snippets, and metric reports. It consumes Codex laws, task logs, viewer metrics, and comment trends.

Running
Prepare an input JSON file:

{
  "laws": ["Law #1 Hook <3s"],
  "systems": ["Loop Trap"],
  "metrics": {"views": 1000, "likes": 50, "comments": 10},
  "task_logs": "Update hooks\nRefactor CTA",
  "comment_trends": ["push harder"]
}

Then execute:

python3 -m src.autotextgenerator data.json --out drafts
