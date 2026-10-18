# Repository evidence & verification log

**Check date:** 2026-10-18. **Method:** GitHub REST API (`/repos/{owner}/{repo}`) for stats/license/language/pushed/archived, plus `raw.githubusercontent.com` README reads and docs-site skims. Per-repo evidence files: `research/raw/<owner>_<repo>.md` (20 files). Raw API JSON: `research/raw/<owner>_<repo>.json`.

## What was verified per repo

| Repo | API JSON | README read | Stats usable | Notes |
|------|----------|-------------|--------------|-------|
| nano-muse/nanoMuse | ✓ | ✓ | ✓ | — |
| jerelvelarde/openmuse | rate-limited | ✓ | unknown | Releases page verified (0.1.0-alpha) |
| wlsdks/muse-agent | rate-limited | ✓ | unknown | Releases page verified (v0.3.0 prerelease) |
| openclaw/openclaw | ✓ + re-verified 2nd call | ✓ (+ docs site) | ✓ | 392,307★ confirmed by two independent API calls |
| NousResearch/hermes-agent | ✓ + re-verified 2nd call | ✓ | ✓ | 254,743★ confirmed by two independent API calls |
| agent0ai/agent-zero | rate-limited | ✓ | unknown | 3rd-party "~17.2k★" claim excluded as unverifiable |
| khoj-ai/khoj | ✓ | ✓ | ✓ | Pushed 2026-08-02 — cadence slowed vs peers |
| nearai/ironclaw | ✓ | ✓ | ✓ | — |
| HKUDS/nanobot | ✓ | ✓ | ✓ | — |
| sipeed/picoclaw | rate-limited | ✓ | unknown | README self-claim "26K★" flagged unverifiable |
| zeroclaw-labs/zeroclaw | ✓ | ✓ | ✓ | License: API Apache-2.0, README "MIT OR Apache-2.0" |
| letta-ai/letta | ✓ | ✓ | ✓ (signpost) | Source moved to `letta-ai/letta-code`; issues disabled (0 is not a signal) |
| OpenHands/OpenHands | ✓ (fresh, post-rename) | ✓ | ✓ | Canonical URL is now `OpenHands/OpenHands`; `All-Hands-AI` 301-redirects |
| browser-use/browser-use | rate-limited | ✓ | unknown | MIT confirmed from README |
| browserbase/stagehand | ✓ | ✓ | ✓ | — |
| mem0ai/mem0 | ✓ | ✓ | ✓ | Benchmark claims flagged: reflect managed platform, not OSS SDK |
| langchain-ai/langgraph | ✓ | ✓ | ✓ | Release 1.2.16 (2026-10-16) verified via releases API |
| crewAIInc/crewAI | ✓ | ✓ | ✓ | — |
| microsoft/autogen | ✓ | ✓ | ✓ (legacy) | README shows **Archived / no longer maintained** banner despite `archived:false` in API — trust the README |
| SWE-agent/SWE-agent | ✓ | ✓ | ✓ | README: development moved to mini-swe-agent |

## Naming verification (2026-10-18)

- `actlet-agent`: **REJECTED** — taken on PyPI (200) and npm (200); 1,490 GitHub repos match `actlet-agent in:name`.
- Alternatives checked free on **both** PyPI and npm (404): `actletagent`, `actlet-ai-agent`, `actlet`, `vesta-agent`, `halcyon-agent`.
- `actlet` on GitHub: 18 name matches, all 0 stars — effectively free.
- **Decision: Actlet** — product name keeps the NOVA working identity; package/repo `actlet`.

## Dependency verification (2026-10-18)

- `BerriAI/litellm`: 61,458★, pushed 2026-10-18, not archived. License field `NOASSERTION` in API; project ships MIT LICENSE (re-verify at build time before release).
- Free-tier grounding: Groq free tier verified via multiple Oct-2026 sources (30 RPM, ~1k req/day, 100–500k tokens/day, no card, per-org limits); Gemini API free tier (5–15 RPM, 20–1,500 RPD, model-dependent); OpenRouter free models (20 RPM / 50 RPD, 1k RPD after $10 credit); **Cerebras has NO permanent free tier** (vendor FAQ; $5 trial credit, 30 days, card required); GitHub Models retired 2026-07-30; Together AI / DeepSeek / xAI offer no free tier. Treat aggregator numbers as dated snapshots — vendor docs are the source of truth.

## Known limitations of this research

- Read-only: no code cloned, no live installs, no runtime verification of claimed features.
- 6 repos lack API stats (rate limit); scored on README/docs evidence only, stats marked unknown.
- Star counts measure attention, not quality — the weighted ranking deliberately down-weights community (×0.75).
- Free-tier numbers change frequently; `docs/cost-model.md` carries check dates and a re-verification policy.
