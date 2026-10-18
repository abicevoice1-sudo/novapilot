# Learning loop — dreaming + skills

Actlet gets smarter the more you use it, without phoning anything home.

## Dreaming (nightly consolidation)

Every night at 02:00 (auto-created schedule, editable like any other), the
agent reviews recently completed tasks and extracts **durable** learnings —
preferences, recurring projects, facts that will matter in a month. One-off
task details are ignored.

- Facts are stored as ordinary memories (`source: "dreaming"`): redacted,
  deduplicated, searchable, editable, deletable by you.
- A bad model response is dropped, never stored half-parsed.
- `POST /api/dreaming/run` runs it on demand (502 if no model is reachable —
  dreaming is honest about needing a brain).

## Skills (reusable playbooks)

When the agent does something well, turn it into a skill:
`POST /api/tasks/{id}/make-skill` asks the model to synthesize a playbook
from a completed task's steps. If the task is too one-off, it says so
(`{"skipped": true}`) instead of inventing a skill.

Skills live as `SKILL.md` files (YAML frontmatter + markdown) under
`<workspace>/skills/` — readable and editable in any text editor, no database
diving required. The planner automatically sees skills relevant to your goal
(keyword matching, no embeddings, no black box).

## Design rules

- Learning never bypasses safety: skills are instructions, not permissions.
  A skill can't grant itself tool access — approvals still apply.
- Everything the loop learns is visible: memories page, skills page, and the
  raw files on disk.
