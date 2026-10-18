import React, { useEffect, useState } from 'react'
import { Health, getHealth, getModels, getToken, setToken } from '../api'

export default function Settings(): React.ReactElement {
  const [health, setHealth] = useState<Health | null>(null)
  const [healthError, setHealthError] = useState<string | null>(null)
  const [defaultModel, setDefaultModel] = useState<string>('')
  const [tokenInput, setTokenInput] = useState(getToken())
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    getHealth()
      .then((h) => {
        setHealth(h)
        setHealthError(null)
      })
      .catch((e: Error) => setHealthError(e.message))
    getModels()
      .then((d) => setDefaultModel(d.default))
      .catch(() => setDefaultModel(''))
  }, [])

  const saveToken = () => {
    setToken(tokenInput.trim())
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  const clearToken = () => {
    setTokenInput('')
    setToken('')
    setSaved(true)
    setTimeout(() => setSaved(false), 2000)
  }

  return (
    <div className="slim-scroll h-full overflow-y-auto">
      <div className="mx-auto max-w-2xl px-4 py-8">
        <h1 className="text-xl font-semibold text-zinc-100">Settings</h1>

        {/* Backend health */}
        <section className="mt-6 rounded-xl border border-zinc-800 bg-zinc-900/60 p-5">
          <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-400">Backend</h2>
          {healthError ? (
            <p className="mt-3 text-sm text-red-300">
              <span className="font-medium">Unreachable:</span> {healthError}
            </p>
          ) : !health ? (
            <p className="mt-3 text-sm text-zinc-500">Checking backend health…</p>
          ) : (
            <dl className="mt-3 space-y-1.5 text-sm">
              <div className="flex gap-2">
                <dt className="w-28 shrink-0 text-zinc-500">Status</dt>
                <dd className={health.ok ? 'text-emerald-300' : 'text-red-300'}>
                  {health.ok ? '● healthy' : '● unhealthy'}
                </dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-28 shrink-0 text-zinc-500">Service</dt>
                <dd className="text-zinc-200">{health.service}</dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-28 shrink-0 text-zinc-500">Milestone</dt>
                <dd className="text-zinc-200">{health.milestone}</dd>
              </div>
              <div className="flex gap-2">
                <dt className="w-28 shrink-0 text-zinc-500">Default model</dt>
                <dd className="font-mono text-xs text-zinc-200">{defaultModel || health.model_default}</dd>
              </div>
            </dl>
          )}
        </section>

        {/* Model gateway */}
        <section className="mt-4 rounded-xl border border-zinc-800 bg-zinc-900/60 p-5">
          <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-400">Model gateway</h2>
          <p className="mt-3 text-sm leading-relaxed text-zinc-300">
            Ollama default · Groq / Gemini / OpenRouter fallbacks.
          </p>
          <p className="mt-2 text-xs leading-relaxed text-zinc-500">
            The gateway routes each request, fails over on rate limits, and enforces per-task
            token, cost, and time budgets. Nothing spends money without a key you configured.
          </p>
        </section>

        {/* Auth token */}
        <section className="mt-4 rounded-xl border border-zinc-800 bg-zinc-900/60 p-5">
          <h2 className="text-sm font-medium uppercase tracking-wide text-zinc-400">API token</h2>
          <p className="mt-3 text-sm text-zinc-400">
            Sent as <code className="rounded bg-zinc-800 px-1 font-mono text-xs">Authorization: Bearer</code> on
            every request. Leave empty for open dev access. Stored only in this browser's
            localStorage.
          </p>
          <div className="mt-3 flex gap-2">
            <input
              type="password"
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              placeholder="Optional bearer token"
              autoComplete="off"
              className="flex-1 rounded-lg border border-zinc-700 bg-zinc-950 px-3 py-2 font-mono text-sm text-zinc-100 placeholder-zinc-600 focus:border-zinc-500 focus:outline-none"
            />
            <button
              onClick={saveToken}
              className="rounded-lg bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-900 hover:bg-white"
            >
              Save
            </button>
            <button
              onClick={clearToken}
              className="rounded-lg border border-zinc-700 px-4 py-2 text-sm text-zinc-300 hover:bg-zinc-800"
            >
              Clear
            </button>
          </div>
          {saved && <p className="mt-2 text-xs text-emerald-300">Saved.</p>}
        </section>
      </div>
    </div>
  )
}
