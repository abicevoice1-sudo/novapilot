# PicoClaw — sipeed/picoclaw — Competitor Evidence

- **Canonical URL:** https://github.com/sipeed/picoclaw (no redirect/rename observed). README warns the ONLY official domain is picoclaw.io (README).
- **Category:** Ultra-lightweight personal AI assistant / agent runtime written in Go, designed for cheap embedded hardware (README).

## Verification status
- Verification date: 2026-10-18.
- **Stats: unknown — GitHub API rate-limited at check time** (saved JSON contains only a rate-limit error). Do NOT trust any star/fork/issue counts. (README itself claims "26K Stars" as of 2026-03-25 in its news feed — self-reported, unverifiable today.)
- **License:** MIT (badge in README).
- **Primary language:** Go (1.25+ required to build) (README).
- **Archived?** Unknown (no documentation of archival; repo shows active releases in README news).
- **Latest release:** unknown. (README's newest dated entry is v0.2.9 on 2026-05-28.)

## Models / providers / cost
- 30+ LLM providers via `model_list` (protocol/model format), all BYOK API keys: OpenAI, Anthropic, Google Gemini, OpenRouter, Zhipu, DeepSeek, Volcengine, Qwen, Groq, Moonshot/Kimi, Minimax, Mistral, NVIDIA NIM, Cerebras, NEAR AI, Novita, Xiaomi MiMo, LiteLLM; OAuth: GitHub Copilot, Antigravity; AWS Bedrock and Azure (build tags / Entra ID) (README providers table).
- **Local inference:** Ollama and vLLM supported, no API key needed (README config examples).
- **Rule-based model routing:** simple queries routed to lightweight models to save API costs (README features).
- **Free usage:** core is MIT; intelligence is BYOK (you pay the provider). Web search engines include free tiers: DuckDuckGo (built-in, unlimited), Brave (2000/mo), Tavily (1000/mo), Baidu (1500/mo), SearXNG self-hosted (README tools table).

## Persistent memory
- None documented in depth. README v0.2.1 news mentions a "JSONL memory store"; demo table shows "Logging & Planning — Schedule · Automate · Remember". No memory architecture doc in README (README).

## Proactive behavior / scheduling / background
- `picoclaw cron add/list/disable/remove` — one-time reminders, recurring tasks, cron expressions (README CLI + docs/reference/cron.md).
- **Hooks:** event-driven system (observers, interceptors, approval hooks) (README + docs/architecture/hooks).
- **Steering:** inject messages into a running agent loop between tool calls (README).
- Gateway mode keeps the agent running for chat-app integration (README).
- Goal tracking: none documented.

## Browser / computer / file / terminal
- File ops and code execution tools built in (README "Other Tools"; `read_file` by lines noted in news).
- Web search tools with 9 engine options (README).
- Vision pipeline: images/files sent to the agent, auto base64-encoded for multimodal LLMs (README).
- **Browser automation: none documented.** "WebUI Launcher" is a config/chat UI on localhost:18800, not agent-driven browser control.

## Integrations / APIs / plugins / MCP / channels
- **Native MCP** (stdio, SSE, HTTP) with CLI management (`mcp add/list/test/edit/remove`) (README).
- **Skills:** modular SKILL.md capabilities, installable from ClawHub registry (`picoclaw skills install`) (README).
- **19+ messaging channels:** Telegram, Discord, WhatsApp, Weixin, QQ, Slack, Matrix, Delta Chat, DingTalk, Feishu/Lark, LINE, WeCom, VK, IRC, OneBot, MQTT, MaixCam, Pico, Pico Client (README channels table).
- ClawdChat.ai "agent social network" join via CLI (README).

## Multi-agent orchestration
- Yes: agent architecture overhaul (v0.2.4) — SubTurn, EventBus, async `spawn` tasks, sub-agent orchestration, `spawn_status` query (README news + docs/guides/spawn-tasks.md).

## Voice / image / documents / multimodal
- Vision pipeline (image/file input to multimodal LLMs) (README).
- Voice: none in core README; Sipeed wiki documents a PicoClaw Expansion Board (240×240 LCD, buttons, LEDs, speaker + voice output) for LicheeRV Nano — voice lives at hardware layer, not core (confirmed via wiki.sipeed.com search result).
- Document handling: file tools; depth unknown.

## Install / hardware / hosting cost / maintenance
- **Install (easy):** one-click precompiled binary from picoclaw.io (auto-detects platform), GitHub Releases binaries, Docker Compose, Android APK, or build from source (Go 1.25+, Node 22+ for WebUI) (README).
- **Yes — device-bound by design:** targets $10 hardware. Officially sold as LicheeRV-Claw on AliExpress (README news 2026-05-11); documented deployments: $9.90 LicheeRV-Nano, $30–100 NanoKVM (server ops), $50–100 MaixCAM (surveillance), old Android phones (APK or Termux), Raspberry Pi Zero 2 W, plus desktop/server. Single binary across RISC-V, ARM64, MIPS, x86 (README). Confirmed on Sipeed wiki: dedicated PicoClaw Expansion Board with LCD/speaker for LicheeRV Nano.
- **Resource footprint:** claims <10MB RAM, <1s boot on 0.6GHz single core; README's own security note admits recent builds use 10–20MB due to rapid PR merges (README).
- **Hosting cost:** near-zero for the runtime (a $10 board or existing device); intelligence costs = your LLM API keys (BYOK) or self-hosted Ollama/vLLM (needs bigger hardware). No cloud bill from the project itself.
- **Maintenance burden:** user maintains own device/config/keys; project warns "early rapid development… do not deploy to production before v1.0" (README).

## Security
- `.security.yml` separate secrets file: config v1 auto-migrates sensitive codes out of `config.json` (README Terminal Launcher section).
- v0.2.4 security hardening: `.security.yml`, sensitive data filtering (README news).
- Cron security gating; approval hooks; security sandbox referenced in configuration docs (README news + docs).
- README explicitly warns of unresolved security issues in early development — honest but low assurance (README Security Notice).

## Top 3 strengths
1. **Extreme edge efficiency:** single Go binary, ~8MB, <1s boot, runs on $10 RISC-V boards — the agent runtime is decoupled from inference hardware (README + Sipeed wiki).
2. **Provider + channel breadth:** 30+ LLM providers with cost-saving routing, local Ollama/vLLM, native MCP, ClawHub skills, 19+ chat channels (README).
3. **Low-friction UX:** WebUI launcher, Android APK, `picoclaw onboard` wizard, docs translated into 10 languages (README).

## Top 3 weaknesses
1. **Security maturity:** self-declared early development with unresolved security issues; "do not deploy to production before v1.0" (README).
2. **BYOK intelligence gap:** the $10-device story still needs a paid cloud API key (or a much bigger box for local models); no bundled free intelligence (README).
3. **Goal drift on own core promise:** memory already crept from <10MB to 10–20MB due to rapid PR merges (README's own caution note).

## Single best lesson to steal
Decouple the agent runtime from inference: a tiny orchestration binary + BYOK + rule-based model routing (cheap models for simple queries) makes "runs anywhere, costs almost nothing" achievable — and keep secrets in a separate `.security.yml`-style file from day one.

## Scores (1–10, one line of evidence each)
1. Intelligence/model flexibility: **9** — 30+ providers, Ollama/vLLM local, rule-based cost routing (README providers table).
2. Persistent memory: **4** — JSONL memory store named in news only; no memory architecture documented (README).
3. Autonomous execution: **7** — cron jobs, async spawn/sub-agents, hooks, exec and file tools (README CLI).
4. Proactive assistance: **5** — reminders, cron, event hooks/steering; no goal tracking documented (README).
5. Browser/computer control: **4** — file ops, code exec, web search; no browser automation documented (README).
6. Integrations/extensibility: **9** — native MCP + CLI, ClawHub skills, 19+ messaging channels (README).
7. Privacy/security: **4** — `.security.yml` secrets split, sensitive-data filtering, approval hooks, but self-reported unresolved security issues pre-v1.0 (README).
8. Ease of deployment: **8** — one-click binary from picoclaw.io, APK, Docker; source build needs Go 1.25 + Node 22 (README).
9. Free-tier/local accessibility: **7** — MIT, $10 hardware, Ollama local; intelligence still requires paid BYOK keys (README).
10. Reliability/observability: **4** — status/logs commands, log levels; no SLO/test evidence in README, self-declared early dev (README).
11. User experience: **7** — WebUI launcher, Android APK, onboarding wizard, 10-language docs (README).
12. Community health: **unknown** — API rate-limited; README claims 26K stars (2026-03-25), unverifiable today.

## Verdict
- **active** (per README: v0.2.9 released 2026-05-28, hardware product on AliExpress 2026-05-11, docs wiki live; live GitHub state unverifiable today due to rate limit).
- **Worth keeping** — strongest evidence in this research set for the edge/deployment extreme: single-binary, multi-arch, $10-hardware agent runtime.
- If the edge angle is out of scope, the strongest replacement for "full personal agent" coverage is **openclaw** (the TypeScript project PicoClaw positions itself against — richer ecosystem, heavier runtime).
