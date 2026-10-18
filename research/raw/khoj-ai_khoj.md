# khoj-ai/khoj — Competitor Research (evidence only)

- **Canonical URL:** https://github.com/khoj-ai/khoj
- **Category:** AI second-brain / personal knowledge assistant — semantic search + RAG over personal docs, custom agents, scheduled automations, multimodal chat.
- **Verification date:** 2026-10-18

## Verified stats (from GitHub API JSON, checked 2026-10-18)

| Field | Value |
|---|---|
| Stars | 37726 |
| Forks | 2519 |
| Open issues | 169 |
| License | AGPL-3.0 |
| Primary language | Python |
| Created | 2021-08-16 |
| Last push | 2026-08-02T01:55:40Z |
| Archived | false |
| Homepage | https://khoj.dev |
| Latest release | unknown (not verified) |
| Topics | agent, ai, assistant, chat, chatgpt, emacs, image-generation, llama3, llamacpp, llm, obsidian, offline-llm, productivity, rag, research, self-hosted, semantic-search, stt, whatsapp-ai |

GitHub description: "Your AI second brain. Self-hostable. Get answers from the web or your docs. Build custom agents, schedule automations, do deep research. Turn any online or local LLM into your personal, autonomous AI (gpt, claude, gemini, llama, qwen, mistral). Get started - free."

*Note: README was thin (107 lines); substantive claims verified against docs.khoj.dev search snippets and two targeted web searches.*

## Models / providers

- Any local or online LLM: "Chat with any local or online LLM (e.g llama3, qwen, gemma, mistral, gpt, claude, gemini, deepseek)" (README).
- Local inference: docs self-host page confirms OpenAI-compatible proxy setup for **Ollama or LMStudio**; multiple chat models configurable with tokenizer/max-prompt-size fields; vision enabled only for OpenAI vision models per docs.
- Free usage: free cloud app at https://app.khoj.dev (no setup), free self-host. Enterprise tier (cloud/on-prem/hybrid) exists at khoj.dev/teams. BYOK status for the cloud app: unknown.

## Persistent memory

- Emphasis is on **semantic search over indexed personal docs** (RAG), not episodic user memory.
- Mechanisms evidenced: file/folder sync via Desktop, Obsidian, Emacs clients; Notion workspace sync; drag-and-drop files; supported formats PDF, Markdown, org-mode, Word, Notion, images.
- Custom agents can have **custom knowledge bases**, personas, chat models, tools (README; makeuseof review).
- No evidence of long-term user-profile memory, episodic conversation memory, or memory consolidation across sessions → treat as "document-memory, not user-memory".

## Proactive behavior / scheduling / background

- **Automations are confirmed**: docs.khoj.dev features page — "Automations are a powerful feature within Khoj to schedule repeated jobs... Automations allow you run your query automatically at a scheduled time and frequency. Khoj will send its research to you as an email."
- makeuseof: custom automations (e.g., daily 9 AM stock summary), pre-built automations, delivered straight to email; described as "agentic-esque RSS feed".
- Backend: DeepWiki of the repo shows **APScheduler** for background tasks with DB-backed job storage and leader election for multi-instance deployments.
- Desktop app: cron-based background scheduling, system-tray persistence, OS notifications, auto-launch on boot (DeepWiki).
- Goal tracking: **none evidenced**. Proactivity = scheduled research + email/newsletter delivery, not autonomous goal pursuit.

## Browser automation / computer use / file ops / terminal

- No evidence of browser automation or computer-use. DeepWiki indexed a page titled "Operator System" but the content shown describes a research tool loop, not a browser operator → treat browser control as "none evidenced".
- Tools evidenced in research mode: SemanticSearchFiles, SearchWeb, ReadWebpage, PythonCoder (`run_code()` — **Python code execution in chat** for analysis/plotting), ViewFile, and MCP tools (`mcp_client.run_tool()`).
- File ops: document sync/indexing via clients; "view file" tool in research loop. Terminal access: none evidenced.

## Integrations / APIs / plugins / MCP / channels

- Clients: web browser, **Obsidian plugin** (76/100 on obsidianstats), **Emacs**, Desktop app (Electron), Phone, **WhatsApp**. Notion direct sync from web app.
- MCP: **client support confirmed** — research loop executes tools via `server/tool` calling `mcp_client.run_tool()` (DeepWiki src/khoj/routers/research.py). A third-party community MCP server ("khoj – Cloud Services MCP Server by Kimbj0204", hexmos) exists; official MCP-server mode: unknown.
- REST API + WebSocket backend (FastAPI, per DeepWiki). Plugins beyond the above clients: unknown.
- Messaging channels: WhatsApp confirmed; Telegram: unknown (not in README/topics).

## Multi-agent orchestration

- **None evidenced.** Users can create multiple custom agents (personality, tools, knowledge), but no agent-to-agent delegation, A2A protocol, or supervisor/worker architecture is stated.

## Voice / image / document / multimodal

