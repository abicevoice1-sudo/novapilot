# openclaw/openclaw

- **Canonical URL:** https://github.com/openclaw/openclaw (no redirect observed)
- **Category:** Open-source AI assistant **gateway** — runs on your own hardware and meets the user in 20+ messaging channels plus native apps.

**Verification date:** 2026-10-18. Stats from saved API JSON: stars **392306**, forks **82464**, open issues **9375**, license **MIT**, primary language **TypeScript**, last push **2026-10-18T05:30:30Z**, archived: **no**. ⚠️ The star count is implausibly high (and 9375 open issues vs. that count is a mismatch); treat the ranking with caution — reported exactly as the API returned. Latest release: **2026.10.4** (calver, verified via npm registry).

## Models / free / local / BYOK
- Models and agent harnesses (Claude, Codex, **local models**) are swappable plugins; per-session model override. No paid tier, no hosted service, no token (501(c)(3) Foundation-stewarded).

## Memory
- Built-in memory tools (`memory_search`, `memory_get`) in the `group:memory` tool group; workspace memory conventions (MEMORY.md/SOUL.md pattern). State lives on the user's hardware.

## Proactive / scheduling / background / goals
- **`cron` tool** ("manage scheduled jobs") + `heartbeat_respond` in the `group:automation` tool group; scheduled/automation work via the local Gateway daemon.

## Browser / computer / files / terminal
- **`browser` tool**: controls Chromium (navigate, click, screenshot) — in `group:ui`; deliberately opt-in under the `coding` profile (`tools.alsoAllow: ["browser"]`) since it can drive real logged-in sessions.
- **`exec`/`process`**: shell commands + background processes; **`code_execution`**: sandboxed remote Python analysis. File I/O: read/write/edit/apply_patch in workspace.

## Integrations / APIs / plugins / MCP / messaging
- **Channels**: Discord, iMessage, Slack, Teams, Telegram, WhatsApp, Google Chat, Signal, 20+ more; companion apps/nodes (voice, Canvas, camera, screen, device actions); Control UI, CLI, TUI.
- **Web**: `web_search`, `x_search` (X posts), `web_fetch`.
- **Media**: image analyze/generate, music generate, video generate, TTS — via plugins (ComfyUI, fal, Google, etc.).
- **Extensibility**: plugins (npm packages) via SDK + **ClawHub** marketplace; **skills** (SKILL.md) injected into system prompt; bundled **MCP tools** under `bundle-mcp`.

## Multi-agent
- Yes: `sessions_*` tools, `subagents`, `agents_list`, per-agent tool profiles — spawn and orchestrate subagents within session groups.

## Voice / image / documents / multimodal
- Full media surface: speech, realtime transcription, realtime voice, media understanding, image/music/video generation, TTS, camera/screen via device nodes.

## Install / hardware / cost / maintenance
- `curl -fsSL https://openclaw.ai/install.sh | bash` or `npm install -g openclaw` (Node 24.16+/26); `openclaw onboard --install-daemon`; Docker/Nix paths; team deployments supported. Maintenance: Foundation-employed core team, donor-funded; docs at docs.openclaw.ai.

## Security / privacy
- **"Trusted gateway, untrusted execution, policy enforced by code"**: per-tool allow/deny lists (`tools.allow`/`tools.deny`, deny wins, **fail-closed** on empty allowlist); per-agent tool **profiles** (full/coding/messaging/minimal); `exec` approvals (`tools.exec.ask`); configurable sandboxing — but **tools run on the host by default** unless sandboxed. DM pairing approval for unknown senders; inbound messages treated as untrusted; secrets stay on hardware; telemetry is one daily version check (opt-in stats); SECURITY.md + exposure runbook.

## Top 3 strengths
1. Widest practical surface in this batch: 20+ channels, media generation, plugins + ClawHub, MCP, nodes — a complete personal-assistant OS.
2. **Policy-as-code permission model**: tool profiles + allow/deny with fail-closed semantics per agent — the best least-privilege tooling here.
3. Governance: independent 501(c)(3) Foundation, no token, no paid tier — credible neutrality.

## Top 3 weaknesses
1. Metrics look gamed (392k stars vs 9,375 open issues); community health is hard to assess honestly.
2. Default exec-on-host is a large attack surface; real safety depends on the user configuring sandboxing.
3. Enormous scope (channels × media × plugins) raises maintenance and supply-chain review burden.

## Best lesson to steal
**Per-agent tool profiles with fail-closed allowlists** (full/coding/messaging/minimal + `alsoAllow` for sensitive tools like browser) — the concrete least-privilege mechanism every personal agent needs.

## Scores (1–10, evidence)
1. Intelligence/model flexibility: **8** — swappable provider plugins, per-session model override.
2. Persistent memory: **7** — built-in memory tools + local workspace files.
3. Autonomous execution: **7** — exec/process, cron automation, subagents.
4. Proactive assistance: **7** — cron + heartbeat automation; learned proactivity unknown.
5. Browser/computer control: **7** — Chromium control, exec, sandbox option; browser opt-in.
6. Integrations/extensibility: **9** — 20+ channels, ClawHub plugins, skills, MCP bundles.
7. Privacy/security: **7** — policy-as-code, fail-closed, pairing approvals; host-exec default.
8. Ease of deployment: **8** — one-line installer, npm package, onboarding wizard.
9. Free-tier/local accessibility: **7** — free software, runs on own hardware; models are BYOK-cost.
10. Reliability/observability: **6** — CI, session tools, token counters; scale complexity is risk.
11. User experience: **8** — Control UI, TUI, native apps, 20+ channels where the user lives.
12. Community health: **7** — foundation, Discord, donors; star metric unreliable, issue backlog huge.

## Verdict
**Active** (pushed today, calver releases). Keep — the permission-profile model and ClawHub marketplace are the two ideas to adopt. Replacement if dropped: NousResearch/hermes-agent (gateway + channels overlap, plus learning loop).
