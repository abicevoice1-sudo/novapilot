# NovaPilot — Cost model

**Principle:** the default experience works with $0 of API spend. Paid keys are an upgrade, never a requirement. Free tiers change often — every number below carries its check date; re-verify against the vendor's own rate-limit page before depending on it.

## What works with no key at all

- **Ollama (local inference)** — the zero-cost floor. `ollama pull gpt-oss:20b && ollama serve` exposes an OpenAI-compatible endpoint on localhost; NovaPilot points at it with one env var. No rate limit, no key, prompts never leave the machine. 20B-class models run acceptably on a 16 GB machine; 120B-class wants an 80 GB GPU or a large unified-memory Mac (checked 2026-10-18).
- **Web research** — RSS feeds, sitemaps, and direct public web access (with safeguards) cost nothing. Wikipedia/Wikidata-style public APIs are free within their terms.
- **Everything local** — memory, scheduler, file tools, browser automation against localhost, audit logs.

## Verified free API tiers (checked 2026-10-18; vendor docs are the source of truth)

| Provider | Free allowance (reported Oct 2026) | Card? | Notes |
|----------|-----------------------------------|-------|-------|
| **Groq** | 30 req/min; ~1,000 req/day; 100K–500K tokens/day by model (gpt-oss-120b/20b, qwen3.x, llama-3.1-8b, llama-3.3-70b, whisper) | No | Limits are **per organization, not per key**. Token ceiling binds before request count for agent workloads. |
| **Google AI Studio (Gemini API)** | ~5–15 req/min; 20–1,500 req/day model-dependent (Flash models free) | No | Best free long-context option (up to 1M ctx on some models). |
| **OpenRouter** | 20+ free models; 20 req/min, 50 req/day; 1,000 req/day after $10 credit purchase | No | Useful as a free-model aggregator behind our gateway. |
| **Mistral La Plateforme** | Free plan exists; amount unstated on pricing page (previously ~$10/mo credits) | — | Verify current terms before depending on it. |
| **Cerebras** | **No permanent free tier** (vendor FAQ). $5 trial credit, expires 30 days, verified payment method required; trial limits 5 req/min, 30K tokens/min, 1M tokens/day/model | Yes (trial) | Do not design around Cerebras as "free". |
| GitHub Models | **Retired 2026-07-30** | — | Gone. |
| Together AI / DeepSeek / xAI | No free tier offered | — | — |

## Recommended $0 configurations

1. **Fully local** — Ollama (`gpt-oss:20b`) for everything. $0 forever; quality ceiling is the local model.
2. **Free-cloud router** — LiteLLM gateway with fallback chain Groq → Gemini → OpenRouter-free → Ollama. Stays inside free quotas for personal use; 429s fail over automatically.
3. **Hybrid (recommended default)** — small local model for routing/classification/extraction; free-cloud frontier-ish models for hard reasoning; local for private data.

## Estimated costs

| Usage | Shape | Est. monthly cost |
|-------|-------|-------------------|
| Light | ~30 min chat/day + a few scheduled checks, free-tier router | **$0** |
| Medium | Daily research reports, browser tasks, background jobs; free tiers + occasional paid fallback | **$0–5** (paid fallback: Groq dev tier ≈ $0.05–0.15/MTok input) |
| Heavy | Always-on automations, long browser sessions, big context | **$10–40** — at this point a $10–20 paid tier beats free-tier rate limits |

Hardware: any 8 GB+ machine runs the stack; local 20B models want 16 GB RAM; Docker required for sandboxed tools. Hosting: $0 local; ~$6/mo VPS if always-on remote (agent-zero's documented floor).

## Quota exhaustion behavior

When a provider 429s, the gateway fails over to the next route. When **all** routes are exhausted, the task pauses (not fails): state is checkpointed, the user sees "quota exhausted — resumes automatically" with per-provider reset times, and scheduled jobs retry with backoff. Nothing silently degrades, nothing spends money without an explicit paid key configured.
