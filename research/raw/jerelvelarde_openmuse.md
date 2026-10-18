# jerelvelarde/openmuse

- **Canonical URL:** https://github.com/jerelvelarde/openmuse (no redirect observed)
- **Category:** Self-hosted personal-agent application (Expo React Native + Hono API + CopilotKit) with its own agent computer — explicitly **alpha**.

**Verification date:** 2026-10-18. Stats: the saved GitHub API JSON for this repo contained only a **rate-limit error** (API rate limit exceeded for 104.29.197.140), so stars/forks/open issues/last push/archived are all **unknown**; the repo exists (README fetches 200, 12,412 bytes). Language: **TypeScript** (Node 24, pnpm 11, README-evidenced). License: **MIT** (badge). Latest release: **0.1.0-alpha** (verified on releases page).

## Models / free / local / BYOK
- `AGENT_BACKEND=model`, `MODEL=provider/model-id` + provider key; CopilotKit supports OpenAI, Anthropic, Google. Provider keys stay on the server. Local default runs with **fictional data, no API keys**. Open-ended reasoning, live Google, and CopilotKit Rich Threads each need their own config.

## Memory
- Editable personal context: name, tone, avatar, **memories**; background-update preferences; durable in-app notifications. Optional **CopilotKit Intelligence** persistence (separate paid service, not MIT-licensed; acceptance pending). One conversation by default.

## Proactive / scheduling / background / goals
- **Goals & Tracking**: goals and milestones; **recurring public-page checks** (content changes, text availability, USD price thresholds) with deduplicated alerts and failure backoff. **Ideas**: suggestions with source evidence (edit/accept/dismiss). Task plans with pause/resume/cancel/retry; SQL leases recover interrupted work (host must stay running).

## Browser / computer / files / terminal
- Token-protected **Playwright Chromium worker** with persistent profiles; app can open a **live screenshot console** (human takeover) and import PDF downloads. Public pages only; **autonomous checkout is future work** — interactive work handed to the person.
- Optional **Docker Linux computer**: nonroot container, no host mounts, terminal **networking disabled** (web via browser worker), 30s command limit, saved command receipts; `/workspace` volume persists. Honest note: "This is a Linux container, not Meta Secure VM."

## Integrations / APIs / plugins / MCP / messaging
- **Gmail & Calendar** via Google OAuth (encrypted credentials at rest), drafts/attachments, calendar discovery; every send/change needs its own stored review. **MCP: none** (no MCP in alpha); disabled OpenBot HTTP adapter with contract tests. No health/bank/social connectors; no device push, no voice — all roadmap.

## Multi-agent
- None formal; chat supports delegated tasks and a follow-up queue.

## Voice / image / documents / multimodal
- **Documents**: PDF viewing, paging/zoom, **supported-field form filling**, PDF transfer computer↔app; pipeline: email attachment → PDF → form values → filled copy → reviewed reply → receipt. **Finance**: CSV import → spending summary. No voice, no image generation.

## Install / hardware / cost / maintenance
- `git clone`, pnpm install, `cp .env.example .env`, `pnpm dev` (+ `pnpm dev:web`); needs Node 24, optional Docker + Playwright. Storage: embedded PGlite in `.openmuse/` (back it up yourself). Single-owner, self-hosted. Maintenance: one person's alpha; CI runs browser/Docker tests.

## Security / privacy
- Single owner protected by a shared access key (not multi-tenant auth); keep on loopback/HTTPS. Stored **action reviews** gate every consequential action; "No hidden retry after an uncertain external write"; website content is "evidence, not permission to act". File/browser consoles use short-lived signatures. SECURITY.md exists.

## Top 3 strengths
1. **Honest alpha engineering**: docs/VERIFICATION.md, documented alpha boundaries, fictional-data default, "what is verified" — trust through evidence.
2. Durable task plans (SQL-lease recovery, pause/resume/cancel/retry) + stored action reviews for sends.
3. Human-takeover browser console + PDF form pipeline + finance CSV — concrete vertical workflows, not demos.

## Top 3 weaknesses
1. Alpha with solo maintainer; community health weakest in this batch.
2. Live functionality (Google, models, Rich Threads) all require the user's own keys/projects; default experience is fictional data.
3. Roadmap gap is huge vs. claimed Muse parity (push, voice, health/bank/social connectors all missing).

## Best lesson to steal
**docs/VERIFICATION.md + stated alpha boundaries** — ship a per-milestone "what is verified" matrix and explicitly label what isn't. It turns a thin alpha into a trustworthy one.

## Scores (1–10, evidence)
1. Intelligence/model flexibility: **6** — provider-neutral via CopilotKit, but live behavior unverified.
2. Persistent memory: **5** — editable memories + optional paid Intelligence persistence.
3. Autonomous execution: **6** — durable tasks with lease recovery; host must stay running.
4. Proactive assistance: **6** — recurring page checks with dedup/backoff; no learned proactivity.
5. Browser/computer control: **7** — persistent Chromium + takeover console + isolated Linux computer; no checkout.
6. Integrations/extensibility: **4** — Gmail/Calendar adapters only; no MCP, no marketplace.
7. Privacy/security: **7** — stored reviews, encrypted creds, honest boundaries; single-owner auth only.
8. Ease of deployment: **6** — standard dev flow, but multi-terminal + Docker + Xcode for mobile.
9. Free-tier/local accessibility: **7** — runs without keys (fictional data); real use needs BYOK/Google setup.
10. Reliability/observability: **5** — 115 tests, CI with browser/container jobs; alpha.
11. User experience: **7** — polished native mobile demo; empty-state flows documented.
12. Community health: **3** — solo author, alpha, no community metrics available.

## Verdict
**Active but alpha** (stats unverifiable due to API rate limit; repo fetched today). Keep as the transparency exemplar, not as an architecture source. Replacement if dropped: CopilotKit/OpenBot (the upstream pattern it copies).
