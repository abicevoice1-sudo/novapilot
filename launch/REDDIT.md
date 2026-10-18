# Reddit posts

## r/selfhosted — "Actlet: self-hosted personal AI agent with approval gates on everything"

Title: Actlet — self-hosted personal AI agent where every consequential action needs your approval

Body:
I built Actlet (Apache-2.0) — a self-hosted personal AI agent with a design decision I haven't seen elsewhere: **every consequential action requires explicit user approval, enforced in code rather than prompts.**

The agent plans, you approve each step, it executes. There are prompt-injection evals in the repo proving the gates hold.

Features:
- Local-first memory with nightly "dreaming" consolidation
- Natural-language scheduling with missed-run replay
- Real Chromium browser control (16 tools, screenshots)
- Telegram, Slack, Gmail, calendar, MCP
- Per-task cost/token/time budgets
- One-command install, $0 with Ollama

`curl -fsSL https://raw.githubusercontent.com/hydope/actlet/master/install.sh | bash`

I also published a 20-project comparison matrix in the repo showing exactly where it wins and loses. Happy to answer anything.

https://github.com/hydope/actlet

---

## r/LocalLLaMA — "Actlet: personal agent, Ollama-default, $0"

Title: Actlet — personal AI agent that runs on Ollama by default, $0

Body:
Actlet is a personal AI agent designed around local models first. Ollama is the default (`ollama/gpt-oss:20b`), with free-tier cloud fallbacks.

The standout feature: approval gates on every consequential action, enforced in code. Plus local-first memory, scheduling, and a real web UI.

One-command install. Would love feedback from the local-model crowd on the Ollama experience.

https://github.com/hydope/actlet
