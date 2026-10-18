"""Skill library endpoints: list, create, delete. Skills are SKILL.md files."""

from actlet_learning import Skill
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..auth import require_auth
from ..learning import get_skill_store

router = APIRouter(prefix="/api/skills", tags=["skills"])


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=300)
    instructions: str = Field(min_length=1, max_length=50000, description="Markdown: how to do the thing")
    tools: list[str] = Field(default_factory=list, max_length=50)


def _serialize(s: Skill) -> dict:
    return {
        "name": s.name,
        "description": s.description,
        "instructions": s.instructions,
        "tools": s.tools,
        "created_from": s.created_from,
        "use_count": s.use_count,
    }


@router.get("", dependencies=[Depends(require_auth)])
async def list_skills():
    return {"skills": [_serialize(s) for s in get_skill_store().list()]}


@router.post("", dependencies=[Depends(require_auth)])
async def create_skill(req: SkillCreate):
    try:
        skill = get_skill_store().save(
            Skill(
                name=req.name.strip(),
                description=req.description.strip(),
                instructions=req.instructions.strip(),
                tools=req.tools,
            )
        )
    except ValueError as e:
        raise HTTPException(400, str(e)) from e
    return _serialize(skill)


@router.get("/{name}", dependencies=[Depends(require_auth)])
async def get_skill(name: str):
    skill = get_skill_store().get(name)
    if skill is None:
        raise HTTPException(404, "skill not found")
    return _serialize(skill)


@router.delete("/{name}", dependencies=[Depends(require_auth)])
async def delete_skill(name: str):
    if not get_skill_store().delete(name):
        raise HTTPException(404, "skill not found")
    return {"deleted": name}


@router.get("/{name}/export", dependencies=[Depends(require_auth)])
async def export_skill(name: str):
    """Download a skill as portable SKILL.md (share it with anyone)."""
    store = get_skill_store()
    skill = store.get(name)
    if skill is None:
        raise HTTPException(404, "skill not found")
    real = store._path(name)  # store-owned path logic; no traversal
    if not real.is_file():
        raise HTTPException(404, "skill file missing")
    return {"name": skill.name, "filename": f"{skill.name}.SKILL.md", "content": real.read_text()}


class SkillImport(BaseModel):
    content: str = Field(min_length=1, max_length=100000, description="SKILL.md markdown (with YAML frontmatter)")


@router.post("/import", dependencies=[Depends(require_auth)])
async def import_skill(req: SkillImport):
    """Install a skill from SKILL.md text (paste what someone shared)."""
    import re

    import yaml

    text = req.content.strip()
    if not text.startswith("---\n"):
        raise HTTPException(400, "not a valid SKILL.md (missing YAML frontmatter)")
    try:
        _, front_raw, instructions = text.split("---\n", 2)
        front = yaml.safe_load(front_raw) or {}
        name = str(front.get("name", "")).strip()
        if not name or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9 _-]*", name):
            raise ValueError("frontmatter needs a valid 'name'")
        skill = get_skill_store().save(
            Skill(
                name=name,
                description=str(front.get("description", "")).strip(),
                instructions=instructions.strip(),
                tools=list(front.get("tools") or []),
            )
        )
    except ValueError as e:
        raise HTTPException(400, f"invalid SKILL.md: {e}") from e
    return _serialize(skill)
