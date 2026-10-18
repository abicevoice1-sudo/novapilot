# zeroclaw-labs/zeroclaw

- Canonical URL: https://github.com/zeroclaw-labs/zeroclaw
- Category: Personal AI assistant runtime — single Rust binary, self-hosted.

Verification date: 2026-10-18. Stats (from saved API JSON): stars 32,991 · forks 4,976 ·
open issues 1,001 · license: API says Apache-2.0 SPDX, README says dual **MIT OR Apache 2.0**
· primary language Rust (Edition 2024) · last push 2026-10-18T04:16:53Z · archived: no.
Latest release: badge exists but not verified → unknown.

## Models / providers / cost
- Provider-agnostic: Anthropic, OpenAI, Ollama (local), and ~20 others; any
  OpenAI-compatible endpoint. Fallback chains + routing across providers.
- Free/local/BYOK: fully usable without paid subscription — Ollama local
  inference or your own keys. Claude Max setup-token and OpenAI Codex
  subscription auth supported natively.

## Memory
- SQLite + embeddings in the runtime (per architecture diagram); web dashboard
  offers memory browsing. Provenance/versioning/editing semantics not documented
  in README → partially verified only.

## Proactive / scheduled / background
- SOP engine: event-triggered Standard Operating Procedures (MQTT / webhook /
  cron / peripheral triggers) with approval gates and resumable runs.
- `zeroclaw service install` registers always-on background service
  (systemd/launchctl/Windows Service); dashboard has cron management.

## Browser / computer / files / terminal
- Tools: shell, browser, HTTP, hardware. Hardware reach: GPIO/I2C/SPI/USB on
  Raspberry Pi, STM32, Arduino, ESP32. Visible human-takeover browser workspace:
  not documented → unknown.

## Integrations / APIs / MCP / channels
- 30+ channels: Discord, Telegram, Matrix, email, voice, webhooks, CLI — all fed
  into one agent loop. Custom MCP servers supported. HTTP/WebSocket gateway +
  dashboard (chat, config, cron, tool inspection). Agent Client Protocol (ACP)
  for IDE integration.

## Multi-agent orchestration
- None advertised — single agent loop answering across channels.

## Voice / image / document / multimodal
- Voice: yes (channel adapter). Image/document: not documented → unknown.

## Install / hardware / cost / maintenance
- One-command installer (Unix: `curl … | sh`, then `zeroclaw quickstart`);
  prebuilt-binary path on Windows; Linux/macOS/Windows/FreeBSD/NixOS/Docker.
- Runs on own machine down to a Raspberry Pi. Cost = your model keys/usage.
- Docs live in a git submodule (contribution friction); 1,001 open issues is a
  maintenance backlog to watch.

## Security
- Default autonomy `supervised`: medium-risk ops require approval, high-risk
  blocked. Workspace boundaries, command policy, OS sandboxes
  (Landlock/Bubblewrap/Seatbelt/Docker), cryptographic tool receipts on every
  action. "YOLO mode" escape hatch for trusted dev boxes. SECURITY.md +
  security@zeroclaw.dev. Secrets storage encryption: not documented → unknown.

## Strengths
1. Security-first design: tiered autonomy + OS-level sandboxing + per-action
   cryptographic tool receipts is the best trust story in this set.
2. 30+ channels and 20+ providers with fallback routing — true "answer me
   anywhere, never go down" posture.
3. Single Rust binary with always-on service install; trivial ops footprint.

## Weaknesses
1. No multi-agent orchestration; single agent loop limits delegation depth.
2. YOLO mode explicitly bypasses the approval gates the project is praised for.
3. Browser tool exists but no documented human-takeover workspace; memory
   semantics (provenance/editing) undocumented.

## Best lesson to steal
Per-action cryptographic tool receipts + default-supervised tiered autonomy:
every consequential action gets a signed, auditable receipt, and the safe
default is supervised with a labeled escape hatch.

## Scores (1–10, one line of evidence each)
1. Intelligence/model flexibility — 9: ~20 providers + fallback routing, any OpenAI-compatible endpoint.
2. Persistent memory — 6: SQLite + embeddings and a memory browser; provenance/edit semantics unverified.
3. Autonomous execution — 8: SOP engine with resumable runs + always-on service install.
4. Proactive assistance — 7: cron/MQTT/webhook-triggered SOPs; goal tracking not documented.
5. Browser/computer control — 6: shell + browser + GPIO hardware; no visible human-takeover browser.
6. Integrations/extensibility — 9: 30+ channels, custom MCP servers, ACP, hardware traits.
7. Privacy/security — 9: OS sandboxes, approval gates, tool receipts, SECURITY.md.
8. Ease of deployment — 8: one-command installer, single binary, one TOML config file.
9. Free-tier/local accessibility — 8: Ollama + BYO keys, no mandatory subscription; no hosted free tier.
10. Reliability/observability — 7: tool receipts + dashboard; CI green; benchmarks not seen.
11. User experience — 7: dashboard chat/memory/cron; CLI-first, no polished consumer web app.
12. Community health — 8: 33k stars, pushed today, Discord, RFC process; 1,001 open issues tempers it.

## Verdict
**Active — keep.** Closest in this batch to a real personal-agent competitor.
Caveat: open-issue backlog and submodule docs suggest velocity strain.
