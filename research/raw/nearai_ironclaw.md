# nearai/ironclaw — evidence file

**Canonical URL:** https://github.com/nearai/ironclaw
**Category:** Privacy/security-first "Agent OS" — local personal AI assistant platform (Rust).
**Rename/fork note:** README declares "OpenClaw Heritage" — IronClaw is a Rust *reimplementation inspired by* [OpenClaw](https://github.com/openclaw/openclaw), NOT a fork (GitHub JSON: `"fork": false`, topics include `openclaw`). Key documented differences: Rust vs TypeScript, WASM sandbox vs Docker, PostgreSQL vs SQLite, security-first design. A FEATURE_PARITY.md tracks OpenClaw parity. No rename/redirect indicated.
**Homepage:** https://www.ironclaw.com

**Verification date:** 2026-10-18. Stats from saved GitHub API JSON: stars 12,661 | forks 1,482 | open issues 1,552 | watchers 78 subscribers. Language: Rust. Created 2026-02-03. Last push 2026-10-18T02:53:33Z. Archived: false. Disabled: false.
**License:** Apache-2.0 (API). README badge says dual-licensed "MIT OR Apache-2.0" at your option.
**Latest release:** unknown (release tags use `ironclaw-vX.Y.Z`; no release version verified).

## Models / providers / free usage / BYOK

- **Providers:** any LLM via `ironclaw models set-provider <route> --model <model>`; README example uses OpenAI (`gpt-5-mini`) and Google OAuth (`google.client_id/client_secret`) settings. Onboarding prompts for provider + API key in hidden prompt — i.e. **BYOK**.
- **Free usage:** no free model/inference documented — user supplies own API key.
- **Local inference:** not documented in README (unknown whether local LLM backends like Ollama are supported).
- Browser automation / computer use: **none documented** in README (no computer-use, screen-control, or browser-agent feature listed).

## Persistent memory design

- **Yes — workspace + hybrid search.** Workspace filesystem (path-based storage for notes/logs/context); hybrid search = full-text + vector search with Reciprocal Rank Fusion; "Identity Files" keep personality/preferences across sessions; Web Gateway UI has a memory view.

## Proactive behavior / scheduled tasks / background execution / goal tracking

- **Routines Engine:** cron schedules, event triggers, webhook handlers for background automation.
- **Heartbeat System:** proactive background execution for monitoring/maintenance tasks.
- **Parallel Jobs:** multiple concurrent requests with isolated contexts; Scheduler manages parallel execution with priorities; Self-repair (detect/recover stuck operations).
- Goal tracking: **none** documented.

## Browser automation, computer use, file ops, terminal access

- No browser automation / computer use in README.
- File ops: Workspace filesystem tool access implied (path-based storage).
- Terminal access: REPL (`ironclaw repl`), one-shot `ironclaw run --message`, Docker-sandboxed isolated execution with per-job tokens and orchestrator/worker pattern (parallel jobs run in Docker containers).

## Integrations, APIs, plugins, MCP, messaging channels

- **MCP Protocol:** connects to Model Context Protocol servers.
- **Plugin architecture:** drop-in WASM tools and channels without restarting.
- **Dynamic Tool Building:** describe a tool, IronClaw builds it as a WASM tool on the fly.
- **Channels:** REPL, HTTP webhooks, WASM channels (Telegram, Slack; docs mention Discord too), Web Gateway (browser UI w/ SSE+WebSocket streaming).

## Multi-agent orchestration

- Orchestrator + in-proc local workers + Docker-sandboxed containers ("Worker / CC"); parallel jobs with isolated contexts. Multi-agent in the worker-farm sense; no documented inter-agent delegation framework — partial/unknown.

## Voice / image / document / multimodal

- **None documented** in README (no voice, image-gen, document-processing capabilities listed).

## Install complexity / hardware / hosting / maintenance

- **Install:** one-line installer script (macOS/Linux/WSL), Windows MSI or PowerShell; guided `ironclaw onboard`; background service auto-installed+started on macOS/Linux. Prebuilt binaries on Releases page. Source build needs Rust 1.96+ and Node.js 22+ w/ pnpm.
- **Hardware:** unknown — no minimum specs documented; own machine hosts it.
- **Hosting cost:** self-hosted on user's machine; $0 infra + BYOK model bills.
- **Maintenance:** single-binary service, `ironclaw service restart` after config changes; PostgreSQL persistence (`createdb ironclaw_test` in dev) implies a local Postgres install — moderate operational burden vs SQLite-based peers.

## Security — privacy architecture (project's headline focus)

- **Local-first:** all data stored locally in app state; no telemetry/analytics/data sharing; full audit log of tool executions.
- **Secrets:** AES-256-GCM encrypted local secret store; secrets never accept positional args (hidden prompts); secrets never exposed to tools — injected at host boundary; leak detection scans requests/responses.
- **WASM sandbox:** untrusted tools run in isolated WebAssembly containers with capability-based permissions (opt-in HTTP, secrets, tool invocation), endpoint allowlisting (HTTP only to approved hosts/paths), rate limiting, memory/CPU/time resource limits.
- **Prompt injection defense:** pattern detection, content sanitization/escaping, severity policy rules (Block/Warn/Review/Sanitize), tool-output wrapping for safe LLM context injection.
- Docker sandbox with per-job tokens for execution jobs. README diagrams the credential-injection + leak-scan pipeline explicitly.

## Top 3 strengths / weaknesses / best lesson

**Strengths:**
1. Strongest privacy/security posture among agent-OS competitors (local-first, WASM capability sandbox, encrypted secrets, injection defense, no telemetry) — a genuine differentiator.
2. Rust single-binary + PostgreSQL: memory-safe, fast, production-grade persistence.
3. Self-expanding runtime (dynamic WASM tool building + MCP + hot-drop plugins) plus mature background automation (routines, heartbeat, parallel jobs).

**Weaknesses:**
1. BYOK-only: no free tier, no documented free/local inference path — real onboarding cost vs "free assistant" expectations.
2. No browser automation/computer-use and no multimodal (voice/image/document) in README — narrows the "Agent OS" claim.
3. Open issue load: 1,552 open issues on 12.6k stars — velocity or triage debt; FEATURE_PARITY.md implies still catching up to OpenClaw.

**Best lesson to steal:** Host-boundary credential injection with bidirectional leak scanning — secrets never enter tool/WASM context; the WASM→Allowlist→LeakScan→CredentialInjector→Execute→LeakScan pipeline is the cleanest sandbox pattern documented here and directly applicable to any tool-running agent.

## Scores (1-10, evidence per score)

1. **Intelligence/model flexibility — 6:** BYOK provider routing (`models set-provider`), any model selectable; no evidence of local/free inference or model-switching smarts.
2. **Persistent memory — 7:** Workspace filesystem + hybrid full-text/vector (RRF) search + identity files; no documented episodic/goal memory.
3. **Autonomous execution — 7:** Routines (cron/events/webhooks), heartbeat, parallel isolated jobs, self-repair — strong, but no goal-tracking.
4. **Proactive assistance — 5:** Heartbeat system + routines are the proactive mechanism; README gives no example of initiative beyond monitoring/maintenance.
5. **Browser/computer control — 1:** none documented.
6. **Integrations/extensibility — 8:** MCP servers, hot-drop WASM plugins, dynamic tool building, Telegram/Slack/Discord/HTTP channels, WebUI extensions page.
7. **Privacy/security — 9:** local-only data, AES-256-GCM secrets, WASM capability sandbox, injection defense, no telemetry, audit log — the project's headline, documented in depth.
8. **Ease of deployment — 7:** one-line installer + guided onboard + auto background service on macOS/Linux; Windows needs MSI/foreground serve; PostgreSQL requirement is friction.
9. **Free-tier/local accessibility — 4:** self-hostable and open-source, but BYOK-only with no free inference documented; own hardware required.
10. **Reliability/observability — 6:** self-repair, audit log of tool executions, `ironclaw status`; no documented metrics/tracing/alerting beyond that.
11. **User experience — 6:** Web Gateway UI (chat, memory, jobs, logs, extensions, routines) + REPL; quality of UX unverified beyond README claims.
12. **Community health — 7:** 12.6k stars / 1.5k forks, pushed within hours of check (2026-10-18), active issue tracker (1,552 open — high ratio), nearai org backing, multi-language READMEs, Telegram/Reddit communities; PR/commit velocity not verified.

## Verdict

**Active.** Not stale, dead, renamed, or irrelevant — pushed 2026-10-18, 12.6k stars, healthy org backing. Worth keeping as the **privacy/security reference implementation** in the competitor set; strongest replacement for this niche is none — it *is* the strongest privacy-first agent-OS repo found here. If a BYOK-free, browser-capable alternative is needed instead, look outside this repo (no replacement repo verified in this evidence pass).
