# Competitor Research: agent0ai/agent-zero

- Canonical URL: https://github.com/agent0ai/agent-zero
- Redirect/rename observed: none. Related sibling repos: agent0ai/space-agent (described in README as "the related, more polished product direction"; Agent Zero "remains the open framework"), agent0ai/a0-launcher, agent0ai/a0-install. Docs site: https://agent-zero.ai
- Category: Open-source personal AI assistant / agentic framework with a full Linux computer (Dockerized XFCE desktop, native browser, live document cowork).

## Verification

- Verification date: 2026-10-18
- Stats: unknown — saved GitHub API JSON (`~/workspace/nova-agent/research/raw/agent0ai_agent-zero.json`) contained ONLY a rate-limit error ("API rate limit exceeded"; authenticated requests advised). No star/fork/issue counts are stated in the README either.
- License: unknown (SPDX not stated anywhere in the README).
- Primary language: Python (per a third-party framework listing; README implies Python via `prompts/`/`tools/` dirs but does not state it explicitly).
- Archived: no. README: "Agent Zero remains the open framework and Linux-powered workbench." Docs site lists v2.14 (startup/prompt-cache release) and v2.13 (file browser, project folders, slash commands) ~25 days ago — actively released.
- Latest release: unknown per GitHub API (rate-limited); docs site documents v2.14 as the newest.

## Models / Providers / Cost

- Provider-agnostic via "Model Presets" (named shortcuts: fast, balanced, cheap, local, high-power). You configure your LLM provider in the Web UI — BYOK model.
- OpenAI Codex plan connectable through OAuth device-code flow (first "account-backed LLM plan"; Gemini CLI / Claude Code "extra-usage" plans listed as coming).
- Local inference: yes — "local" model presets and local/self-hosted models via configurable presets (README).
- Free usage: framework itself free (Docker image, CLI tools, no licensing fee); you pay only for LLM API usage. Runs from a ~$6 VPS or Raspberry Pi to a workstation/GPU server.

## Persistent Memory

- Yes. **Projects** isolate workspaces, instructions, **memory**, secrets, knowledge, repos, and model-preset choices.
- A Memory guide (`docs/guides/memory.md`) documents managing/curating memories; Plugin Hub offers alternative memory backends, intelligent consolidation strategies, and vector-recall plugins.
- No dedicated long-term knowledge-base/graph beyond project-scoped memory + plugins.

## Proactive Behavior / Scheduled Tasks / Background Execution / Goal Tracking

- Scheduled operations: yes — "run recurring checks and monitoring tasks with project-scoped context and credentials"; scheduler and project-automation plugins in the Plugin Hub.
- Background execution: yes — Docker container runs continuously; subagents execute delegated tasks asynchronously.
- Time Travel: snapshot history, diff inspection, and revert for Agent Zero-owned `/a0/usr` workspaces (practical safety layer, not a Git replacement).
- Goal tracking: none documented — no goal/objective tracker in the README. Proactive assistant loop (reminders, notification channels) is thin: "slash commands for messaging integrations" appear in v2.13 release notes and messaging plugins were security-hardened in v2.12, but no always-on proactive assistant pattern is described.

## Browser / Computer / File / Terminal

- Browser automation: built-in native browser with **DOM annotation mode** — click an element to Change (JS instruction applied + verified), Inspect, Lift (re-implement component in your stack), or Comment (pinned UI-review notes the agent fixes). Browser history keeps screenshots; Chrome extensions supported; "Bring Your Own Browser" via the A0 CLI Connector drives host Chrome/Edge/Brave/Opera/Vivaldi/Chromium. Standard automation, not detection-evasion (per third-party FAQ).
- Computer use: full XFCE Linux desktop rendered in the right-side Canvas; agent drives real GUI software (README shows it driving Blender); user shares mouse/keyboard on the same desktop.
- File ops: redesigned file browser/editor with project folders, live Markdown editor cowork (agent + user edit the same doc simultaneously), LibreOffice Writer/Calc/Impress cowork (ODT/ODS/ODP first-class).
- Terminal: embedded terminals, full Linux terminal in the container, and the A0 CLI Connector bridges the instance to the host machine (opt-in, controlled; install on the host, not in the container).

## Integrations / APIs / Plugins / MCP / Messaging

- Plugin Hub: 100+ community plugins (BMAD Method dev lifecycle, memory backends, terminals, custom browsers, deployment helpers, UI extensions, schedulers, multi-agent orchestration).
- MCP: yes — MCP setup guide (`docs/guides/mcp-setup.md`); custom tools in `tools/`, custom prompts in `prompts/`.
- A2A connectors supported. Project-scoped configuration; environment-based deployment settings.
- Messaging: slash commands for messaging integrations (v2.13) + messaging plugins (security-hardened in v2.12); specific channels (Telegram/Discord/etc.) not enumerated in the README.

## Multi-Agent Orchestration