- Voice: speech-to-text tag on repo; README "talk out loud, play your messages" (TTS). STT input: topic-evidenced, detail unknown.
- Image: **context-aware image generation** leveraging personal notes (G2/MOGE summaries); supported doc formats include images.
- Documents: PDF, Markdown, org-mode, Word, Notion, images. Video: none evidenced.

## Install complexity / hardware / cost / maintenance

- Install: docs-driven self-host; KDnuggets shows **Docker Compose** path (Windows needs WSL + Docker Desktop); also a **pypi package** (`khoj`) and CI badges (test/dockerize/pypi). Setup docs cover chat-model config and knowledge sync. Complexity: moderate — Docker one-command for basics, more config for models/sync.
- Hardware: not stated in README. Local LLM inference implies GPU-class machine (standard Ollama/LMStudio requirements) → mark unknown, no stated minimums.
- Hosting cost: self-host free; free cloud app; enterprise pricing unknown.
- Maintenance: DB-backed (Postgres, with embedded-Postgres option per DeepWiki env config); background scheduler needs to stay running → a persistent host/daemon, not a one-shot script.

## Security

- Privacy architecture: **"open-source, self-hostable. Always."** — on-device/self-hosted option keeps data local; G2: "keeping your information local for enhanced privacy".
- Sandboxing of code execution / approval workflows for tool use: **unknown** (no statement in README or searched docs).
- Secrets handling (API keys for models): **unknown** — config docs mention model fields; storage mechanism not verified.
- License AGPL-3.0: strong copyleft — sharing-networked code must be released; matters if NOVA forks/embeds it.

## Strengths / weaknesses / lesson

**Top 3 strengths**
1. Best-in-class personal RAG: semantic search over synced notes/docs with published retrieval-benchmark claims (blog: "excellent performance on modern retrieval and reasoning benchmarks").
2. Provider flexibility: any local (Ollama/LMStudio/llama.cpp) or cloud LLM, swappable chat models per agent.
3. Real scheduled proactivity: automations run recurring research and email results — a working cron+LLM loop (APScheduler, DB-backed), plus multi-surface clients (WhatsApp/Obsidian/Emacs/Desktop).

**Top 3 weaknesses**
1. No browser/computer-use — tool loop is search+read+code+MCP only; cannot act on the open web or user's machine.
2. AGPL-3.0 license makes commercial embedding/forking costly (must open-source derivative network services).
3. Memory is document-centric; no evidenced episodic user memory, goal tracking, or autonomous multi-step pursuit beyond scheduled research.

**Single best lesson to steal:** Scheduled automations that run a research query on a cron and **deliver results to the user's email inbox** — low-cost, high-value proactivity that works with zero autonomy risk. This is the cheapest credible "proactive agent" feature to ship first.

## Scores (1–10, one line of evidence each)

1. Intelligence/model flexibility — **8**: any local or online LLM; docs confirm Ollama/LMStudio OpenAI-compatible proxies plus gpt/claude/gemini/deepseek (README + self-host docs).
2. Persistent memory — **6**: strong document memory via semantic search/indexed knowledge bases; no evidenced episodic or user-profile memory.
3. Autonomous execution — **7**: research tool loop (web search, page read, Python code exec, MCP tools) plus APScheduler automations; bounded to research tasks, no computer control.
4. Proactive assistance — **6**: scheduled automations with email delivery (newsletters, smart notifications); no goal tracking or nudge loops evidenced.
5. Browser/computer control — **4**: file view and Python code execution evidenced; browser automation/computer-use: none evidenced.
6. Integrations/extensibility — **8**: Obsidian, Emacs, WhatsApp, Desktop, web, phone, Notion; MCP client support; FastAPI/REST backend.
7. Privacy/security — **7**: self-hostable, on-device option, open-source; sandboxing/approval workflows/secrets handling: unknown.
8. Ease of deployment — **7**: Docker Compose path, PyPI package, free zero-setup cloud app; local-LLM/GPU config and Postgres add friction.
9. Free-tier/local accessibility — **8**: free cloud app, free self-host, local LLM support; enterprise tier pricing unknown.
10. Reliability/observability — **6**: CI badges (test/dockerize/pypi) in README; APScheduler DB-backed jobs with leader election; production monitoring tooling: unknown.
11. User experience — **7**: third-party review (makeuseof) calls it a NotebookLM+Claude hybrid with per-agent tuning UI; UI not directly inspected.
12. Community health — **8**: 37.7k stars, 2.5k forks, 169 open issues, not archived, Discord + blog active; note last push 2026-08-02 (~10 weeks before verification) suggests slower but continuing cadence.

## Verdict

- **Status: active.** Not archived, large community (37.7k stars / 2.5k forks), shipped sibling project Pipali (open-source AI coworker) announced in README, CI pipelines present.
- **Worth keeping in research set:** yes — it is the reference implementation for self-hosted personal RAG + scheduled automations. No replacement repo named; it is itself the strongest candidate in its lane.
- **Caveat:** last verified push 2026-08-02 (vs 2026-10-18 verification date) — re-check activity before treating it as fast-moving.
