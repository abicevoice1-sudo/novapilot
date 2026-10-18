# NousResearch/hermes-agent

- **Canonical URL:** https://github.com/NousResearch/hermes-agent (no redirect observed)
- **Category:** Self-improving personal AI agent with TUI + messaging gateway — "the agent that grows with you." Python, by Nous Research.

**Verification date:** 2026-10-18. Stats from saved API JSON: stars **254742**, forks **55389**, open issues **49856**, license **MIT**, primary language **Python**, last push **2026-10-18T05:12:30Z**, archived: **no**. ⚠️ Star count is implausibly high and 49,856 open issues suggests automated/issue-factory inflation; reported exactly as the API returned — treat as unreliable. Latest release: **v0.22.2** (2026-10-15, verified on releases page; "0.22.1 shipped unreleased gateway work" — disclosed mishap).

## Models / free / local / BYOK
- Provider-neutral: **Nous Portal**, OpenRouter, OpenAI, custom endpoint — switch with `hermes model`, no code changes. **Nous Portal** (optional subscription): one OAuth login for 300+ models + Tool Gateway (web search, FAL image gen, OpenAI TTS, cloud Browser Use). Free onramp: **free trial model** (`nous/welcome`) in guided setup. **Local:** one-click llama.cpp runtime installs/maintains engine per hardware (CPU/CUDA/Metal/Vulkan/ROCm), rates catalog models vs. GPU/RAM. Long local-model turns engineered to survive laptop sleep.

## Memory (the standout)
- **Closed learning loop**: agent-curated memory with **periodic nudges** to persist knowledge; **autonomous skill creation** after complex tasks; **skills self-improve during use**; FTS5 session search + LLM summarization for cross-session recall; **Honcho dialectic user modeling**; agentskills.io open standard; Skills Hub. 600-plugin catalog.

## Proactive / scheduling / background / goals
- **Built-in cron scheduler with delivery to any platform** — daily reports, nightly backups, weekly audits in natural language, unattended. `/insights` command for usage review.

## Browser / computer / files / terminal
- **Seven terminal backends**: local, Docker, SSH, Singularity, Modal, Daytona, Vercel Sandbox; serverless persistence (hibernate when idle, wake on demand) — "$5 VPS or GPU cluster."
- Browser: cloud browser via Nous Tool Gateway (Browser Use); desktop "bot screen you can take over"; community `computer-use-linux` MCP (AT-SPI, Wayland/X11, screenshots). Password-manager sign-in for the browser.

## Integrations / APIs / plugins / MCP / messaging
- **Messaging**: Telegram, Discord, Slack, WhatsApp, Signal, Email, Home Assistant — one gateway process. **Connectors**: agent acts inside hosted apps (Linear, Notion) via tool gateway — sign in once in browser. **MCP**: connect any server; plugin catalog 600. Voice memo transcription. **Migration**: `hermes claw migrate` imports OpenClaw's SOUL.md, memories, skills, allowlists, API keys.

## Multi-agent
- Spawn **isolated subagents for parallel workstreams**; delegation ledger with fenced receipts (v0.22.1 release notes); batch trajectory generation (research-oriented).

## Voice / image / documents / multimodal
- Voice memo transcription; TTS + image generation (FAL) via Tool Gateway; cross-platform conversation continuity.

## Install / hardware / cost / maintenance
- One-liners: `curl …/install.sh | bash` (Linux/macOS/WSL2), PowerShell script (native Windows), signed APT for Termux aarch64, signed desktop packages + **Microsoft Store**. `hermes setup` wizard, `hermes doctor`, `hermes update`. Runs on $5 VPS; serverless backends cost ~nothing idle. Maintenance: large contributor base (~2,520 contributors claimed in v0.22.0 notes), release lanes, smoke tests.

## Security / privacy
- Command approval, DM pairing, container isolation, **safe workers** (isolated, no memory readers, no plugin providers), session-authority admission controls, canonical attachment admissions, per-profile bot relay, frozen session manifests, read-only host checks. Local models = nothing leaves the machine.

## Top 3 strengths
1. **Closed learning loop** — autonomous skill creation + self-improving skills + nudges + user modeling is the most complete learning-memory design anywhere in this batch.
2. Best local-model story: one-click llama.cpp runtime, hardware-rated model picks, laptop-surviving long turns.
3. Radical changelog honesty (wrong-commit release disclosed with known issues) + `claw migrate` (strategic onboarding from a competitor).

## Top 3 weaknesses
1. Enormous scope (600 plugins, 7 backends, messaging × 7) — release mishaps (v0.22.1) show the strain; reliability risk.
2. Nous Portal adds an optional subscription layer — the "free forever" story depends on Nous's funding.
3. Issue tracker is unusable as a signal (49,856 open issues); real community health can't be judged from metrics.

## Best lesson to steal
**Autonomous skill creation + periodic nudges**: procedural learning as skills the agent writes, self-improves, and periodically refreshes — memory as a self-improving artifact, not a flat store. Plus the `hermes doctor`/`claw migrate` onboarding pattern.

## Scores (1–10, evidence)
1. Intelligence/model flexibility: **8** — provider-neutral + 300 models via optional portal + local llama.cpp.
2. Persistent memory: **9** — learning loop, skill creation/self-improvement, FTS5 recall, Honcho modeling; strongest in batch.
3. Autonomous execution: **8** — cron delivery anywhere, subagents, serverless persistence.
4. Proactive assistance: **8** — natural-language scheduled automations + platform delivery.
5. Browser/computer control: **7** — 7 terminal backends, cloud browser, take-over screen; desktop control via MCP.
6. Integrations/extensibility: **9** — 7 messaging platforms, connectors, 600-plugin catalog, MCP.
7. Privacy/security: **7** — approvals, pairing, safe workers, isolation; gateway complexity is risk.
8. Ease of deployment: **8** — one-liners all OSes, Store package, setup wizard, doctor.
9. Free-tier/local accessibility: **8** — one-click local models, free trial; portal optional.
10. Reliability/observability: **6** — release lanes + smokes, but shipped-wrong-commit incident and scope risk.
11. User experience: **8** — TUI, personalities, guided setup chat, usage insights.
12. Community health: **7** — big contributor base and Discord; issue metrics unreliable.

## Verdict
**Active** (v0.22.2, pushed today). Keep — the closest to the full vision (learning memory + gateway + cron + local models) and the primary architecture reference for NOVA. Replacement if dropped: openclaw/openclaw (gateway/channels) — though hermes already migrates from it.
