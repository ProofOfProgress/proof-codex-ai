from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class CodexData:
    """Container for Codex laws, systems and rules."""

    laws: List[str]
    systems: List[str]


@dataclass
class Metrics:
    """Simplified metrics used for text generation."""

    views: int
    likes: int
    comments: int


class AutoTextGenerator:
    """Generate various text snippets based on Codex inputs."""

    def __init__(self, task_parser: Any, validator: Any) -> None:
        self.task_parser = task_parser
        self.validator = validator

    def generate_hook(self, codex: CodexData, metrics: Metrics, comments: List[str]) -> str:
        """Return a simple hook line referencing the first Codex law."""
        law = codex.laws[0] if codex.laws else "Law #1"
        trend = comments[0] if comments else "viewer demands"
        hook = f"{law}: Turn '{trend}' into proof with {metrics.views} views of momentum!"
        return self.validator.validate_hook(hook)

    def generate_codex_update(self, codex: CodexData) -> str:
        """Return a short codex update referencing available laws and systems."""
        laws = ", ".join(codex.laws[:3])
        systems = ", ".join(codex.systems[:3])
        update = f"Codex Laws in play: {laws}. Systems engaged: {systems}."
        return self.validator.validate_update(update)

    def generate_cta(self, comments: List[str]) -> str:
        """Return a call to action echoing common viewer comments."""
        ref = comments[0] if comments else "join the challenge"
        cta = f"Prove it. Drop a comment if you're ready to {ref}."""
        return self.validator.validate_cta(cta)

    def generate_pr_summary(self, tasks: List[str]) -> str:
        """Return a pull request summary based on parsed tasks."""
        summary = "\n".join(f"- {t}" for t in tasks)
        pr = f"### Proof Codex Updates\n{summary}"
        return self.validator.validate_pr(pr)

    def generate_readme_update(self, codex: CodexData) -> str:
        """Create a short README addition referencing laws."""
        law_ref = codex.laws[0] if codex.laws else "the Codex"
        text = f"This project follows {law_ref} to automate Proof content pipelines."
        return self.validator.validate_readme(text)

    def generate_report(self, metrics: Metrics) -> str:
        """Generate a text report from metrics."""
        return f"Views: {metrics.views}, Likes: {metrics.likes}, Comments: {metrics.comments}"

    def generate_all(
        self,
        codex: CodexData,
        logs: str,
        metrics: Metrics,
        comments: List[str],
    ) -> Dict[str, str]:
        tasks = self.task_parser.parse(logs)
        return {
            "hook.txt": self.generate_hook(codex, metrics, comments),
            "codex_update.txt": self.generate_codex_update(codex),
            "cta.txt": self.generate_cta(comments),
            "pr_summary.txt": self.generate_pr_summary(tasks),
            "readme_update.txt": self.generate_readme_update(codex),
            "report.txt": self.generate_report(metrics),
        }


class SimpleValidator:
    """Fallback validator used if no custom validator is supplied."""

    def validate_hook(self, text: str) -> str:
        return text

    def validate_update(self, text: str) -> str:
        return text

    def validate_cta(self, text: str) -> str:
        return text

    def validate_pr(self, text: str) -> str:
        return text

    def validate_readme(self, text: str) -> str:
        return text


def main(argv: List[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Generate Codex text snippets")
    parser.add_argument("data", type=Path, help="Path to input JSON file")
    parser.add_argument("--out", type=Path, default=Path("drafts"), help="Output directory")
    args = parser.parse_args(argv)

    with args.data.open() as fh:
        payload = json.load(fh)

    codex = CodexData(laws=payload.get("laws", []), systems=payload.get("systems", []))
    metrics = Metrics(**payload.get("metrics", {"views": 0, "likes": 0, "comments": 0}))
    logs = payload.get("task_logs", "")
    comments = payload.get("comment_trends", [])

    generator = AutoTextGenerator(task_parser=payload.get("parser", SimpleParser()), validator=SimpleValidator())
    texts = generator.generate_all(codex, logs, metrics, comments)

    args.out.mkdir(parents=True, exist_ok=True)
    for name, content in texts.items():
        (args.out / name).write_text(content)
        print(f"Wrote {name}")


class SimpleParser:
    """Default parser used when no external parser is available."""

    def parse(self, logs: str) -> List[str]:
        return [line.strip() for line in logs.splitlines() if line.strip()]


if __name__ == "__main__":
    main()
