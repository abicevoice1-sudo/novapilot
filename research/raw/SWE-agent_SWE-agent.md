# SWE-agent/SWE-agent — research notes

- Canonical URL: https://github.com/SWE-agent/SWE-agent
- Category: [framework/component] — specialized autonomous coding agent (takes a GitHub issue → edits code → runs tests). A reference implementation + research platform, not a general agent framework or product.
- Verification date: 2026-10-18. Stats (from saved GitHub API JSON): 20,588 stars · 2,314 forks · 156 open issues · License: MIT · Primary language: Python · Last push: 2026-10-12 · Archived: no. Latest GitHub release: unknown (no GitHub releases; 1.0 announced Feb 2026 per README news). **Note: README states development has moved to [mini-swe-agent](https://github.com/SWE-agent/mini-SWE-agent), which "has superseded SWE-agent" — evaluate that repo for any adoption.**

## What it provides as a building block
Not a framework to build on — a single-purpose agent design to study: an LM given a small set of well-designed tools (bash, file edit/view, search) inside a sandboxed repo, governed by a single YAML config, solving software-engineering tasks end-to-end. Achieved SOTA on SWE-bench among open-source projects (Feb 2026: SWE-agent 1.0 + Claude 3.7). The transferable lesson is the **agent-computer interface (ACI)**: fewer, better tools beat a large tool catalog.

## Models / providers / cost
- "Your LM of choice" — README names GPT-4o and Claude Sonnet 4 as examples. Full provider list unknown from README (docs cover more; unverified). BYOK inherently.
- Free usage: code is free (MIT); model calls are the user's key. No managed service. Local-model support: unknown from README.

## Memory design
- None. Episodic/task-scoped only; no cross-session personal memory.

## Proactive / scheduling / background
- None. Single-run CLI/batch agent; batch mode exists for benchmarking, not scheduling.

## Browser / computer / file / terminal
- Yes — its core: terminal command execution, file viewing/editing, repo search, inside a containerized/sandboxed workspace (SWE-ReX execution backend is a sibling project). No web browser automation (EnIGMA mode targets CTF challenges, i.e., terminal-based offensive-security tasks).

## Integrations / MCP
- Minimal: configured via a single YAML file; GitHub-issue-driven workflow; Codespaces one-click demo. No MCP story in README.

## Multi-agent
- None. Single agent by design (mini-swe-agent: "100 lines of python").

## Voice / image / document / multimodal
- None. Code/text only.

## As a dependency: install / hardware / cost / maintenance
- Install from source per docs; runs in Docker/Codespaces. Hardware: sandbox container + model API spend (SWE-bench runs are notoriously token-hungry). Maintenance: active-ish (push 6 days ago) but the maintainers' energy is on mini-swe-agent; this repo is in sunset.

## Security posture (embedding it)
- Designed to run untrusted-model-generated code — execution is containerized (SWE-ReX), which is the right pattern. But it is also explicitly dual-use: README advertises "offensive cybersecurity" mode (EnIGMA). As a dependency it offers no auth, no approval gates, no audit logging — it is a research harness, not a hardened component.

## Strengths / weaknesses / lesson
- Strengths: (1) Empirically SOTA open-source coding agent — the ACI design is proven, not theoretical. (2) Radical simplicity: single YAML config, minimal toolset, hackable. (3) Containerized execution (SWE-ReX) is the correct sandbox pattern for code tools.
- Weaknesses: (1) Single-purpose (software engineering) — not a building block for chat, memory, browsing, or scheduling. (2) Token-hungry trajectories make it expensive per task. (3) Repo is superseded by mini-swe-agent; adopting this one means adopting abandonware.
- Best lesson to steal: **design the tool interface first, keep it tiny** — a coding/file subagent with ~5 excellent tools (read, edit, exec, search, test) inside a container will outperform a generalist agent with 50 tools.

## Scores (as a building block for a personal agent)
1. Intelligence/model flexibility: 5 — model-agnostic in principle; tuned around frontier models (GPT-4o/Claude).
2. Persistent memory: 1 — none.
3. Autonomous execution: 7 — strong single-domain autonomy (fix issue → test → iterate); not general.
4. Proactive assistance: 1 — none.
5. Browser/computer control: 6 — excellent terminal/file ACI in a sandbox; no web browser.
6. Integrations/extensibility: 4 — YAML-configured, hackable; no plugin/MCP ecosystem.
7. Privacy/security: 4 — containerized execution is good; no auth/approvals/audit; dual-use offensive mode.
8. Ease of deployment: 6 — Docker/Codespaces one-click; source install per docs.
9. Free-tier/local accessibility: 5 — free code; heavy token spend per task; local-model viability unknown.
10. Reliability/observability: 6 — benchmarked on SWE-bench (reproducible evals); pytest CI; but research-grade.
11. Developer experience: 6 — simple and hackable "by design"; docs site; sunset in favor of mini-swe-agent.
12. Community health: 5 — 20.6k stars, academic maintainers (Princeton/Stanford), but effort moved to mini-swe-agent.

## Verdict
**AVOID as a dependency** (superseded, single-purpose, research harness) — but **ADAPT its lesson**: build the coding/file specialist as a minimal-tool ACI agent in a container, and check mini-swe-agent if a ready-made coding subagent is ever needed.
