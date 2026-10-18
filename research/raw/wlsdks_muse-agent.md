# wlsdks/muse-agent

- **Canonical URL:** https://github.com/wlsdks/muse-agent (no redirect observed)
- **Category:** Local-first, continuity-focused personal AI agent — CLI + local web console, "remembers the state you meant to continue."

**Verification date:** 2026-10-18. Stats: the saved GitHub API JSON for this repo contained only a **rate-limit error**, so stars/forks/open issues/last push/archived are **unknown**. Language: **TypeScript** (README-evidenced). License: **MIT**. Latest release: **v0.3.0 prerelease** (verified on releases page; "first deliberate product boundary" after v0.2.42; native desktop companion macOS-only).

## Models / free / local / BYOK
- **Provider-neutral `ModelProvider` interface** — `agent-core` never touches vendor SDKs; adapters for OpenAI, Anthropic, Gemini, OpenRouter, Ollama, OpenAI-compatible (LM Studio via baseUrl). Missing capabilities degrade explicitly.
- **Local-first:** `muse setup local` points at Ollama (`gemma4:12b` example); `MUSE_LOCAL_ONLY=true` makes remote model/cloud-voice paths **hard errors**, not silent fallbacks.

## Memory
- Local stores under `~/.muse/` (plaintext by default; memory/episodes/action log encryptable at rest on request; credentials in OS keychain). Commands: `muse remember` / `recall` / `forget`; facts, preferences, goals, vetoes.
- **Grounding gate**: retrieval is a gate in front of the model — rank → weigh (stale marked) → cite → **abstain below confidence** → user corrections stored and decay the replaced belief. Measured: grounding gate ON 16/17 vs OFF 0/17 faithfulness (self-authored corpus).
- **AttuneGraph** (experimental): agent-native temporal/provenance graph on embedded SQLite (pinned `@attunegraph/core` submodule); exact continuity receipts, bounded queries, read-only Lens; full graph Admin is roadmap.

## Proactive / scheduling / background / goals
- `muse proactive watch` — "speaks first inside a hard interruption budget, never as an autonomous send." **Shadow Muse** (learns when to speak — partly built), morning brief (`muse setup briefing`), **quiet hours** (real setting), reminders, follow-ups, delivery canaries; one runtime across CLI/web/messaging/scheduled jobs; `muse trace`/`muse resume` checkpoints.

## Browser / computer / files / terminal
- "Guarded tools and browser actions" with fail-close guards, bounded loops, timeouts; browsing visits stored in continuity baselines.
- **Terminal: restricted** — "Standard personal runtimes no longer expose a general command runner"; risky execution via Rust `runner` child process; coding execution moved to a dedicated tool. (Security-over-capability tradeoff.)

## Integrations / APIs / plugins / MCP / messaging
- **Email:** IMAP/SMTP app-password path (no Google Cloud project) + Gmail OAuth with indefinite token refresh; **calendar:** 5 backends behind one interface.
- **MCP both directions**: external servers behind an allowlist (`muse mcp login` with OAuth 2.1; one-click Atlassian preset) and **`muse mcp serve`** exposing read-only grounded recall to other agents.
- Channels: web, Telegram, Matrix, remote CLI over tailnet. Never: money movement, bank/brokerage (permanently out of scope).

## Multi-agent
- **Council debates**: multi-agent worker panels with agreement/disagreement checks (release notes describe fixing an inverted conflict check — "silenced minority voices" surfaced as dissent). Continuity threads link external GitHub issues/PRs via MCP.

## Voice / image / documents / multimodal
- Cloud voice paths exist but are disabled under `MUSE_LOCAL_ONLY`; document/note-grounded answers; no image generation claimed.

## Install / hardware / cost / maintenance
- `git clone --recurse-submodules` (attunegraph pinned), `corepack enable`, `pnpm install:muse`, `muse onboard`; **Node ≥22** (24.15+ for SQLite store); `muse doctor` self-repairs; `muse update`. macOS-first (daemon = LaunchAgent; native desktop macOS-only). Runs on own Ollama — hardware: enough RAM for a 12B model.

## Security / privacy
- Deterministic, code-enforced boundaries (not prompt instructions): no money movement, **draft-first sends** (owner confirms exact content/recipient), continuity threads user-authored, SSRF/symlink boundaries, fail-closed stores, URL-egress must be user-quoted, link-preview suppression, scoped time-bound consents, web pages cannot teach rules, injected-tool-description guard. Adversarial **audits published with failures fixed**. Privacy policy doc: what is/isn't covered.

## Top 3 strengths
1. **Honesty as architecture**: grounding gate, abstention, receipts, "evidence ledgers never promoted past their evidence" — the strongest epistemic discipline in this batch.
2. Provider-neutral core + local-only hard mode + explicit capability degradation.
3. Draft-first/never-send-unauthorized posture enforced in code, with published audits and corrected failures.

## Top 3 weaknesses
1. Experimental 0.x, macOS-first; flagship ideas (Shadow Muse, Continuity Capsule, Policy Card) largely roadmap.
2. No general command runner in standard runtimes — caps autonomous coding/execution depth.
3. Small/unknown community; eval battery "not fully green"; recall-correction unqualified.

## Best lesson to steal
**The grounding gate + separate evidence ledgers**: retrieval as a gate before the model, abstention on low confidence, and the rule that tests/synthetic runs stay in their own ledgers and are never promoted into claims. Adopt this honesty discipline verbatim.

## Scores (1–10, evidence)
1. Intelligence/model flexibility: **7** — provider-neutral interface, Ollama default, explicit degradation.
2. Persistent memory: **8** — grounded recall with citations, continuity threads, AttuneGraph receipts; correction handling.
3. Autonomous execution: **6** — guards, checkpoints, resume; general runner removed caps depth.
4. Proactive assistance: **6** — interruption budget, quiet hours, morning brief; Shadow Muse partial.
5. Browser/computer control: **5** — guarded browser actions; terminal deliberately restricted.
6. Integrations/extensibility: **7** — bidirectional MCP, email/calendar backends, Telegram/Matrix.
7. Privacy/security: **9** — code-enforced boundaries, fail-closed, audits; best in batch.
8. Ease of deployment: **7** — scripted install + doctor; macOS-first, Node 24.
9. Free-tier/local accessibility: **9** — Ollama default, local-only hard mode; best local story for CLI.
10. Reliability/observability: **6** — 512 compiled tests, smoke/eval gates, fail-closed; experimental.
11. User experience: **6** — CLI-first, web console, mascot polish; desktop macOS-only.
12. Community health: **4** — single primary author, stats unverifiable today.

## Verdict
**Active** (v0.3.0 prerelease, releases page fetched today). Keep — the security/honesty model and provider-neutral core are reference-grade. Replacement if dropped: NousResearch/hermes-agent (broader but less disciplined) or Letta (memory framework).
