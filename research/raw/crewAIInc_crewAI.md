# crewAIInc/crewAI — research notes

- Canonical URL: https://github.com/crewAIInc/crewAI
- Category: [framework/component] — multi-agent orchestration framework (Crews + Flows). Not an end-user personal assistant product.
- Verification date: 2026-10-18. Stats (from saved GitHub API JSON): 59,813 stars · 8,762 forks · 753 open issues · License: MIT · Primary language: Python · Last push: 2026-10-18 · Archived: no. Latest GitHub release: unknown (no GitHub releases; versioned via PyPI, CLI reports v0.102.0 in README).

## What it provides as a building block
The multi-agent coordination layer: role-based Agents (role/goal/backstory/LLM/tools), Tasks with expected outputs and delegation, Crews (sequential or hierarchical process with a manager agent), and Flows (event-driven `@start`/`@listen`/`@router` workflows with typed state). Scaffolds JSON-first projects (`agents/*.jsonc`, `crew.jsonc`) plus a `crewai` CLI. This is the closest match to the "specialized subagents" requirement (researcher/planner/coder/browser agents).

## Models / providers / cost
- Default OpenAI; per-agent LLM configurable (`"llm": "openai/gpt-4o"`); documented LLM-connections page. FAQ: local models via Ollama/LM Studio supported. Fully BYOK.
- Free usage: framework is free/OSS (MIT). Model calls are the user's key. Enterprise CrewAI AMP (control plane, observability) is paid; free access to part of AMP (Crew Control Plane) per FAQ.
- Anonymous telemetry collected by default (OTEL_SDK_DISABLED=true to disable); opt-in `share_crew` shares task content — a privacy surface to disable in a personal product.

## Memory design
- Per-agent memory exists (short/long-term, entity memory per docs; README mentions "agents — role, goal, backstory, tools, LLMs, memory"), but README does not detail a semantic personal-memory system. Not a mem0 replacement; weaker than mem0 for cross-session personal recall.

## Proactive / scheduling / background
- Flows are event-driven with async execution and checkpointing — good primitives for workflow automation. No built-in cron/scheduler or proactive notification engine; human-input-on-execution supported (approval-adjacent).

## Browser / computer / file / terminal
- Tool-based: built-in tools include SerperDevTool (web search); browser automation comes from attached tools/MCP servers, not built in. Custom tools in `tools/` referenced as `"custom:<name>"`. Knowledge files (`knowledge/`) for RAG-ish grounding.

## Integrations / MCP
- Explicit MCP and A2A support claimed ("MCP/A2A support" in Key Features). Docs served via a live MCP server (docs.crewai.com/mcp). Large public tool ecosystem; official examples repo.

## Multi-agent
- This IS the multi-agent framework: role-playing agents, delegation, sequential + hierarchical (manager) processes, Agent-ready async execution. Core value proposition.

## Voice / image / document / multimodal
- Not documented in README; knowledge/ dir and skills/ dir exist (document ingestion implied via knowledge files). No voice. Multimodal depends on model.

## As a dependency: install / hardware / cost / maintenance
- Install via `uv tool install crewai` (Python 3.10–3.14, UV required — extra toolchain step vs pip). Chroma/hnswlib native dependency has caused Windows build pain (documented workaround). No server needed; hardware = model API calls. Maintenance: very active (push today), VC/company-backed, 753 open issues, 100k+ certified devs claimed.

## Security posture (embedding it)
- Tools execute with the developer's privileges; human-input-on-execution exists but is not a mandatory approval framework. Anonymous telemetry default-on (disable in product). Prompt-injection defenses not claimed in README. Guardrails mentioned only as an agent-design option in the skills table.

## Strengths / weaknesses / lesson
- Strengths: (1) Highest-level multi-agent abstraction: role/goal/backstory agents with delegation map directly onto the supervisor→specialists design. (2) Crews (autonomy) + Flows (deterministic control) in one framework. (3) JSON-first agent definitions + CLI make specialist agents declarative and auditable.
- Weaknesses: (1) Opinionated around role-play personas — ceremony overhead for a single personal agent. (2) Memory story weaker than mem0; checkpointing/async details thin in README vs LangGraph's. (3) UV toolchain + native deps (chroma) raise install friction; telemetry default-on is a privacy tax.
- Best lesson to steal: **declarative specialist agents (role/goal/tools as data) combined with explicit flow control** — define subagents in JSON config, wrap them in deterministic flows with human-input gates.

## Scores (as a building block for a personal agent)
1. Intelligence/model flexibility: 8 — per-agent LLM, local models via Ollama, but OpenAI-default and config overhead.
2. Persistent memory: 5 — per-agent memory exists but underspecified in README; weaker than dedicated memory layers.
3. Autonomous execution: 8 — crews with delegation, hierarchical manager, checkpointing, async execution.
4. Proactive assistance: 3 — event-driven flows; no scheduler or notification engine.
5. Browser/computer control: 4 — tool/MCP-based only; no built-in computer use.
6. Integrations/extensibility: 9 — MCP/A2A claimed, custom tools, knowledge, skills, examples repo.
7. Privacy/security: 5 — telemetry default-on, no stated injection defenses, guardrails optional.
8. Ease of deployment: 6 — UV install, Python version pin, native chroma dep; no infra beyond that.
9. Free-tier/local accessibility: 8 — MIT, free framework, Ollama support; paid AMP optional.
10. Reliability/observability: 6 — checkpointing claimed; best observability lives in paid AMP; OSS tracing unknown.
11. Developer experience: 8 — CLI scaffolding, JSON-first definitions, coding-assistant skills, courses.
12. Community health: 9 — 59.8k stars, daily pushes, company-backed, large claimed community.

## Verdict
**ADAPT** — take the role-based specialist-agent + flow-control pattern as design inspiration, but do NOT adopt as a dependency: it duplicates LangGraph's runtime role with heavier abstraction and weaker memory; better to implement a small supervisor on LangGraph and keep agents declarative.
