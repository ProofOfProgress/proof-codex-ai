# Proof Codex AI

Utilities and reference material for automating Proof content generation.

## AutoTextGenerator

`src/autotextgenerator.py` builds draft hooks, codex updates, CTAs, pull-request summaries, README snippets, and metric reports. It consumes Codex laws, task logs, viewer metrics, and comment trends.

### Running

Prepare an input JSON file:

```json
{
  "laws": ["Law #1 Hook <3s"],
  "systems": ["Loop Trap"],
  "metrics": {"views": 1000, "likes": 50, "comments": 10},
  "task_logs": "Update hooks\nRefactor CTA",
  "comment_trends": ["push harder"]
}
```

Then execute:

```bash
python3 -m src.autotextgenerator data.json --out drafts
```

The script writes text drafts into the specified output directory for review.

