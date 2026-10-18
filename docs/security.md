# NovaPilot — Security & threat model

NovaPilot handles private memories, files, credentials, browser sessions, and external actions. It is designed as a security-sensitive application from day one.

## Trust boundaries

1. **Model output is untrusted.** The LLM plans, but every consequential action passes a policy gate before executing.
2. **Tool output / retrieved content is untrusted data, never instructions.** Web pages, documents, emails, and tool results cannot issue commands (prompt-injection boundary).
3. **The browser and sandbox are hostile territory.** Code runs in Docker; the browser runs in its own container; neither reaches host credentials.
4. **The user is the authority.** Only the user (via UI approval or explicit delegation) authorizes consequential actions.

## Threat model (STRIDE-lite)

| # | Threat | Abuse case | Mitigation |
|---|--------|-----------|------------|
| T1 | **Prompt injection** (web page / doc / email / tool result) | Malicious page tells the agent to exfiltrate files or run commands | Injection boundary: retrieved content is wrapped and labeled as data; planner is instructed (and tested) to never follow instructions from tool output; high-risk tools require approval regardless of what the page says; `tests/security/` includes injection evals |
| T2 | **Tool misuse / overreach** | Agent deletes data, spams contacts, spends money | Tiered autonomy (default-supervised, from zeroclaw): low-risk auto, medium-risk approve, high-risk blocked; per-tool allowlists; signed tool receipts in the audit log |
| T3 | **Credential exfiltration** | Secrets leak into model context, logs, or a third party | Secrets in OS keyring / encrypted store, never in prompts; stagehand-pattern credential entry (deterministic selectors, secrets bypass the model); audit logs redact secret values; API keys never reach the browser bundle |
| T4 | **SSRF / internal network access** | Agent tricked into hitting `localhost` services or cloud metadata | Egress allowlist on the sandbox; cloud-metadata IPs blocked; browser container has no route to host services |
| T5 | **Data exfiltration** | Memory or files sent to an attacker-controlled endpoint | Tool-level network allowlists; uploads require approval; audit log records every external transmission |
| T6 | **Supply chain** | Malicious skill/plugin or dependency | Skills are markdown+YAML, reviewed before install (explicit user approval); dependencies pinned with hashes; `pip audit` in CI |
| T7 | **Session hijacking** | Attacker steals the web session | Secure, HttpOnly, SameSite cookies; short-lived tokens; optional TOTP for the local UI |
| T8 | **Memory poisoning** | Attacker plants false memories via chat or documents | Memories carry source + timestamp + confidence; user reviews the memory library; provenance shown on recall; delete/edit are one click |
| T9 | **Resource exhaustion** | Runaway task burns quota/money/CPU | Per-task budgets (tokens, calls, cost, wall-clock) enforced by the gateway; global kill switch; quiet hours |
| T10 | **Malicious downloads** | Agent fetches malware or unsafe scripts | Downloads land in quarantine; execution requires approval; file-type policy; hash recorded in receipt |

## Security controls (shipped progressively, tracked in roadmap)

- Least-privilege tool permissions; per-tool and per-integration authorization
- Sandboxed code execution (Docker; no host exec in default config)
- Secrets outside source control (`.env`, never committed; `.env.example` only)
- Encrypted transport (TLS) and encrypted local secret store
- Authentication + secure session management on the web UI
- Audit log with sensitive values redacted; per-action signed receipts
- Resource limits: file access scope, network egress, CPU/memory/time per tool
- Explicit approval for: sending messages, spending money, deleting data, publishing content, installing skills, granting integrations
- Data export, retention controls, and full deletion workflows (GDPR-shaped, even for single-user)

## Responsible vulnerability reporting

See `SECURITY.md` in the repo root: report to the maintainer privately, allow 90 days for a fix before disclosure, and never test against other users' deployments. Security issues are never filed as public GitHub issues.
