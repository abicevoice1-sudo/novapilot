# Contributing to Actlet

Thanks for being here. Actlet is built in the open, and good contributions are welcome.

## The one rule

**Don't claim what you can't prove.** Every feature ships as: build → tests → live verify → docs → commit. If you can't verify it works, label it honestly in `docs/roadmap.md`.

## How to contribute

1. Fork the repo, create a branch.
2. Add tests for your change (`pytest` — every package has a `tests/` dir).
3. Run `ruff check .` — it must be clean.
4. Update docs if behavior changed.
5. Open a PR with: what you built, how you verified it, what you didn't verify.

## What we're looking for

- New channel plugins (WhatsApp, Discord, Matrix…) — see `packages/channels/` for the pattern
- New tools for the agent — see `packages/agent-core/`
- UI improvements in `apps/web/`
- Prompt-injection evals in `tests/security/` — try to break the approval gates
- Bug reports with reproduction steps

## What we won't merge

- Features without tests
- Unverified claims in docs or README
- Anything that weakens the approval-gate safety model

## Code of conduct

Be kind. Be honest. Assume good intent.
