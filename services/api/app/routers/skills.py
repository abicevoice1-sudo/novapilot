"""Skill library endpoints: list, create, delete. Skills are SKILL.md files."""

from fastapi import APIRouter, Depends, HTTPException
from novapilot_learning import Skill
from pydantic import BaseModel, Field

from ..auth import require_auth
from ..learning import get_skill_store

router = APIRouter(prefix="/api/skills", tags=["skills"])


class SkillCreate(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    description: str = Field(min_length=1, max_length=300)
    instructions: str = Field(min_length=1, description="Markdown: how to do the thing")
    tools: list[str] = Field(default_factory=list)


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
