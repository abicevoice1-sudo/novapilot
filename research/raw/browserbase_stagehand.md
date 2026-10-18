# browserbase/stagehand

- Canonical URL: https://github.com/browserbase/stagehand
- Category: SDK for browser agents (TypeScript, Python, Go monorepo) —
  framework/tool, NOT a personal assistant product.

Verification date: 2026-10-18. Stats (from saved API JSON): stars 25,720 ·
forks 1,764 · open issues 402 · license MIT · primary language TypeScript ·
last push 2026-10-17T22:12:14Z · archived: no. Latest release: not verified →
unknown. Copyright 2026 Browserbase, Inc.; "Stagehand" is a trademark.

## Models / providers / cost
- Any model via config (README example: `openai/gpt-5.4-mini` with
  `OPENAI_API_KEY`). Local runs need Chrome; Browserbase cloud browsers
  optional (pricing unverified → unknown).
- Free/local/BYOK: SDK is MIT and free; model keys BYO; no permanent free
  cloud tier documented.

## Memory
- None — per-run browser automation SDK; cookies/session persist in a
  local `userDataDir`, which is session state, not personal memory.

## Proactive / scheduled / background
- None — no scheduler, heartbeats, or goal tracking; you build that yourself.

## Browser / computer / files / terminal
- Core API: `act()` (self-healing actions), `observe()` (returns real
  selectors), `extract()` (schema-validated data via zod/pydantic). Signs in
  once, keeps the session. Human-takeover live view: not documented → unknown.

## Integrations / APIs / MCP / channels
- Three SDK languages (TS, Python, Go); part of the Browserbase ecosystem.
  MCP support: not documented in README → unknown. Positioning: "works with
  Claude Code, Codex, Eve, Mastra, and more" — i.e., a browser tool for agents.

## Multi-agent orchestration
- None.

## Voice / image / document / multimodal
- Structured web-data extraction; no voice, no document Q&A, no upload story.

## Install / hardware / cost / maintenance
- `pnpm add @browserbasehq/stagehand` / `pip install stagehand`; Chrome
  required for local runs. Lightweight as a library; trivial hosting burden
  (it runs inside your app).

## Security
- Nice privacy design point: `observe()` returns selectors so **credentials
  never reach the model** (README example fills login form from env vars).
  Approval workflows, sandboxing, prompt-injection hardening: not documented
  in README → unknown.

## Strengths
1. Cleanest browser API in this batch: act/observe/extract with self-healing
   selectors and schema-validated output.
2. Credentials-bypass-model pattern (`observe` returns selectors; secrets
   stay in env) — a privacy design NOVA should copy.
3. Three-language SDK (TS/Python/Go) with an active company behind it.

## Weaknesses
1. Category mismatch: framework for agents, not a personal agent.
2. Pulls you toward the Browserbase ecosystem for cloud; vendor coupling.
3. Every interaction costs an LLM call — latency and cost per task with no
   documented budgets.

## Best lesson to steal
The observe→act separation: let the model find elements, but perform
credential entry through deterministic selectors so secrets never enter the
model context. Schema-validated extraction (zod/pydantic) for reliable output.

## Scores (1–10, one line of evidence each)
1. Intelligence/model flexibility — 5: any model via config, but only for narrow browser tasks.
2. Persistent memory — 1: none.
3. Autonomous execution — 5: self-healing browser actions; no durable tasks.
4. Proactive assistance — 1: none.
5. Browser/computer control — 8: purpose-built browser SDK; human-takeover unverified.
6. Integrations/extensibility — 7: TS/Python/Go SDKs; Browserbase ecosystem pairing.
7. Privacy/security — 7: credentials never reach the model; broader controls undocumented.
8. Ease of deployment — 7: one package install; needs Chrome.
9. Free-tier/local accessibility — 6: MIT SDK free locally; model keys BYO.
10. Reliability/observability — 6: "reliability first" is their stated priority; metrics unverified.
11. User experience — 6: developer SDK with good docs; no end-user interface.
12. Community health — 8: 25.7k stars, pushed yesterday, Discord, X presence.

## Verdict
**Active — keep as browser-component/framework evidence only.** Not a
personal-assistant competitor; useful for the browser-tool architecture.
