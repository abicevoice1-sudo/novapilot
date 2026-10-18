# Channels & MCP

## Messaging channels

Talk to Nova from Telegram: set `TELEGRAM_BOT_TOKEN` (from @BotFather) and
restart. Optionally set `TELEGRAM_ALLOWED_USERS="12345,67890"` — without it,
anyone who finds the bot can talk to your agent.

How it works:
- Your message becomes an agent **task** — with the full approval machinery.
  Channel tasks are fully supervised (no pre-approved tools).
- You get an immediate "On it" ack, a nudge if the task needs your approval
  in the web UI, and the summary when it finishes.
- Every task is tagged `source: "telegram:<chat_id>"` so the audit trail
  shows where it came from.

## MCP servers as tools

Point Nova at any MCP server via `MCP_SERVERS` JSON:

```json
{"fs": {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]}}
```

The server's tools appear as `mcp_<server>_<tool>`, always with
`risk="medium"` and `requires_approval=True` — external code runs outside our
audit boundary, so every call needs a human yes. A server that fails to start
is logged and skipped; it never breaks boot.

## Skill portability (marketplace v0)

Skills are just `SKILL.md` files. Export one from the Skills page to share it;
import someone else's by pasting their file. No accounts, no registry, no
gatekeepers — the format *is* the marketplace.
