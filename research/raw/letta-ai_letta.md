# letta-ai/letta

- Canonical URL: https://github.com/letta-ai/letta
- Category: Stateful-agent harness / memory platform (personal + coding agents).
  **Important:** the `letta` repo is now a signpost — the current source lives at
  [`letta-ai/letta-code`](https://github.com/letta-ai/letta-code) (agent harness,
  terminal UI, App Server, channels); the old Letta V1 API server is on the
  `archive` branch and retired. Stats below are for `letta-ai/letta`.

Verification date: 2026-10-18. Stats (from saved API JSON): stars 25,176 · forks
2,649 · open issues 0 (API reports 0 — issues likely disabled, treat with
caution) · license Apache-2.0 · primary language: none (redirect repo) ·
last push 2026-09-10T17:59:08Z · archived: no. Latest release: unknown.

## Models / providers / cost
- `/connect` adds your own LLM API keys (OpenAI/ChatGPT, Anthropic, Z.ai coding
  plan, …); `/model` swaps models at runtime. Backend: Letta Cloud (default,
  requires sign-in) or local. Local-model/Ollama pathway: not documented →
  unknown.

## Memory
- Best-in-class in this batch: memory blocks (system-prompt learning),
  sleep-time compute / "dreaming" (`/sleeptime`, `/dream`, `/reflect`) for
  self-improvement, MemFS (all context, incl. memory, git-versioned and
  syncable to a GitHub repo), `/palace` memory viewer, `/search` across all
  messages/agents, skill learning. Export of memory supported; AgentFile
  import/export deprecated.

## Proactive / scheduled / background
- Crons & schedules, heartbeats, and self-managed schedules; agents designed
  to "work proactively" across time. Agents run on laptop, remote computers
  (`letta server --computer-name`), GitHub Actions, cloud sandbox, and are
  reachable via chat.letta.com / mobile.

## Browser / computer / files / terminal
- Runs on your own machines via the server binary; remote computers routable
  per-agent. Browser automation as a first-class feature: not documented →
  unknown.

## Integrations / APIs / MCP / channels
- Channels: Slack, Telegram, Discord, chat.letta.com (mobile web), desktop app,
  custom channels. Skills ecosystem: install from GitHub, ClawHub, Hermes
  Skills Hub. Hooks (custom scripts at execution keypoints), Letta Agent SDK
  for TypeScript apps. MCP support: not documented → unknown.

## Multi-agent orchestration
- Built-in subagents (general-purpose, forked, recall) run in background;
  agents can call any other agent (including themselves) as subagents.

## Voice / image / document / multimodal
- Not documented → unknown.

## Install / hardware / cost / maintenance
- `npm install -g @letta-ai/letta-code`, then `letta`; desktop apps for
  macOS/Windows/Linux; AUR/Nix packages. Local backend keeps it free apart
  from your model keys; Letta Cloud free tier: not documented → unknown.

## Security
- Permission modes: configure what actions auto-approve/auto-deny.
  Secrets feature obfuscates values from context (requires sign-in). Cloud
  stores memory/identity centrally (convenience vs. privacy trade-off).
  Prompt-injection hardening details: not documented → unknown.

## Strengths
1. Memory architecture is the state of the art here: memory blocks + MemFS +
   scheduled dreaming — the exact "remembers and self-improves" story NOVA
   needs.
2. True cross-device identity: one agent reachable from CLI, desktop, mobile
   web, and messaging channels, running on any of your machines.
3. Self-configuring agents ("ask your agent to configure itself") + skills
   ecosystem lower the setup barrier.

## Weaknesses
1. Code split across repos (`letta` signpost vs `letta-code` source) confuses
   evaluation and contribution.
2. Cloud-default + sign-in for secrets/remote features creates lock-in and
   privacy surface for the most sensitive asset (memory).
3. Open-issue count of 0 is a transparency smell (issues disabled), not proof
   of zero defects.

## Best lesson to steal
Memory blocks + scheduled "dreaming": a tiered memory (fast editable blocks
+ archival store) plus background reflection jobs that consolidate and
self-improve memory — not just retrieval.

## Scores (1–10, one line of evidence each)
1. Intelligence/model flexibility — 8: BYO keys, /model hot-swap, several providers.
2. Persistent memory — 10: memory blocks, MemFS, dreaming, /palace, /search.
3. Autonomous execution — 7: always-on agents, crons, remote computers; task checklists unadvertised.
4. Proactive assistance — 8: heartbeats, crons, self-managed schedules.
5. Browser/computer control — 6: runs on own machines with tool use; browser automation not evidenced.
6. Integrations/extensibility — 8: channels, hooks, Agent SDK, skills hubs, custom channels.
7. Privacy/security — 7: permission modes, secret obfuscation; cloud-default is a caveat.
8. Ease of deployment — 8: one-command npm install, desktop app, local backend option.
9. Free-tier/local accessibility — 6: local backend free but model keys BYO; cloud free tier unknown.
10. Reliability/observability — 7: /doctor symptom investigation; eval benchmarks not seen.
11. User experience — 8: CLI + desktop + mobile web + self-configuring agents.
12. Community health — 8: 25k stars, MemGPT creators, active docs; repo split is a smell.

## Verdict
**Active (via letta-code) — keep.** The memory-system reference implementation
for NOVA. Monitor how the repo split evolves.
