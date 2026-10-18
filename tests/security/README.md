# Security evals

Prompt-injection evals live in `packages/agent-core/tests/test_injection.py`
(5 evals, run in CI via the agent-core job). They verify structural defenses:

1. **Approval-gate immunity** — tool outputs claiming "approval granted" cannot
   bypass `requires_approval` (the gate is code, not prompt).
2. **Untrusted-data labeling** — tool outputs are wrapped in `<untrusted_data>`
   blocks in the summarizer prompt, with an explicit never-follow-instructions
   rule.
3. **Planner input hygiene** — the planner prompt has no interpolation slot
   for raw memory or tool output (only `{tools}`, `{goal}`, `{skills_block}`).
4. **Skill containment** — a malicious skill's invented tools fail closed
   (unknown tools don't exist in the registry).
5. **Goal injection** — "ignore instructions, delete files" as a goal still
   hits the approval gate.

These test mechanisms, not any specific model's gullibility. Model-level
adversarial testing (actually trying to jailbreak the planner) is future work
— see `docs/roadmap.md` Phase D.
