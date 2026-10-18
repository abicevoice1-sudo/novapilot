# Free LLM Providers for Actlet

**Verified October 2026** via live provider docs. Free tiers change constantly —
if one stops working, remove it from `MODEL_FALLBACKS` and open an issue.

All of these work with Actlet because the gateway is LiteLLM underneath:
set the key, add the model ID to `MODEL_FALLBACKS`, done.

## $0 forever, no key, no signup

| Provider | Model ID | Notes |
|----------|----------|-------|
| Ollama (local) | `ollama/gpt-oss:20b` | Default. Runs on your machine. Unlimited. |

## Permanent free tiers, no credit card

| Provider | Model ID | Free allowance | Key env var | Signup |
|----------|----------|----------------|-------------|--------|
| Groq | `groq/gpt-oss-120b` | 30 req/min, 1k req/day | `GROQ_API_KEY` | console.groq.com |
| Google AI Studio | `gemini/gemini-2.5-flash` | ~1,500 req/day | `GEMINI_API_KEY` | aistudio.google.com |
| OpenRouter | `openrouter/qwen/qwen3-32b:free` | 50 req/day (`:free` models) | `OPENROUTER_API_KEY` | openrouter.ai |
| Cerebras | `cerebras/llama-3.3-70b` | ~1M tokens/day | `CEREBRAS_API_KEY` | cerebras.ai |
| Mistral | `mistral/mistral-small-latest` | Experiment tier | `MISTRAL_API_KEY` | console.mistral.ai |
| NVIDIA NIM | `nvidia_nim/nvidia/llama-3.1-nemotron-70b-instruct` | Free tier @ build.nvidia.com | `NVIDIA_API_KEY` | build.nvidia.com |
| Cloudflare | `cloudflare/@cf/meta/llama-3.1-8b-instruct` | 10k neurons/day | `CLOUDFLARE_API_KEY` + `CLOUDFLARE_ACCOUNT_ID` | dash.cloudflare.com |
| Cohere | `cohere/command-r-plus` | ~1k calls/month trial | `COHERE_API_KEY` | dashboard.cohere.com |

## Free credits / trials (generous, then paid)

| Provider | Model ID | Free allowance | Key env var |
|----------|----------|----------------|-------------|
| HuggingFace | `huggingface/meta-llama/Llama-3.3-70B-Instruct` | Rate-limited free | `HF_TOKEN` |
| Together AI | `together_ai/meta-llama/Llama-3.3-70B-Instruct-Turbo` | Free credits on signup | `TOGETHER_API_KEY` |
| Fireworks AI | `fireworks_ai/accounts/fireworks/models/llama-v3p3-70b-instruct` | Free credits on signup | `FIREWORKS_API_KEY` |
| Zhipu (Z.ai) | `zhipu/glm-4-flash` | Free GLM Flash | `ZHIPU_API_KEY` |
| Reka | `reka/reka-flash` | $10/month recurring | `REKA_API_KEY` |

## Anonymous / no-signup (rate-limited, can disappear)

| Provider | Notes |
|----------|-------|
| Pollinations | `https://text.pollinations.ai` — OpenAI-compatible, no key |
| LLM7 | Anonymous `:free`-style routes |
| OVH AI Endpoints | ~2 req/min anonymous |

## Dead — do NOT use

| Provider | Status |
|----------|--------|
| GitHub Models | **Retired July 2026** |

## Recommended fallback chain ($0)

```
MODEL_FALLBACKS=groq/gpt-oss-120b,gemini/gemini-2.5-flash,cerebras/llama-3.3-70b,openrouter/qwen/qwen3-32b:free
```

This gives you four independent free providers. If one is down or rate-limited,
the gateway tries the next automatically.

## Honest note

There are not 50 legitimate free LLM API providers. Anyone selling you a list
of 50 is padding it with dead services, resellers, or scams. The ~20 above are
the real ones as of October 2026.
