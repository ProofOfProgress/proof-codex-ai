# Proof Codex AI

This repository contains tools for managing the Proof Codex and automating Proof of Progress content generation and AI advisor functionality.

## Modules

- **codex_task_parser.py**  
  Parses task log files and produces Codex entries such as `[LAW:]` or `[SYSTEM:]` blocks.

- **codex_auto_updater.py**  
  Appends parsed entries to the master Codex document automatically.

- **data_scraper.py**  
  Provides simple web scraping and search API helpers for gathering viewer psychology and Shorts algorithm data.

- **codex_validator.py**  
  Validates entries to ensure they comply with Codex formatting rules.

- **codexadvisor.py**  
  Analyzes channel metrics and comment trends to generate actionable recommendations backed by Codex laws.

  ### Usage

  ```bash
  python codexadvisor.py

Reads metrics from data/metrics.json and comments from data/comments.json.
Recommendations cite lines from Proof_AI_Advisor_Protocol.txt to justify each suggestion.

AutoTextGenerator Utility (src/autotextgenerator.py)
Builds draft hooks, Codex updates, CTAs, pull-request summaries, README snippets, and metric reports. It consumes Codex laws, task logs, viewer metrics, and comment trends.

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

The script writes text drafts into the specified output directory for review.
