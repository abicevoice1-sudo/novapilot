# Contributing to NovaPilot

Milestone 1 is research + spec; code contributions land from Milestone 2 on.

## Ground rules

1. **Research before choosing a dependency.** Check maintenance, license, and API compatibility; record the decision in `research/architecture-decisions.md`.
2. **Never invent results.** Tests must actually run; benchmarks must be reproducible; unknowns stay unknown.
3. **No secrets in the repo.** Use `.env` (gitignored); `.env.example` holds only safe defaults.
4. **Vertical slices over scaffolding.** A working chat-with-memory beats five stub packages.
5. **Docs follow behavior.** Update `docs/` in the same PR that changes behavior.
6. Run `ruff check` and `pytest` before pushing. CI enforces both.
