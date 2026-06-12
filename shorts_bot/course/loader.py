from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CourseFile:
    number: str
    title: str
    path: Path
    content: str
    anchors: list[str]


class CourseKnowledgeBase:
    """Loads **Codex** strategist files (Jenny Hoyos course 01–09) plus verbatim supplements."""

    FILE_PATTERN = re.compile(r"^(\d{2})_.*\.md$")

    def __init__(self, course_dir: Path | None = None) -> None:
        root = course_dir or Path(__file__).resolve().parents[2] / "course"
        self.root = root
        self.files_dir = root / "files"
        self.verbatim_dir = root / "verbatim"
        self.router_prompt_path = root / "router_prompt.md"
        self.free_services_path = root / "free_services.md"
        self._files: dict[str, CourseFile] = {}
        self._load()

    def _load(self) -> None:
        for path in sorted(self.files_dir.glob("*.md")):
            match = self.FILE_PATTERN.match(path.name)
            if not match:
                continue
            number = match.group(1)
            content = path.read_text(encoding="utf-8")
            title = self._extract_title(content)
            anchors = self._extract_anchors(content)
            self._files[number] = CourseFile(
                number=number,
                title=title,
                path=path,
                content=content,
                anchors=anchors,
            )

    @staticmethod
    def _extract_title(content: str) -> str:
        for line in content.splitlines():
            if line.startswith("# "):
                return line[2:].strip()
        return "Untitled"

    @staticmethod
    def _extract_anchors(content: str) -> list[str]:
        anchors: list[str] = []
        in_section = False
        for line in content.splitlines():
            lower = line.lower().strip()
            if lower.startswith("## semantic anchors"):
                in_section = True
                continue
            if in_section:
                if lower.startswith("## "):
                    break
                if lower:
                    anchors.extend(a.strip() for a in line.split(",") if a.strip())
        return [a.lower() for a in anchors]

    @property
    def router_prompt(self) -> str:
        if self.router_prompt_path.exists():
            return self.router_prompt_path.read_text(encoding="utf-8")
        return ""

    @property
    def free_services(self) -> str:
        if self.free_services_path.exists():
            return self.free_services_path.read_text(encoding="utf-8")
        return ""

    @property
    def verbatim(self) -> str:
        parts: list[str] = []
        if self.verbatim_dir.exists():
            for path in sorted(self.verbatim_dir.glob("*.md")):
                parts.append(path.read_text(encoding="utf-8"))
        return "\n\n".join(parts)

    def get(self, number: str) -> CourseFile | None:
        return self._files.get(number.zfill(2))

    def all_files(self) -> list[CourseFile]:
        return [self._files[k] for k in sorted(self._files)]

    def context_bundle(self, numbers: list[str], *, include_verbatim: bool = True) -> str:
        parts: list[str] = []
        for number in numbers:
            file = self.get(number)
            if file:
                parts.append(file.content)
        if include_verbatim:
            verbatim = self.verbatim.strip()
            if verbatim:
                parts.append(verbatim)
        return "\n\n---\n\n".join(parts)
