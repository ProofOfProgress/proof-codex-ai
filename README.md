# Proof Codex AI

This repository provides resources for the Proof Codex system. The new
`codexadvisor.py` module analyzes channel metrics and comment trends to
generate actionable recommendations backed by Codex laws.

## Usage

Run the advisor with sample data:

```bash
python codexadvisor.py
```

The script reads metrics from `data/metrics.json` and comments from
`data/comments.json`. Recommendations cite the relevant line from
`Proof_AI_Advisor_Protocol.txt` used to justify each suggestion.
