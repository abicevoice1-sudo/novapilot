# microsoft/autogen — research notes

- Canonical URL: https://github.com/microsoft/autogen
- Category: [framework/component] — multi-agent AI application framework (AgentChat, Core, Extensions). Not an end-user product.
- Verification date: 2026-10-18. Stats (from saved GitHub API JSON): 61,455 stars · 9,294 forks · 1,125 open issues · License: **CC-BY-4.0** (docs) / **MIT** (code, per LICENSE-CODE — dual licensing) · Primary language: Python (+ .NET) · Last push: 2026-10-16 · Archived: **flag false in API, but README displays an "Archived / no longer maintained" banner** directing all users to the successor Microsoft Agent Framework. Treat as deprecated: Microsoft states no bug fixes, security fixes, or support.

## What it provides as a building block
Layered multi-agent framework: Core API (message passing, event-driven agents, local/distributed runtime, cross-language .NET/Python), AgentChat API (opinionated two-agent chat / group-chat patterns), Extensions (model clients, code execution). AutoGen Studio (no-code GUI, explicitly "not production-ready") and Magentic-One (SOTA web/code/file multi-agent team demo). Successor is **microsoft/agent-framework** — any adoption should target the successor, not this repo.

## Models / providers / cost
- Model clients in Extensions: OpenAI, Azure OpenAI shown; docs reference other supported models (unverified here). BYOK inherently (user supplies keys).
- Free usage: framework free; model calls are user's cost. No local-inference documentation in README (unknown).
- AutoGen Studio is a local GUI prototype tool, not a service.

## Memory design
- Not documented in README beyond agent state; not a memory layer. None worth relying on.

## Proactive / scheduling / background
- None — distributed runtime exists (Core API) but no scheduler, cron, or proactive engine documented.

## Browser / computer / file / terminal
- Via Extensions: code execution extensions; README's headline integration is a **Playwright MCP server** giving an agent headless web browsing. Magentic-One bundles web browsing + code execution + file handling. Human-in-the-loop noted for AutoGen patterns generally, but the README emphasizes Studio's security note: not production-hardened.

## Integrations / MCP
- First-class MCP: `McpWorkbench` / `StdioServerParams` example in README. Cross-runtime interop (A2A + MCP) is cited as the successor framework's design goal.

## Multi-agent
- Core strength: AgentChat group chats, `AgentTool` (agents-as-tools orchestration), distributed event-driven runtime, .NET + Python interop. The original multi-agent research framework (Microsoft Research).

## Voice / image / document / multimodal
- Model-dependent; nothing specific in README.

## As a dependency: install / hardware / cost / maintenance
- `pip install "autogen-agentchat" "autogen-ext[openai]"` (Python 3.10+). No infra required beyond model keys. Maintenance: **dead** — archived by Microsoft, community-managed only, contributions limited to bug fixes; security patches explicitly not provided. 1,125 open issues will not be triaged by Microsoft.

## Security posture (embedding it)
- **Negative**: Microsoft's own README warns against production use and flags unpatched vulnerabilities as a risk "particularly when handling sensitive data". MCP usage carries the documented warning that servers may execute local commands or exfiltrate data. Prompt-injection posture not documented. Verdict on security alone: do not embed.

## Strengths / weaknesses / lesson
- Strengths: (1) Pioneered multi-agent conversation patterns (group chat, agents-as-tools) the whole field copied. (2) Clean layered design (Core → AgentChat → Extensions) with cross-language runtime. (3) Magentic-One showed a credible web+code+file agent team on this stack.
- Weaknesses: (1) **Archived/deprecated by Microsoft** — no security fixes. (2) Fragmented v0.2→v1 API history and migration burden. (3) Successor (Microsoft Agent Framework) is the maintained path; investing in AutoGen is a dead end.
- Best lesson to steal: **agents-as-tools (`AgentTool`)** — wrap a specialist agent behind a tool interface so the supervisor delegates through the same validated tool-call mechanism as any other tool.

## Scores (as a building block for a personal agent)
1. Intelligence/model flexibility: 6 — pluggable model clients, but ecosystem frozen; successor supersedes.
2. Persistent memory: 3 — no documented memory layer.
3. Autonomous execution: 6 — capable patterns (group chat, Magentic-One), but unmaintained.
4. Proactive assistance: 2 — none.
5. Browser/computer control: 6 — Playwright-MCP browsing + code execution via extensions; Magentic-One proof point.
6. Integrations/extensibility: 7 — first-class MCP workbench; frozen extension ecosystem.
7. Privacy/security: 2 — archived = no security patches; Microsoft explicitly warns against production/sensitive use.
8. Ease of deployment: 6 — simple pip install, but deprecated docs and migration pressure.
9. Free-tier/local accessibility: 6 — free framework; local-model path undocumented; successor is the supported route.
10. Reliability/observability: 4 — AutoGen Bench exists for evals; no maintained observability; dead project.
11. Developer experience: 5 — good docs historically; now "community-managed, responses may be limited".
12. Community health: 3 — 61k stars is legacy; archived, 1,125 open issues, maintenance mode.

## Verdict
**AVOID** — deprecated by Microsoft with no security fixes; evaluate its successor **microsoft/agent-framework** instead. Steal only the agents-as-tools delegation pattern.
