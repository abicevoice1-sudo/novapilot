import React, { useCallback, useEffect, useState } from 'react'
import {
  DreamResult,
  Skill,
  createSkill,
  deleteSkill,
  exportSkill,
  getSkills,
  importSkill,
  runDreaming,
} from '../api'

const inputCls =
  'w-full rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none disabled:opacity-50'
const btnPrimary =
  'rounded-xl bg-zinc-100 px-4 py-2.5 text-sm font-medium text-zinc-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40'
const btnGhost =
  'rounded-xl border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 transition hover:border-zinc-500 hover:text-zinc-100 disabled:cursor-not-allowed disabled:opacity-40'

function parseTools(s: string): string[] {
  return s.split(',').map((t) => t.trim()).filter(Boolean)
}

function SkillForm({
  onCreated,
  onCancel,
  busy,
  error,
  setBusy,
  setError,
}: {
  onCreated: (s: Skill) => void
  onCancel: () => void
  busy: boolean
  error: string | null
  setBusy: (b: boolean) => void
  setError: (e: string | null) => void
}): React.ReactElement {
  const [name, setName] = useState('')
  const [description, setDescription] = useState('')
  const [instructions, setInstructions] = useState('')
  const [tools, setTools] = useState('')

  const submit = async () => {
    setBusy(true)
    setError(null)
    try {
      onCreated(
        await createSkill({
          name: name.trim(),
          description: description.trim(),
          instructions: instructions.trim(),
          tools: parseTools(tools),
        }),
      )
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not create skill')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-4">
      <div className="grid gap-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Skill name — e.g. weekly-flight-check"
          disabled={busy}
          className={inputCls}
        />
        <input
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          placeholder="One-line description of what this skill does"
          disabled={busy}
          className={inputCls}
        />
        <textarea
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          placeholder="Instructions the agent follows when using this skill…"
          disabled={busy}
          rows={5}
          className={`${inputCls} resize-y font-mono`}
        />
        <input
          value={tools}
          onChange={(e) => setTools(e.target.value)}
          placeholder="web_fetch, browser_open  (optional, comma-separated)"
          disabled={busy}
          className={`${inputCls} font-mono`}
        />
      </div>
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      <div className="mt-3 flex gap-2">
        <button
          onClick={() => void submit()}
          disabled={busy || !name.trim() || !description.trim() || !instructions.trim()}
          className={btnPrimary}
        >
          {busy ? '…' : 'Create skill'}
        </button>
        <button onClick={onCancel} disabled={busy} className={btnGhost}>
          Cancel
        </button>
      </div>
    </div>
  )
}

function SkillCard({
  skill,
  onDeleted,
}: {
  skill: Skill
  onDeleted: (name: string) => void
}): React.ReactElement {
  const [expanded, setExpanded] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [busy, setBusy] = useState(false)
  const [exporting, setExporting] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const remove = async () => {
    setBusy(true)
    try {
      await deleteSkill(skill.name)
      onDeleted(skill.name)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not delete skill')
      setBusy(false)
      setConfirmDelete(false)
    }
  }

  const exportIt = async () => {
    setExporting(true)
    setError(null)
    try {
      const exp = await exportSkill(skill.name)
      const blob = new Blob([exp.content], { type: 'text/markdown' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = exp.filename || `${skill.name}.md`
      document.body.appendChild(a)
      a.click()
      a.remove()
      URL.revokeObjectURL(url)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not export skill')
    } finally {
      setExporting(false)
    }
  }

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 px-4 py-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="truncate font-mono text-sm font-medium text-zinc-100">{skill.name}</h3>
            <span
              title="Times this skill has been used"
              className="shrink-0 rounded-full bg-zinc-800 px-2 py-0.5 text-xs text-zinc-400"
            >
              used {skill.use_count}×
            </span>
          </div>
          <p className="mt-1 text-sm text-zinc-400">{skill.description}</p>
          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            {skill.tools.length === 0 ? (
              <span className="text-xs italic text-zinc-600">no tools bound</span>
            ) : (
              skill.tools.map((t) => (
                <span key={t} className="rounded-full bg-zinc-800 px-2 py-0.5 font-mono text-xs text-zinc-300">
                  {t}
                </span>
              ))
            )}
          </div>
          {skill.created_from.length > 0 && (
            <p className="mt-2 text-xs text-zinc-500">
              learned from: {skill.created_from.map((id) => id.slice(0, 8)).join(', ')}
            </p>
          )}
          {expanded && (
            <pre className="slim-scroll mt-3 max-h-64 overflow-auto whitespace-pre-wrap rounded-lg bg-zinc-950 p-3 text-xs text-zinc-300">
              {skill.instructions}
            </pre>
          )}
        </div>
        <div className="flex shrink-0 flex-col gap-1.5">
          <button onClick={() => setExpanded((v) => !v)} disabled={busy} className={btnGhost}>
            {expanded ? 'Hide' : 'View'}
          </button>
          <button onClick={() => void exportIt()} disabled={busy || exporting} className={btnGhost}>
            {exporting ? '…' : 'Export'}
          </button>
          {confirmDelete ? (
            <button
              onClick={() => void remove()}
              disabled={busy}
              className="rounded-xl border border-red-800 bg-red-950 px-3 py-1.5 text-sm text-red-200 transition hover:bg-red-900 disabled:opacity-40"
            >
              Yes, delete
            </button>
          ) : (
            <button onClick={() => setConfirmDelete(true)} disabled={busy} className={btnGhost}>
              Delete
            </button>
          )}
        </div>
      </div>
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
    </div>
  )
}

export default function Skills(): React.ReactElement {
  const [skills, setSkills] = useState<Skill[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [busy, setBusy] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)
  const [dreamBusy, setDreamBusy] = useState(false)
  const [dreamResult, setDreamResult] = useState<DreamResult | null>(null)
  const [dreamError, setDreamError] = useState<string | null>(null)
  const [importing, setImporting] = useState(false)
  const [importText, setImportText] = useState('')
  const [importBusy, setImportBusy] = useState(false)
  const [importError, setImportError] = useState<string | null>(null)

  const refresh = useCallback(() => {
    setLoading(true)
    getSkills()
      .then((d) => {
        setSkills(d.skills)
        setLoadError(null)
      })
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const dream = async () => {
    setDreamBusy(true)
    setDreamResult(null)
    setDreamError(null)
    try {
      setDreamResult(await runDreaming())
    } catch (e) {
      setDreamError(e instanceof Error ? e.message : 'Dreaming failed')
    } finally {
      setDreamBusy(false)
    }
  }

  const doImport = async () => {
    setImportBusy(true)
    setImportError(null)
    try {
      const s = await importSkill(importText)
      setSkills((prev) => [s, ...prev.filter((x) => x.name !== s.name)])
      setImportText('')
      setImporting(false)
    } catch (e) {
      setImportError(e instanceof Error ? e.message : 'Could not import skill')
    } finally {
      setImportBusy(false)
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col px-4 py-6">
      <div className="mb-6 flex items-start justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">Skills</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Reusable know-how Actlet has learned. Skills can be distilled from completed tasks
            or written by hand — and dreaming turns recent tasks into lasting memory.
          </p>
        </div>
        <div className="flex shrink-0 gap-2">
          <button onClick={() => void dream()} disabled={dreamBusy} className={btnGhost} title="Run dreaming consolidation now — Actlet reviews recent tasks and stores lasting facts to memory">
            {dreamBusy ? 'Dreaming…' : '🌙 Run dreaming now'}
          </button>
          <button onClick={() => { setImportError(null); setImporting(true) }} className={btnGhost}>
            ⤓ Import skill
          </button>
          {!creating && (
            <button onClick={() => setCreating(true)} className={btnPrimary}>
              + New skill
            </button>
          )}
        </div>
      </div>

      {importing && (
        <div className="mb-6 rounded-xl border border-zinc-700 bg-zinc-900/80 p-4">
          <h2 className="text-sm font-medium text-zinc-200">Import skill</h2>
          <p className="mt-1 text-xs text-zinc-500">
            Paste the exported SKILL.md content below. It must include the name and instructions.
          </p>
          <textarea
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            placeholder={'---\nname: weekly-flight-check\ndescription: …\n---\n\nInstructions…'}
            disabled={importBusy}
            rows={10}
            className={`${inputCls} slim-scroll mt-3 resize-y font-mono`}
          />
          {importError && <p className="mt-2 text-sm text-red-400">{importError}</p>}
          <div className="mt-3 flex gap-2">
            <button
              onClick={() => void doImport()}
              disabled={importBusy || !importText.trim()}
              className={btnPrimary}
            >
              {importBusy ? '…' : 'Import'}
            </button>
            <button
              onClick={() => { setImporting(false); setImportText(''); setImportError(null) }}
              disabled={importBusy}
              className={btnGhost}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {dreamResult && (
        <div className="mb-4 rounded-xl border border-emerald-900/50 bg-emerald-950/40 px-4 py-3">
          <p className="text-sm text-emerald-200">
            Dreaming complete — {dreamResult.tasks_considered}{' '}
            {dreamResult.tasks_considered === 1 ? 'task' : 'tasks'} considered,{' '}
            {dreamResult.facts_stored} {dreamResult.facts_stored === 1 ? 'fact' : 'facts'} stored.
          </p>
          {dreamResult.facts.length > 0 && (
            <ul className="mt-2 space-y-1">
              {dreamResult.facts.map((f) => (
                <li key={f.id} className="text-sm text-zinc-300">
                  <span className="mr-2 text-emerald-400">✦</span>
                  {f.content}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
      {dreamError && (
        <div className="mb-4 rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-200">
          <span className="font-medium">Dreaming failed: </span>
          {dreamError}
        </div>
      )}

      {creating && (
        <div className="mb-6">
          <SkillForm
            onCreated={(s) => {
              setSkills((prev) => [s, ...prev])
              setCreating(false)
            }}
            onCancel={() => {
              setCreating(false)
              setCreateError(null)
            }}
            busy={busy}
            error={createError}
            setBusy={setBusy}
            setError={setCreateError}
          />
        </div>
      )}

      <div className="slim-scroll min-h-0 flex-1 overflow-y-auto">
        {loading ? (
          <p className="py-10 text-center text-sm text-zinc-500">Loading skills…</p>
        ) : loadError ? (
          <div className="rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-200">
            <span className="font-medium">Couldn't load skills: </span>
            {loadError}
            <button onClick={refresh} className="ml-3 underline underline-offset-2 hover:text-red-100">
              Retry
            </button>
          </div>
        ) : skills.length === 0 && !creating ? (
          <div className="py-16 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-800 text-2xl">
              🧠
            </div>
            <h2 className="text-lg font-medium text-zinc-200">No skills yet</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-zinc-500">
              Finish a task worth repeating, then distill it into a skill from the task page —
              or write one by hand.
            </p>
          </div>
        ) : (
          <ul className="space-y-2">
            {skills.map((s) => (
              <li key={s.name}>
                <SkillCard skill={s} onDeleted={(n) => setSkills((prev) => prev.filter((x) => x.name !== n))} />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
