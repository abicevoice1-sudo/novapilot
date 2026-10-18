# Competitor matrix — 20 repositories

**Verification date:** 2026-10-18 (all stats pulled live from the GitHub API or READMEs on this date; see `research/raw/` for per-repo evidence files and `research/repository-evidence.md` for the verification log).
**Scope:** personal AI agents and the frameworks/components used to build them. Products and frameworks are scored on the same 12 dimensions but **ranked separately** — a library is not a product.

## How to read the scores

Each dimension scored 1–10 by an independent researcher with a one-line evidence note in the raw file. `?` = unknown (evidence absent; never invented). Dimensions:

1. Intelligence / model flexibility · 2. Persistent memory · 3. Autonomous execution · 4. Proactive assistance · 5. Browser / computer control · 6. Integrations / extensibility · 7. Privacy / security · 8. Ease of deployment · 9. Free-tier / local-model accessibility · 10. Reliability / observability · 11. UX (end-user; frameworks scored on developer experience) · 12. Community health / maintainability

## Master stats table

| # | Repository | Category | Stars | Forks | Open issues | License | Lang | Last push | Verdict |
|---|------------|----------|------:|------:|------------:|---------|------|-----------|---------|
| 1 | [nano-muse/nanoMuse](https://github.com/nano-muse/nanoMuse) | product · phone-first personal agent | 1,399 | 154 | 55 | GPL-3.0 | Swift | 2026-10-18 | keep |
| 2 | [jerelvelarde/openmuse](https://github.com/jerelvelarde/openmuse) | product · alpha personal agent | ? (API rate-limited) | ? | ? | ? | ? | ? | keep (alpha) |
| 3 | [wlsdks/muse-agent](https://github.com/wlsdks/muse-agent) | product · local-first CLI agent | ? (API rate-limited) | ? | ? | ? | ? | v0.3.0 prerelease | keep |
| 4 | [openclaw/openclaw](https://github.com/openclaw/openclaw) | product · agent runtime + marketplace | **392,307** ✓ | 82,464 | 9,375 | MIT | TypeScript | 2026-10-18 | keep |
| 5 | [NousResearch/hermes-agent](https://github.com/NousResearch/hermes-agent) | product · self-improving agent OS | **254,743** ✓ | 55,389 | 49,856 | MIT | Python | 2026-10-18 | keep |
| 6 | [agent0ai/agent-zero](https://github.com/agent0ai/agent-zero) | product · Docker desktop computer-use agent | ? (API rate-limited; 3rd-party claim ~17k unverified) | ? | ? | ? | Python | ? | keep |
| 7 | [khoj-ai/khoj](https://github.com/khoj-ai/khoj) | product · self-hosted RAG "second brain" | 37,726 | 2,519 | 169 | **AGPL-3.0** | Python | 2026-08-02 | keep (ideas only — copyleft) |
| 8 | [nearai/ironclaw](https://github.com/nearai/ironclaw) | product · Rust privacy-first agent OS | 12,661 | 1,482 | 1,552 | Apache-2.0 | Rust | 2026-10-18 | keep |
| 9 | [HKUDS/nanobot](https://github.com/HKUDS/nanobot) | product · lightweight Python agent framework+apps | 49,141 | 8,639 | 866 | MIT | Python | 2026-10-17 | keep |
| 10 | [sipeed/picoclaw](https://github.com/sipeed/picoclaw) | product · edge/embedded agent (Go) | ? (README claims 26k, unverified) | ? | ? | MIT (per README) | Go | ? | keep |
| 11 | [zeroclaw-labs/zeroclaw](https://github.com/zeroclaw-labs/zeroclaw) | product · Rust single-binary agent | 32,991 | 4,976 | 1,001 | Apache-2.0 (README: MIT OR Apache-2.0) | Rust | 2026-10-18 | keep |
| 12 | [letta-ai/letta](https://github.com/letta-ai/letta) | product · stateful-agent harness (source now at `letta-code`) | 25,176 | 2,649 | 0 (disabled) | Apache-2.0 | — (signpost) | 2026-09-10 | keep |
| 13 | [OpenHands/OpenHands](https://github.com/OpenHands/OpenHands) | framework · agent control center (renamed from `All-Hands-AI`) | 91,163 | 12,098 | 1,055 | MIT | TypeScript | 2026-10-17 | keep (framework evidence) |
| 14 | [browser-use/browser-use](https://github.com/browser-use/browser-use) | component · browser-agent library | ? (API rate-limited) | ? | ? | MIT | Python/TS | ? | keep (component) |
| 15 | [browserbase/stagehand](https://github.com/browserbase/stagehand) | component · browser SDK (act/observe/extract) | 25,720 | 1,764 | 402 | MIT | TypeScript | 2026-10-17 | keep (component) |
| 16 | [mem0ai/mem0](https://github.com/mem0ai/mem0) | component · memory layer | 67,370 | 7,940 | 841 | Apache-2.0 | Python | 2026-10-17 | keep (component) |
| 17 | [langchain-ai/langgraph](https://github.com/langchain-ai/langgraph) | framework · agent orchestration runtime | 43,426 | 7,401 | 651 | MIT | Python | 2026-10-18 | keep (framework) |
| 18 | [crewAIInc/crewAI](https://github.com/crewAIInc/crewAI) | framework · role-based multi-agent | 59,813 | 8,762 | 753 | MIT | Python | 2026-10-18 | keep (framework) |
| 19 | [microsoft/autogen](https://github.com/microsoft/autogen) | framework · multi-agent (ARCHIVED) | 61,455 | 9,294 | 1,125 | API reports CC-BY-4.0 | Python | 2026-10-16 | **avoid** (archived, no security fixes) |
| 20 | [SWE-agent/SWE-agent](https://github.com/SWE-agent/SWE-agent) | component · coding-agent harness (sunset → mini-swe-agent) | 20,588 | 2,314 | 156 | MIT | Python | 2026-10-12 | keep (ideas only) |

✓ = independently re-verified with a second API call on 2026-10-18 (the two viral outliers).
`?` = GitHub API rate-limited at check time; the value is genuinely unknown, not zero.

## Score table — personal-agent products (12)

| # | Repo | 1 intel | 2 mem | 3 auto | 4 proact | 5 browser | 6 integ | 7 sec | 8 deploy | 9 free | 10 rel | 11 ux | 12 comm |
|---|------|---------|-------|--------|----------|-----------|---------|-------|----------|--------|--------|-------|-------|
| 1 | nanoMuse | 8 | 7 | 7 | 6 | 8 | 7 | 7 | 9 | 8 | 5 | 8 | 5 |
| 2 | openmuse | 6 | 5 | 6 | 6 | 7 | 4 | 7 | 6 | 7 | 5 | 7 | 3 |
| 3 | muse-agent | 7 | 8 | 6 | 6 | 5 | 7 | 9 | 7 | 9 | 6 | 6 | 4 |
| 4 | openclaw | 8 | 7 | 7 | 7 | 7 | 9 | 7 | 8 | 7 | 6 | 8 | 7 |
| 5 | hermes-agent | 8 | 9 | 8 | 8 | 7 | 9 | 7 | 8 | 8 | 6 | 8 | 7 |
| 6 | agent-zero | 8 | 7 | 8 | 5 | 9 | 9 | 6 | 7 | 8 | 6 | 8 | 7 |
| 7 | khoj | 8 | 6 | 7 | 6 | 4 | 8 | 7 | 7 | 8 | 6 | 7 | 8 |
| 8 | ironclaw | 6 | 7 | 7 | 5 | 1 | 8 | 9 | 7 | 4 | 6 | 6 | 7 |
| 9 | nanobot | 8 | 8 | 6 | 4 | 3 | 8 | 6 | 8 | 7 | 6 | 8 | 9 |
| 10 | picoclaw | 9 | 4 | 7 | 5 | 4 | 9 | 4 | 8 | 7 | 4 | 7 | ? |
| 11 | zeroclaw | 9 | 6 | 8 | 7 | 6 | 9 | 9 | 8 | 8 | 7 | 7 | 8 |
| 12 | letta | 8 | 10 | 7 | 8 | 6 | 8 | 7 | 8 | 6 | 7 | 8 | 8 |

## Score table — frameworks / components (8)

Scored **as building blocks** (dim 11 = developer experience).

| # | Repo | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11dx | 12 |
|---|------|---|---|---|---|---|---|---|---|---|----|------|----|
| 13 | OpenHands | 8 | 2 | 9 | 6 | 7 | 8 | 7 | 6 | 6 | 7 | 7 | 9 |
| 14 | browser-use | 7 | 1 | 6 | 1 | 9 | 8 | 5 | 7 | 6 | 6 | 6 | ? |
| 15 | stagehand | 5 | 1 | 5 | 1 | 8 | 7 | 7 | 7 | 6 | 6 | 6 | 8 |
| 16 | mem0 | 7 | 10 | 2 | 1 | 1 | 7 | 6 | 7 | 5 | 6 | 8 | 9 |
| 17 | langgraph | 9 | 7 | 8 | 3 | 3 | 9 | 7 | 7 | 8 | 8 | 8 | 10 |
| 18 | crewai | 8 | 5 | 8 | 3 | 4 | 9 | 5 | 6 | 8 | 6 | 8 | 9 |
| 19 | autogen | 6 | 3 | 6 | 2 | 6 | 7 | 2 | 6 | 6 | 4 | 5 | 3 |
| 20 | swe-agent | 5 | 1 | 7 | 1 | 6 | 4 | 4 | 6 | 5 | 6 | 6 | 5 |

## Weighted overall ranking — personal-agent products

Weights reflect what a *personal* agent lives or dies on: memory ×1.5, autonomous execution ×1.5, privacy/security ×1.5, proactivity ×1.25, browser/computer ×1.25, free/local ×1.25, intelligence ×1.0, integrations ×1.0, reliability ×1.0, UX ×1.0, deploy ×0.75, community ×0.75 (sum 13.75; picoclaw normalized over 13.0 with dim 12 unknown).

| Rank | Product | Weighted score /10 | One-line read |
|------|---------|-------------------:|---------------|
| 1 | **hermes-agent** | **7.78** | Strongest all-rounder: learning loop + local models + proactivity. Weakness: enormous scope, release-mishap history. |
| 2 | **zeroclaw** | **7.62** | Best trust story: tiered autonomy + tool receipts + OS sandboxes. Weakness: no multi-agent, 1k-issue backlog. |
| 3 | **letta** | **7.60** | Best memory architecture anywhere (blocks + MemFS + dreaming). Weakness: cloud-default lock-in, repo split. |
| 4 | **agent-zero** | **7.31** | Best computer-use (full XFCE desktop + Time Travel). Weakness: safety = user discipline; no goal/proactive loop. |
| 5 | **openclaw** | **7.27** | Biggest ecosystem (ClawHub, 20+ channels). Weakness: host-exec default, scale complexity. |
| 6 | **nanoMuse** | **7.09** | Best phone-first UX + human-takeover logins. Weakness: 3 weeks old, thin reliability record. |
| 7 | **muse-agent** | **6.82** | Best security posture (fail-closed, code-enforced) + best local story. Weakness: solo author, macOS-first. |
| 8 | **khoj** | **6.78** | Best document memory + scheduled research automations. Weakness: AGPL copyleft; no browser/computer use. |
| 9 | **nanobot** | **6.56** | Best lightweight footprint + markdown memory. Weakness: no replay after restart, thin safety model. |
| 10 | **ironclaw** | **6.05** | Security benchmark (WASM sandbox, AES secrets, no telemetry). Weakness: no browser, BYOK-only, PG friction. |
| 11 | **picoclaw** | **5.96** | Edge extreme (10–20MB RAM, rule-based routing). Weakness: self-declared "not production-ready", weak memory. |
| 12 | **openmuse** | **5.87** | Honesty exemplar (VERIFICATION.md) + durable tasks. Weakness: solo-author alpha, fictional-data default. |

**What the ranking says:** nobody clears 8/10. The leader (hermes-agent) wins on breadth, not on trust or focus. The top-3 cluster (hermes-agent, zeroclaw, letta) defines the bar: learning memory + audited autonomy + tiered storage. Every product below 7 has a structural hole (no browser, no memory, no proactivity, or no security story).

## Ranking for free and self-hosted usage

Ordered by genuinely-free usability (local inference + BYOK + no mandatory subscription), not by marketing:

1. **muse-agent** — Ollama default, local-only hard mode, explicit degradation. Best $0 story for CLI users.
2. **hermes-agent** — one-click llama.cpp runtime with hardware-rated model picks; local-first credible.
3. **zeroclaw** — Ollama + ~20 BYOK providers + fallback routing; single binary, runs on own hardware.
4. **nanobot** — Ollama/vLLM + model fallbacks; one-line installer; runs anywhere Python runs.
5. **khoj** — free cloud app + free self-host + local-LLM support (AGPL caveat on the code).
6. **agent-zero** — runs on a $6 VPS / Raspberry Pi; local-model presets; you pay only LLM API.
7. **nanoMuse** — free relay allowance + self-host; allowance is dev-funded, not guaranteed.
8. **picoclaw** — $10 hardware + Ollama; but intelligence still needs paid BYOK keys.
9. **openclaw** — free software, own hardware; models are BYOK-cost.
10. **letta** — local backend free, but model keys BYO and cloud is the default path.
11. **openmuse** — runs without keys but on fictional data; real use needs BYOK + Google setup.
12. **ironclaw** — BYOK-only, no free inference documented, own hardware required.

## Feature-by-feature comparison (products)

| Capability | Best in class | Also strong | Notably absent everywhere |
|---|---|---|---|
| Provider-neutral model gateway | zeroclaw (20+ providers + fallback routing) | hermes-agent (300 via portal), nanobot, nanoMuse (21) | Cost/latency budgets per task; only picoclaw has rule-based routing |
| Durable memory | letta (blocks + MemFS + dreaming) | hermes-agent (learning loop), muse-agent (grounded recall + receipts) | User-editable memory with provenance everywhere except nanobot/letta |
| Scheduling / background | zeroclaw (SOP engine + service install) | khoj (APScheduler automations that email), letta (crons + heartbeats) | Missed-schedule replay (nanobot admits the gap); goal tracking rare |
| Proactive assistance | hermes-agent (nudges + NL automations) | letta (self-managed schedules) | Learned proactivity from behavior; all are cron/rules-based |
| Browser / computer use | agent-zero (full desktop + Time Travel) | nanoMuse (screen-hands + takeover), openmuse (takeover console) | Stealth + human-takeover + injection-hardened in one package |
| Human approval gates | zeroclaw (tiered autonomy + receipts) | muse-agent (fail-closed, code-enforced) | Consumer-grade approval UX; most are CLI flags or nothing |
| Prompt-injection defense | ironclaw (defense tiers, documented) | stagehand (credentials bypass model) | Tested, benchmarked injection resistance — nobody publishes it |
| Messaging channels | zeroclaw/openclaw (30+/20+ channels) | nanobot (10+), hermes-agent (7) | — (solved problem) |
| Multi-agent | hermes-agent, agent-zero (hierarchical subagents) | letta (agents-as-subagents) | Structured result exchange + verification of subagent outputs |
| Voice | zeroclaw, nanoMuse | — | Voice-first interaction design; all are chat-first |
| Evals / benchmarks | — | mem0 (LoCoMo/LongMemEval — platform only) | Reproducible personal-agent evals: **nobody** |

## Each competitor's best idea and biggest weakness

| Repo | Best idea to steal | Biggest weakness to avoid |
|------|-------------------|---------------------------|
| nanoMuse | Device-federated approvals + "screen-hands" with human login handoff | 3 weeks old; relay operator can see conversations |
| openmuse | `docs/VERIFICATION.md` honesty discipline — document what is verified vs fictional | Solo-author alpha; live features all need user's own keys |
| muse-agent | Grounding gate + evidence ledgers + fail-closed, code-enforced safety | macOS-first, single author, terminal restricted by design |
| openclaw | Per-agent tool profiles with fail-closed allowlists + ClawHub marketplace | Host-exec default; 9,375 open issues; scale complexity |
| hermes-agent | Autonomous skill creation + self-improving skills + periodic nudges | Enormous scope; shipped-wrong-commit incident; portal subscription layer |
| agent-zero | Time Travel snapshots: checkpoint/revert around desktop actions | Safety = Docker + user discipline; no goal/proactive loop |
| khoj | Scheduled research automations that email results (cheap, safe proactivity) | AGPL-3.0 copyleft; no browser/computer use; slowed cadence |
| ironclaw | WASM→Allowlist→LeakScan→CredentialInjector→Execute→LeakScan sandbox pipeline | No browser; BYOK-only; PostgreSQL install friction |
| nanobot | Dream consolidation into diffable `USER.md`/`MEMORY.md` markdown | Missed schedules not replayed; no approval workflow; token = full admin |
| picoclaw | Decouple runtime from inference: tiny binary + BYOK + rule-based cost routing | Self-declared not production-ready; JSONL-only memory |
| zeroclaw | Per-action cryptographic tool receipts + default-supervised tiered autonomy | No multi-agent; YOLO mode bypasses its own gates; 1,001 open issues |
| letta | Memory blocks + scheduled "dreaming" consolidation + MemFS versioning | Cloud-default + sign-in for secrets; confusing repo split |
| OpenHands | ACP: neutral JSON-RPC interface decoupling control plane from agent/model | Category drift — no longer a personal assistant |
| browser-use | Browser-as-pluggable-tool with persistent profiles (sessions survive runs) | No budgets; injection hardening undocumented; token-hungry |
| stagehand | observe→act separation: credentials never enter the model context | Vendor pull toward Browserbase cloud; every step costs an LLM call |
| mem0 | Add-only memory + entity linking + temporal-ranked retrieval | OSS ≠ platform (benchmarks reflect managed optimizations); no anti-poisoning filters |
| langgraph | Durable execution + checkpointing + human-in-the-loop interrupts | No scheduler/proactivity/browser/gateway — runtime only |
| crewai | Declarative role-based specialist agents (Crews/Flows pattern) | Telemetry default-on; weaker memory; duplicates LangGraph's role |
| autogen | Agents-as-tools delegation pattern | **Archived — no security fixes; do not build on it** |
| swe-agent | Minimal, well-designed agent-computer interface (few excellent tools) | Sunset research harness; single-domain |

## The 10 most important opportunities competitors leave open

1. **Memory + computer-use + proactivity in one coherent product.** Letta owns memory, agent-zero owns computer-use, hermes-agent owns proactivity. Nobody fuses all three without scope bloat.
2. **Audited autonomy as consumer UX.** Zeroclaw's tool receipts and tiered autonomy are CLI-first; muse-agent's fail-closed safety is macOS-only. A polished web approval/audit surface doesn't exist.
3. **Honest capability boundaries.** muse-agent's explicit degradation and openmuse's VERIFICATION.md are exceptions. Most projects overclaim; a product that says "I can't do X without Y" earns trust.
4. **Per-task cost and latency budgets with model routing.** Only picoclaw routes by cost; nobody gives users a visible budget that the agent must respect.
5. **Human-readable, user-owned memory.** nanobot's markdown and letta's /palace point the way; mem0's best version lives in their cloud. Local-first, editable, exportable, deletable memory is still rare.
6. **True local-first intelligence.** hermes-agent's llama.cpp and muse-agent's Ollama-default prove it's possible; most "local support" is a checkbox with a weak model story.
7. **Cross-device identity without cloud lock-in.** Letta does it via their cloud; ironclaw is single-machine. Local-first sync across a user's own devices is unsolved.
8. **Reproducible evaluations.** No personal-agent project publishes a benchmark suite. Claims rest on stars and demos.
9. **Tested prompt-injection resistance.** Ironclaw documents defense tiers; nobody publishes adversarial test results. For a product that reads the web and runs code, this is the missing safety case.
10. **A genuinely polished web app.** Every serious contender is CLI/TUI/developer-first. The consumer-grade web UX slot is empty.

## Implementation decision matrix — adopt / adapt / avoid / buy

| Item | Decision | Rationale |
|------|----------|-----------|
| LangGraph (agent runtime) | **ADOPT** | Durable execution, checkpointing, HITL interrupts = the approval-gate primitive. MIT, model-agnostic, 43k★, maintained. |
| mem0 self-hosted (memory layer) | **ADOPT** | Best OSS memory primitive (add/search API, entity linking). Caution: its benchmark numbers reflect the managed platform; self-host and measure ourselves. |
| LiteLLM (model gateway) | **ADOPT** | 61k★, active, unified interface across 100+ providers, fallbacks, cost tracking. Verified 2026-10-18. (License: MIT per project LICENSE — re-verify at build time.) |
| Playwright (browser engine) | **ADOPT** | Mature, maintained, the substrate under every serious browser agent. |
| FastAPI + React/Vite + SQLite→Postgres | **ADOPT** | Smallest dependable stack for a single-user MVP; documented in ADRs. |
| Hermes-agent learning loop (skills that self-improve + nudges) | **ADAPT** | Core differentiator pattern; reimplement scoped to our memory model, without the 600-plugin scope. |
| Letta memory blocks + dreaming consolidation | **ADAPT** | Tiered memory (fast blocks + archival store) + background reflection jobs; local-first, no cloud. |
| Zeroclaw tool receipts + tiered autonomy | **ADAPT** | Every consequential action gets a signed receipt; default-supervised with labeled escape hatch. |
| Ironclaw sandbox pipeline (allowlist → scan → execute → scan) | **ADAPT** | Implement over Docker + network allowlists for MVP; WASM later if justified. |
| Stagehand observe→act credential pattern | **ADAPT** | Secrets never enter model context; deterministic selectors for credential entry. |
| Nanobot markdown memory (USER.md/MEMORY.md) | **ADAPT** | Human-readable export/mirror of the memory store; user can edit in any editor. |
| Khoj scheduled research automations | **ADAPT** | Email/chat delivery of scheduled research = cheap, safe proactivity. |
| Agent-zero Time Travel checkpoints | **ADAPT** | Snapshot/revert around destructive actions. |
| OpenClaw ClawHub skills marketplace pattern | **ADAPT** | Skills as installable markdown+YAML packages; our own registry later. |
| ACP neutrality pattern | **ADAPT** | Control plane (UI, scheduler, permissions) never hard-couples to a model vendor. |
| Muse-agent fail-closed boundaries + VERIFICATION.md honesty | **ADAPT** | Code-enforced safety boundaries; docs distinguish verified vs planned. |
| Browser-use as browser tool module | **ADAPT (library, not product)** | Pluggable local↔cloud browser with persistent profiles; enforce per-task token budgets (its missing piece). |
| CrewAI role-based specialist pattern | **ADAPT (pattern only)** | Declarative specialist agents; implemented on LangGraph, not as a dependency. |
| AutoGen (any version) | **AVOID** | Archived by Microsoft; no security fixes. Steal only the agents-as-tools pattern. |
| SWE-agent as dependency | **AVOID** | Sunset research harness; steal the minimal-ACI lesson instead. |
| CrewAI as dependency | **AVOID** | Duplicates LangGraph with weaker memory and telemetry default-on. |
| Khoj source code | **AVOID (copying)** | AGPL-3.0 copyleft is incompatible with our Apache-2.0 plan. Ideas only. |
| Browser-use cloud / Browserbase lock-in | **AVOID (dependence)** | Use as swappable modules; local-first default. |
| Building our own model gateway from scratch | **AVOID** | LiteLLM already solves it; don't NIH the hardest part. |
| Building our own vector DB / memory engine from scratch | **AVOID** | mem0 self-hosted + SQLite FTS5 covers MVP; measure before inventing. |

---

*Matrix compiled from `research/raw/*.md` (20 evidence files, verification date 2026-10-18). Weighted ranking weights: memory ×1.5, autonomy ×1.5, security ×1.5, proactivity ×1.25, browser ×1.25, free/local ×1.25, intelligence ×1.0, integrations ×1.0, reliability ×1.0, UX ×1.0, deploy ×0.75, community ×0.75.*
