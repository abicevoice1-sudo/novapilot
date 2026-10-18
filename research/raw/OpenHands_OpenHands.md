# OpenHands/OpenHands (renamed from All-Hands-AI/OpenHands)

- Canonical URL: https://github.com/OpenHands/OpenHands
  (renamed; old org `All-Hands-AI` returns GitHub "Moved Permanently" and
  redirects to the `OpenHands` org — new org id 225919603).
- Category: Self-hosted developer control center for coding agents and
  automations ("Agent Canvas") — pivoted from the original OpenHands coding agent
  to a platform that runs ANY agent.

Verification date: 2026-10-18. Stats (fresh GitHub API JSON, saved to
`OpenHands_OpenHands.json`): stars 91,163 · forks 12,098 · open issues 1,055 ·
license MIT · primary language TypeScript · last push 2026-10-17T22:11:14Z ·
archived: no. Latest release: not verified → unknown.

## Models / providers / cost
- Bring-your-own model: any LLM via LLM profiles/settings. Agent-agnostic:
  runs OpenHands agent, Claude Code, Codex, Gemini CLI, Pi, OpenCode, or any
  Agent-Client Protocol (ACP) agent across local, remote, and cloud backends.
- Free/local/BYOK: self-hosting is free; model keys BYO; OpenHands
  Cloud/Enterprise optional (pricing unverified → treat as unknown).

## Memory
- None as a personal-memory product. Automations have task state, but no
  user-profile / long-term personal memory advertised.

## Proactive / scheduled / background
- Prebuilt automations run on a schedule or on webhook events (e.g. reports
  publishing to Slack; GitHub issue decomposition). Backends keep agents
  running even with the laptop shut. Goal tracking dashboard: not advertised.

## Browser / computer / files / terminal
- Agents run in Docker sandboxes, VMs, or company infra with full filesystem
  access ("Without a Sandbox" mode warns the agent gets the whole filesystem).
  Browser automation as a first-class capability: not documented → unknown.

## Integrations / APIs / MCP / channels
- Automations integrate Slack, GitHub, Linear, Notion, Datadog. Multi-backend
  switch from one frontend. OpenHands Cloud/Enterprise optional. MCP support:
  not documented in README → unknown.

## Multi-agent orchestration
- "Always-on engineering team" framing; multiple agents across multiple
  backends managed from one console. Structured delegation/orchestration
  primitives: not documented → partially verified (multi-agent hosting, not
  necessarily orchestration).

## Voice / image / document / multimodal
- Not documented → unknown.

## Install / hardware / cost / maintenance
- `npm install -g @openhands/agent-canvas` (Node 24+, `uv`); Docker-sandbox
  option; multi-machine/VM/server deployments for teams. Heavier than a
  single-user MVP. 1,055 open issues is a notable backlog.

## Security
- Docker sandbox option; SELF_HOSTING.md documents security hardening.
  Non-sandboxed mode = agent has full filesystem access (explicit warning).
  Secrets handling, approval workflows, prompt-injection defenses: not
  documented in README → unknown.

## Strengths
1. ACP-based agent neutrality — decouples the control plane from any single
   model or agent implementation.
2. Multi-backend execution (local/Docker/VM/cloud) with always-on automations
   triggered by schedule or webhooks.
3. Strong chatops integrations (Slack, GitHub, Linear, Notion) — real team
   workflows, 91k stars of community signal.

## Weaknesses
1. Category drift: no longer a personal assistant — it is a developer control
   center; weak fit for the personal-AI-agent comparison.
2. No personal memory, user profiles, or proactive personal assistance.
3. Multi-machine self-hosting and 1,055 open issues imply real ops burden.

## Best lesson to steal
The ACP (Agent Client Protocol) pattern: a neutral, JSON-RPC-style interface
so the control plane (UI, scheduler, permissions) never hard-couples to any
model or agent vendor.

## Scores (1–10, one line of evidence each)
1. Intelligence/model flexibility — 8: BYO LLM + any ACP agent (Claude Code, Codex, Gemini…).
2. Persistent memory — 2: no personal-memory product; task state only.
3. Autonomous execution — 9: scheduled/webhook automations on always-on backends.
4. Proactive assistance — 6: scheduled automations exist; not a proactive personal assistant.
5. Browser/computer control — 7: Docker-sandboxed code execution, full filesystem; browser unadvertised.
6. Integrations/extensibility — 8: Slack/GitHub/Linear/Notion + ACP plugin surface.
7. Privacy/security — 7: Docker sandboxing + self-hosting hardening docs; non-sandbox mode is risky.
8. Ease of deployment — 6: npm install is easy; multi-backend/multi-machine setup is not.
9. Free-tier/local accessibility — 6: self-host free, BYO keys; no personal local-model story documented.
10. Reliability/observability — 7: CI, live previews; automation observability depth unknown.
11. User experience — 7: Agent Canvas web UI exists; still in beta.
12. Community health — 9: 91k stars, pushed yesterday, Slack community, docs site.

## Verdict
**Active — keep as framework evidence only.** Not a personal-assistant
competitor anymore; useful for architecture lessons (ACP, multi-backend).
No stronger personal-agent replacement needed — it was never one.
