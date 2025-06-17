# Proof Codex AI

This repository contains tools for managing the Proof Codex and related automation scripts.

## Modules

- `codex_task_parser.py` parses task log files and produces Codex entries such as `[LAW:]` or `[SYSTEM:]` blocks.
- `codex_auto_updater.py` appends parsed entries to the master Codex document automatically.
- `data_scraper.py` provides simple web scraping and search API helpers for gathering viewer psychology and Shorts algorithm information.
- `codex_validator.py` validates entries to ensure they comply with basic Codex formatting rules.

These utilities are meant to assist the Codex AI workflow.