- Yes — hierarchical multi-agent cooperation: every agent can create subordinate agents; the superior assigns tasks and receives reports; subagents keep focused contexts. Used for research, coding, analysis, review, plugin dev.

## Voice / Image / Multimodal

- Voice: none documented in the README.
- Image/vision: browser screenshots + history, "vision sidecars" (v2.11), context-usage indicator.
- Documents: strong — live Markdown cowork + full LibreOffice suite cowork.

## Install Complexity / Hardware / Cost / Maintenance

- Install: easiest path is the A0 Launcher (desktop app that checks Docker, creates instances, manages ports); terminal path is one-line A0 Install (`curl | bash`) or a single `docker run -p 80:80 -v a0_usr:/a0/usr agent0ai/agent-zero`. Low-medium complexity, but Docker is a hard prerequisite.
- Hardware: anything Docker runs on — $6 VPS, Raspberry Pi, local workstation, GPU server.
- Hosting cost: ~$6/mo minimum VPS + whatever you spend on LLM APIs; data persists across updates in the `/a0/usr` volume.
- Maintenance: re-run installer or pull latest Docker image to update; projects/secrets/data persist in the mounted volume. Self-managed — no SaaS layer.

## Security

- Primary isolation: Docker container. Safety Model section: keep it inside Docker; do NOT mount your entire home directory; grant A0 CLI Read+Write + remote code execution only to trusted machines; store credentials in **project secrets** or settings, never in prompts/public files; review actions touching accounts, money, production systems, private data; keep backups of important workspaces.
- Transparency: prompts, tools, plugins, skills, settings all inspectable/editable; Time Travel snapshots give recoverability. Security posture is "transparent + container-isolated, but relies on user discipline" — no formal approval-workflow engine or sandboxed per-action policy documented in the README.

## Strengths / Weaknesses / Lesson

- Top 3 strengths:
  1. Deepest "give your agent a real computer" implementation — full XFCE desktop + terminal + real GUI apps in Docker, not a sandboxed tool loop.
  2. Novel cowork UX — DOM annotation mode and live document/spreadsheet cowork turn the browser and files into interactive directive surfaces.
  3. Transparent, extensible core — 100+ plugin ecosystem, MCP, A2A, inspectable prompts/tools, project-scoped isolation of memory/secrets/models.
- Top 3 weaknesses:
  1. Docker is mandatory — install/ops friction (VPS, port management) versus zero-install agents.
  2. No documented goal tracking or proactive assistant loop — it's a workbench you drive, not an always-on companion.
  3. Safety is user-discipline-based; browser automation is standard (not stealth), so login/anti-bot friction stays on the user.
- Best lesson to steal: **Annotate-mode cowork + Time Travel safety layer** — make the browser and documents interactive directive surfaces (click/annotate → instruction) instead of trapping everything in chat, and wrap all agent file work in a visible snapshot/diff/revert safety net.

## Scores (1-10, one line of evidence each)

1. Intelligence/model flexibility: 8 — provider-agnostic Model Presets (fast/balanced/cheap/local/high-power) + Codex OAuth plans; BYOK required (README).
2. Persistent memory: 7 — project-scoped memory with curation guide + vector-recall/consolidation plugins; no higher goal layer (README).
3. Autonomous execution: 8 — full Linux desktop + terminal + scheduled ops + subagents in Docker; safety model warns to review money/production actions (README).
4. Proactive assistance: 5 — schedulers/scheduled operations exist, but no proactive notification/goal-tracking loop documented (README).
5. Browser/computer control: 9 — real XFCE desktop + DOM-annotating browser + BYOB host browsers; standard automation, not stealth (README).
6. Integrations/extensibility: 9 — 100+ Plugin Hub, MCP, A2A, custom tools/prompts, project-scoped config (README).
7. Privacy/security: 6 — Docker isolation + project secrets + Time Travel, but safety relies on user discipline (README).
8. Ease of deployment: 7 — guided A0 Launcher and one-line Docker run, but Docker + self-managed host required (README).
9. Free-tier/local accessibility: 8 — framework free, runs on $6 VPS/Raspberry Pi, local-model presets; pay only for LLM API (README).
10. Reliability/observability: 6 — Time Travel snapshots/diff/revert + transparent prompts/tools + browser history screenshots; no formal eval/observability story (README).
11. User experience: 8 — Canvas cowork (Markdown editor, LibreOffice, annotations, Time Travel) is best-in-class agentic UX; guided Launcher (README).
12. Community health: 7 — GitHub Issues, Discord, Skool, YouTube, X/LinkedIn/Warpcast, GitHub Sponsors, DeepWiki, frequent releases (v2.11–v2.14 on docs site); GitHub stats unknown (API rate-limited).

## Verdict

**Active** — clearly under active development (v2.13/v2.14 within ~a month per docs site; Plugin Hub growing past 100). Not archived, not renamed. Keep as the primary benchmark for agent computer-use and cowork UX. No stronger replacement repo identified; it is the reference implementation in its niche.
