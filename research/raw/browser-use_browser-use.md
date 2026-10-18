# browser-use/browser-use

- Canonical URL: https://github.com/browser-use/browser-use
- Category: Open-source browser agent LIBRARY (Python + TypeScript) + optional
  hosted cloud — a component/framework, NOT a personal assistant product.

Verification date: 2026-10-18. Stats: **unknown — the GitHub API returned
rate-limit errors for this repo at check time, and the saved JSON holds only
the error.** License MIT (from README). Language: Python/TypeScript. Last push
and latest release: unknown (not verified). No evidence of archival.

## Models / providers / cost
- Runs locally with ANY LLM (README example uses ChatOpenAI `gpt-5.6-luna`);
  proprietary `ChatBrowserUse` (BU2 model) option via Browser Use API key.
- Free/local/BYOK: fully usable locally with your own key; cloud browsers
  $0.02/browser-hour + traffic (stealth, residential proxies, CAPTCHA
  solving, live view); new cloud signups get $1 credit. No permanent free
  tier claimed.

## Memory
- None — per-task agent library; no cross-session user memory.

## Proactive / scheduled / background
- None — you wire your own scheduling around it.

## Browser / computer / files / terminal
- This is its entire purpose: AI browser agent that navigates like a human
  (self-claimed 90.5% top score on "Stealth Bench V2" — vendor benchmark, not
  independently verified). Local Chrome or cloud browser; remote over CDP.
  File ops: included Bash toolset for processing data and writing files.
  Terminal: Bash on host. Human-takeover: live view URL on cloud; local
  takeover story unverified → unknown.

## Integrations / APIs / MCP / channels
- MCP support: yes (registered MCP name `com.browser-use/browser-use`).
  Maintained "toolsets for Claude" (31 browser actions + Bash via Anthropic
  SDK). CLI skill install for Claude Code/Codex/OpenClaw-style agents.
  Hosted Agents API on cloud.

## Multi-agent orchestration
- None — one agent per task.

## Voice / image / document / multimodal
- Visual understanding of pages implied by design; screenshots on cloud.
  Voice: none. Document upload: not documented → unknown.

## Install / hardware / cost / maintenance
- `uv add browser-use`, Python ≥ 3.11, `.env` with `OPENAI_API_KEY`; local
  runs need Chrome installed; works in Docker/CI/serverless. Cost = your LLM
  tokens per task (browser agents are token-hungry — watch budgets).

## Security
- Local execution keeps browsing data on your machine; cloud has ToS/privacy
  policy. Prompt-injection defenses for malicious pages: not documented in
  README → unknown (a real risk class for browser agents). Bash toolset =
  unsandboxed host command execution by design.

## Strengths
1. Strongest pure browser-agent in this batch: stealth/detection handling,
   CAPTCHA solving, residential proxies, session profiles, live view.
2. Local-first with any LLM + MCP + Claude toolsets — clean integration story
   as a browser TOOL for a larger agent.
3. Cheap cloud browsers ($0.02/hr) for when local Chrome won't do.

## Weaknesses
1. Category mismatch: a component, not a personal agent — no memory,
   scheduling, chat UI, or proactivity.
2. Browser agents are the highest prompt-injection-risk surface; hardening not
   documented in the README.
3. Token cost per browser task is high; no built-in budgets observed.

## Best lesson to steal
Treat browser driving as a pluggable tool module (local browser ↔ stealth
cloud browser swap) with persistent browser profiles — signed-in sessions
survive across runs.

## Scores (1–10, one line of evidence each)
1. Intelligence/model flexibility — 7: any LLM locally; BYO key required.
2. Persistent memory — 1: none; per-task library.
3. Autonomous execution — 6: autonomous browser tasks; no durable jobs.
4. Proactive assistance — 1: none.
5. Browser/computer control — 9: purpose-built browser agent with stealth, CAPTCHA, proxies.
6. Integrations/extensibility — 8: MCP, Claude toolsets, CLI skill, hosted API.
7. Privacy/security — 5: local option is good; injection hardening undocumented, Bash unsandboxed.
8. Ease of deployment — 7: `uv add`; needs Chrome and .env keys.
9. Free-tier/local accessibility — 6: free locally with own keys; cloud is pay-per-use.
10. Reliability/observability — 6: vendor benchmark self-reported; independent verification absent.
11. User experience — 6: demos/CLI for developers; no end-user interface.
12. Community health — unknown: API rate-limited stats; README/blog/docs show activity but no numbers verified.

## Verdict
**Active (presumed; stats unverifiable today) — keep as browser-component
evidence, not a competitor.** Re-check stats when API quota resets before
finalizing the matrix.
