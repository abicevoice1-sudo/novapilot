# Show HN: Actlet — the little actor that does your tasks

Hi HN. I built Actlet, an open-source personal AI agent, because every agent I tried had the same hole: they'd happily click, write, send, and spend without asking.

Actlet inverts that. **Every consequential action requires your explicit approval — enforced in code, not in prompts.** The agent literally cannot act without you. I also wrote 5 prompt-injection evals to prove the gates hold when the model is being manipulated.

What it does:
- Remembers (local-first, full-text, exportable — it "dreams" nightly to consolidate learnings)
- Schedules ("every morning at 8" → recurring tasks, with missed-run replay and quiet hours)
- Browses (real Chromium, 16 approval-gated tools, tab management, screenshots at every step)
- Connects (Telegram, Slack, Gmail, calendar, any MCP server)
- Delegates (specialist sub-agents with restricted toolsets)
- Stays honest (per-task budgets, verified-vs-planned labeling everywhere)

Install is one command — it installs, generates your token, starts the server, and opens your browser:

```
curl -fsSL https://raw.githubusercontent.com/abicevoice1-sudo/actlet/master/install.sh | bash
```

$0 by default (local Ollama). Apache-2.0.

The differentiator I'm proudest of: I researched 20 agent projects live before writing the architecture, scored them on 12 dimensions, and published the full matrix in the repo (research/competitor-matrix.md) — including where Actlet loses. Nobody clears 8/10; we're at 7.76, second overall. The honest gaps are stars and battle-testing, which is why I'm here.

Try to break the approval gates. I'd genuinely love to know if you can.

https://github.com/abicevoice1-sudo/actlet
