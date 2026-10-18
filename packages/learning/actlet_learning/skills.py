"""File-based skills: SKILL.md with YAML frontmatter, human-readable and editable.

Format:
    ---
    name: morning-brief
    description: Summarize overnight news from RSS feeds
    tools: [web_fetch, write_file]
    created_from: [task-id-1, task-id-2]
    use_count: 3
    ---
    # morning-brief
    1. Fetch each feed with web_fetch ...
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Skill:
    name: str
    description: str
    instructions: str
    tools: list[str] = field(default_factory=list)
    created_from: list[str] = field(default_factory=list)
    use_count: int = 0

    def prompt_block(self) -> str:
        return f"- {self.name}: {self.description}\n  How: {self.instructions[:400]}"


def _slug(name: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    if not slug:
        raise ValueError("skill name must contain letters or numbers")
    return slug


class SkillStore:
    def __init__(self, skills_dir: str | Path) -> None:
        self.dir = Path(skills_dir)
        self.dir.mkdir(parents=True, exist_ok=True)

    def _path(self, name: str) -> Path:
        return self.dir / _slug(name) / "SKILL.md"

    def save(self, skill: Skill) -> Skill:
        path = self._path(skill.name)
        path.parent.mkdir(parents=True, exist_ok=True)
        front = {
            "name": skill.name,
            "description": skill.description,
            "tools": skill.tools,
            "created_from": skill.created_from,
            "use_count": skill.use_count,
        }
        path.write_text("---\n" + yaml.safe_dump(front, sort_keys=False) + "---\n" + skill.instructions)
        return skill

    def get(self, name: str) -> Skill | None:
        path = self._path(name)
        if not path.is_file():
            return None
        text = path.read_text()
        if not text.startswith("---\n"):
            raise ValueError(f"{path} is not a valid SKILL.md")
        _, front_raw, instructions = text.split("---\n", 2)
        front = yaml.safe_load(front_raw) or {}
        return Skill(
            name=front.get("name", name),
            description=front.get("description", ""),
            instructions=instructions.strip(),
            tools=list(front.get("tools") or []),
            created_from=list(front.get("created_from") or []),
            use_count=int(front.get("use_count") or 0),
        )

    def list(self) -> list[Skill]:
        skills = []
        for path in sorted(self.dir.glob("*/SKILL.md")):
            try:
                skills.append(self.get(path.parent.name))
            except ValueError:
                continue
        return [s for s in skills if s is not None]

    def delete(self, name: str) -> bool:
        path = self._path(name)
        if not path.is_file():
            return False
        path.unlink()
        try:
            path.parent.rmdir()
        except OSError:
            pass
        return True

    def find_relevant(self, goal: str, limit: int = 3) -> list[Skill]:
        """Keyword-overlap matching: cheap, transparent, no embeddings needed."""
        words = set(re.findall(r"[a-z0-9]+", goal.lower())) - _STOPWORDS
        scored = []
        for skill in self.list():
            hay = f"{skill.name} {skill.description} {skill.instructions}".lower()
            hay_words = set(re.findall(r"[a-z0-9]+", hay))
            overlap = words & hay_words
            if overlap:
                scored.append((len(overlap), skill))
        scored.sort(key=lambda t: -t[0])
        return [s for _, s in scored[:limit]]

    def record_use(self, name: str) -> None:
        skill = self.get(name)
        if skill is not None:
            skill.use_count += 1
            self.save(skill)


_STOPWORDS = frozenset(
    ["the", "a", "an", "to", "of", "and", "for", "in", "on", "with", "my", "me", "i", "you", "your", "is", "are", "be", "do", "does", "did", "what", "when", "where", "how", "why", "which", "who", "this", "that", "these", "those", "it", "its", "at", "as", "by", "from", "please"]
)
