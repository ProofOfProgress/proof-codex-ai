# AGENTS.md

## Cursor Cloud specific instructions

### Project overview

Proof Codex AI is a **Python 3.10+ CLI toolkit** (no web server, database, or Docker). It provides:

- `codexadvisor.py` — analyzes channel metrics/comments and prints Codex-backed recommendations
- `python3 -m src.autotextgenerator <input.json> --out <dir>` — generates draft text files (hooks, CTAs, PR summaries, etc.)
- `codex/` package — task log parsing, Codex validation, optional web scraping/search

### Services

There are **no long-running services**. End-to-end verification is done by running the CLI entry points against bundled data under `data/`.

### Dependencies

Install with:

```bash
pip install -r requirements.txt
```

Only `requests` and `beautifulsoup4` are required (for `codex/data_scraper.py`). The advisor CLI and autotextgenerator use stdlib only at runtime, but importing `codex` pulls in the scraper dependencies.

### Agent clock

Check the time before scheduling posts, daily autopilot, or time-sensitive replies:

```bash
python3 -m src.clock              # human-readable UTC + owner local (America/Los_Angeles)
python3 -m src.clock --json       # machine-readable
python3 -m src.clock --write      # refresh data/CLOCK.json snapshot
bash scripts/clock.sh --json
```

Override timezones: `OWNER_TIMEZONE=America/Chicago OPS_TIMEZONE=UTC python3 -m src.clock`

### Running the application

**Codex Advisor** (works out of the box with bundled sample data):

```bash
python3 codexadvisor.py
```

**AutoTextGenerator** (requires a JSON input file; see `README.md` for schema):

```bash
python3 -m src.autotextgenerator path/to/input.json --out drafts
```

### Lint / test

This repo has **no configured linter** (no ruff/flake8/mypy) and **no test suite on `main`**. Use these smoke checks:

```bash
python3 -m compileall -q .
python3 -c "from codex import CodexTaskParser, DataScraper; from src.autotextgenerator import AutoTextGenerator"
python3 -m src.clock --json
python3 codexadvisor.py
```

A remote branch (`origin/codex/create-initial-tests-directory-with-pytest-config`) adds a minimal `pytest` setup if tests are needed.

### Optional environment variables

For Google Custom Search via `codex/data_scraper.py`:

- `GOOGLE_API_KEY`
- `GOOGLE_ENGINE_ID`
