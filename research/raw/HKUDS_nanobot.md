# HKUDS/nanobot — competitor research

- Canonical URL: https://github.com/HKUDS/nanobot
- Category: Ultra-lightweight, open-source, self-hosted personal AI agent framework in Python (WebUI + TUI + chat-app gateway).

## Verification
- Verification date: 2026-10-18.
- Stars: 49,141 | Forks: 8,639 | Open issues: 866 | License: MIT | Language: Python
- Created: 2026-02-01 | Last push: 2026-10-17T19:40:29Z | Archived: false | Homepage: https://nanobot.wiki
- Latest release: "unknown" (not verified via API; README mentions v0.3.5 released 2026-09-15).

## Models / providers / cost model
- Any OpenAI-compatible API provider; model fallbacks supported; provider cookbook + recipes in docs.
- Local inference: Ollama, vLLM, or any OpenAI-compatible local server. Open Source Partners: Kimi (Moonshot), MiniMax; Render blueprint asks for ANTHROPIC_API_KEY.
- BYOK only: "nanobot does not supply a model account." No free tier bundled. Framework itself is free; hosting + model fees are the user's.

## Persistent memory
- Session history + long-term memory via "Dream": `/compact` then `/dream` consolidates preferences into `USER.md` / `memory/MEMORY.md` markdown files in the agent workspace (human-readable, diffable).
- Context compaction visible in conversation timeline; one shared memory/agent profile per instance (separate instances for client isolation); Temporary chats excluded from history/memory.

## Proactive behavior / scheduling / background execution / goals
- Scheduled Automations (cron-like, Tasks + Calendar views in WebUI); `/goal` for long-running bounded goals across model turns while gateway runs; `nanobot gateway --background` detaches; OS services (Docker/Compose, systemd, LaunchAgent) for persistence.
- Reliability gaps (stated in README): missed scheduled times are NOT replayed after a gateway restart; interrupted subagent tasks are NOT auto-relaunched after restart.
- Proactive nudging beyond cron: none evident.

## Browser / computer use / file ops / terminal
- Shell tool, web search/fetch, full file ops (reads PDF/DOCX/XLSX/PPTX; writes files, diffs) within project workspaces with access modes (e.g. Restricted).
- Terminal: native TUI + one-shot CLI + OpenAI-compatible HTTP API. No browser automation or computer-use (screen/GUI) agent in README.

## Integrations / MCP / messaging
- MCP: built-in Apps catalog of MCP server presets + custom servers; Agent Plugins; local CLI App adapters; Skills; Python SDK; OpenAI-compatible API (`/v1/chat/completions`); Langfuse support mentioned.
- Chat channels: Telegram, Discord, WeChat/WeCom, Slack, Email, Mattermost, Linear, Teams, Feishu (DM pairing/allowlist + group-access policies documented).

## Multi-agent
- Multi-agent delegation / subagents supported (subagent recovery docs referenced); coordination across sessions via `@` mentions.

## Voice / image / document / multimodal
- Voice and image-generation settings in WebUI/TUI; image generation built in; paste clipboard images (Ctrl+V) in TUI; attach files to conversations; built-in PDF/Word/Excel/PowerPoint readers.

## Install / hardware / cost / maintenance
- Install: one-line `curl|sh` / `irm|iex` installer, or `uv tool install nanobot-ai` / `pip install nanobot-ai`; Python ≥3.11; guided WebUI wizard; beginner no-terminal guide; wheels for macOS/Windows/Linux.
- Hardware: framework is lightweight; local LLM hardware is user's burden (BYOK/Ollama/vLLM).
- Hosting: self-host free (Render one-click needs paid persistent disk); maintenance = keep gateway + OS service + model credentials alive.

## Security / privacy
- Self-hosted, local session/memory storage; workspace access modes (Restricted); chat-channel DM pairing/allowlist; WebUI login-link token.
- Gaps: WebUI access = full admin ("share it only with trusted operators"); no documented per-tool-call approval workflow in README; no strong sandbox beyond folder access modes.

## Strengths (top 3)
1. Massive traction: 49k stars, 8.6k forks, 200+ contributors, pushed yesterday — the dominant lightweight agent framework.
2. Model freedom: any OpenAI-compatible provider + Ollama/vLLM local + fallbacks; BYOK, no lock-in.
3. Chat-native reach + bundled clients: WebUI + TUI + gateway to Telegram/Discord/Slack/WeChat/Email/etc. in one small Python core.

## Weaknesses (top 3)
1. Young and reliability-gapped: created 2026-02-01; missed schedules not replayed; subagent tasks not auto-relaunched after restart.
2. Thin safety model: no documented approval workflow; WebUI token equals full admin.
3. No real proactive loop or computer-use: automations are cron only; no browser/GUI control; "current source" vs stable docs can drift.

## Best lesson to steal
- Dream-based memory consolidation: `/compact` + `/dream` → durable preferences written as markdown (`USER.md`, `memory/MEMORY.md`) — human-readable, version-controlled memory instead of an opaque vector store.

## Scores (1–10)
1. Intelligence/model flexibility: 8 — any OpenAI-compatible provider, Ollama/vLLM, model fallbacks, image generation.
2. Persistent memory: 8 — Dream consolidation to USER.md/MEMORY.md, compaction, shared instance memory.
3. Autonomous execution: 6 — shell/file ops/subagents/goals, but no auto-relaunch after restart, no missed-schedule replay.
4. Proactive assistance: 4 — cron automations only; no proactive nudging or agenda behavior evidenced.
5. Browser/computer control: 3 — shell + web fetch only; no browser automation or GUI computer use.
6. Integrations/extensibility: 8 — MCP presets + custom, Agent Plugins, Python SDK, OpenAI-compatible API, Skills, Langfuse, 10+ chat channels.
7. Privacy/security: 6 — self-hosted, local storage, Restricted access modes; but no approval workflow and token = full admin.
8. Ease of deployment: 8 — one-line installer, pip/uv/pipx, Render one-click, Docker/systemd/LaunchAgent guides.
9. Free-tier/local accessibility: 7 — no bundled model/free tier (BYOK); local inference fully supported via Ollama/vLLM.
10. Reliability/observability: 6 — CI badge, gateway logs/status, context-usage UI; undermined by documented no-replay reliability gaps.
11. User experience: 8 — polished WebUI + TUI workbench, multi-pane topics, 11-language docs, beginner wizard.
12. Community health: 9 — 49k stars / 8.6k forks / 866 open issues, push on 2026-10-17, 2 named maintainers, active Discord/X/WeChat.

## Verdict
- Verdict: **active** — worth keeping as the primary lightweight-agent benchmark. Keep watching for its memory ("Dream") design, chat-channel gateway architecture, and the small-core + MCP-plugin pattern. Note: repo topics tag "openclaw", suggesting openclaw lineage/inspiration — cross-check OpenClaw research for overlap. No replacement repo needed.
