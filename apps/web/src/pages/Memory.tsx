import React, { useCallback, useEffect, useRef, useState } from 'react'
import {
  Memory,
  MemoryImportEntry,
  addMemory,
  deleteMemory,
  exportMemories,
  getMemories,
  importMemories,
  updateMemory,
} from '../api'
import { formatTime } from './Tasks'

function parseTags(input: string): string[] {
  return input
    .split(',')
    .map((t) => t.trim())
    .filter((t) => t.length > 0)
}

function parseImport(text: string): MemoryImportEntry[] {
  let data: unknown
  try {
    data = JSON.parse(text)
  } catch {
    throw new Error('That is not valid JSON.')
  }
  const arr = Array.isArray(data)
    ? data
    : (data as { memories?: unknown }).memories
  if (!Array.isArray(arr)) {
    throw new Error('Expected a JSON array or {"memories": [...]}.')
  }
  return arr.map((m: unknown) => {
    const entry = m as { content?: unknown; tags?: unknown }
    if (!entry || typeof entry.content !== 'string' || !entry.content.trim()) {
      throw new Error('Each memory needs a non-empty "content" string.')
    }
    const tags = Array.isArray(entry.tags)
      ? entry.tags.filter((t): t is string => typeof t === 'string')
      : undefined
    return tags ? { content: entry.content, tags } : { content: entry.content }
  })
}

function MemoryCard({
  memory,
  onChanged,
}: {
  memory: Memory
  onChanged: () => void
}): React.ReactElement {
  const [editing, setEditing] = useState(false)
  const [confirmingDelete, setConfirmingDelete] = useState(false)
  const [editContent, setEditContent] = useState(memory.content)
  const [editTags, setEditTags] = useState(memory.tags.join(', '))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const save = useCallback(async () => {
    const content = editContent.trim()
    if (!content || busy) return
    setBusy(true)
    setError(null)
    try {
      await updateMemory(memory.id, content, parseTags(editTags))
      setEditing(false)
      onChanged()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save')
    } finally {
      setBusy(false)
    }
  }, [editContent, editTags, busy, memory.id, onChanged])

  const remove = useCallback(async () => {
    if (busy) return
    setBusy(true)
    setError(null)
    try {
      await deleteMemory(memory.id)
      onChanged()
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not delete')
      setConfirmingDelete(false)
    } finally {
      setBusy(false)
    }
  }, [busy, memory.id, onChanged])

  return (
    <li className="rounded-xl border border-zinc-800 bg-zinc-900/60 px-4 py-3">
      {editing ? (
        <div>
          <textarea
            value={editContent}
            onChange={(e) => setEditContent(e.target.value)}
            rows={3}
            disabled={busy}
            className="w-full resize-y rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 focus:border-zinc-500 focus:outline-none disabled:opacity-50"
          />
          <input
            value={editTags}
            onChange={(e) => setEditTags(e.target.value)}
            placeholder="tags, comma-separated"
            disabled={busy}
            className="mt-2 w-full rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none disabled:opacity-50"
          />
          <div className="mt-2 flex gap-2">
            <button
              onClick={() => void save()}
              disabled={busy || editContent.trim().length === 0}
              className="rounded-lg bg-zinc-100 px-3 py-1.5 text-sm font-medium text-zinc-900 transition hover:bg-white disabled:opacity-40"
            >
              {busy ? '…' : 'Save'}
            </button>
            <button
              onClick={() => {
                setEditing(false)
                setEditContent(memory.content)
                setEditTags(memory.tags.join(', '))
                setError(null)
              }}
              disabled={busy}
              className="rounded-lg px-3 py-1.5 text-sm text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 disabled:opacity-40"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div>
          <p className="whitespace-pre-wrap text-sm leading-relaxed text-zinc-100">{memory.content}</p>
          <div className="mt-2 flex flex-wrap items-center gap-2 text-xs text-zinc-500">
            {memory.tags.map((t) => (
              <span key={t} className="rounded-full bg-zinc-800 px-2 py-0.5 text-zinc-300">
                {t}
              </span>
            ))}
            <span>from {memory.source}</span>
            <span>·</span>
            <span>{formatTime(memory.updated_at)}</span>
            <span className="ml-auto flex gap-1">
              <button
                onClick={() => {
                  setEditing(true)
                  setConfirmingDelete(false)
                  setError(null)
                }}
                className="rounded-md px-2 py-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200"
              >
                Edit
              </button>
              {confirmingDelete ? (
                <>
                  <span className="self-center text-red-300">Delete permanently?</span>
                  <button
                    onClick={() => void remove()}
                    disabled={busy}
                    className="rounded-md bg-red-950 px-2 py-1 font-medium text-red-200 hover:bg-red-900 disabled:opacity-40"
                  >
                    {busy ? '…' : 'Yes, delete'}
                  </button>
                  <button
                    onClick={() => setConfirmingDelete(false)}
                    disabled={busy}
                    className="rounded-md px-2 py-1 text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200 disabled:opacity-40"
                  >
                    Keep
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setConfirmingDelete(true)}
                  className="rounded-md px-2 py-1 text-zinc-400 hover:bg-zinc-800 hover:text-red-300"
                >
                  Delete
                </button>
              )}
            </span>
          </div>
        </div>
      )}
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
    </li>
  )
}

export default function MemoryPage(): React.ReactElement {
  const [memories, setMemories] = useState<Memory[]>([])
  const [total, setTotal] = useState(0)
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)

  const [newContent, setNewContent] = useState('')
  const [newTags, setNewTags] = useState('')
  const [adding, setAdding] = useState(false)
  const [addError, setAddError] = useState<string | null>(null)
  const [addNote, setAddNote] = useState<string | null>(null)

  const [showImport, setShowImport] = useState(false)
  const [importText, setImportText] = useState('')
  const [importing, setImporting] = useState(false)
  const [importError, setImportError] = useState<string | null>(null)
  const [importResult, setImportResult] = useState<{
    added: number
    merged: number
    skipped: number
  } | null>(null)
  const [exporting, setExporting] = useState(false)
  const fileRef = useRef<HTMLInputElement>(null)

  const load = useCallback((q: string) => {
    setLoading(true)
    getMemories(q || undefined)
      .then((d) => {
        setMemories(d.memories)
        setTotal(d.total)
        setLoadError(null)
      })
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false))
  }, [])

  // Live search, debounced.
  useEffect(() => {
    const id = window.setTimeout(() => load(query.trim()), 300)
    return () => window.clearTimeout(id)
  }, [query, load])

  const add = useCallback(async () => {
    const content = newContent.trim()
    if (!content || adding) return
    setAdding(true)
    setAddError(null)
    setAddNote(null)
    try {
      const { merged } = await addMemory(content, parseTags(newTags))
      setNewContent('')
      setNewTags('')
      setAddNote(merged ? 'Merged with a memory Actlet already had.' : 'Remembered.')
      load(query.trim())
    } catch (e) {
      setAddError(e instanceof Error ? e.message : 'Could not save memory')
    } finally {
      setAdding(false)
    }
  }, [newContent, newTags, adding, load, query])

  const doExport = useCallback(async () => {
    if (exporting) return
    setExporting(true)
    setLoadError(null)
    try {
      const d = await exportMemories()
      const blob = new Blob([JSON.stringify({ memories: d.memories }, null, 2)], {
        type: 'application/json',
      })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = 'actlet-memories.json'
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.setTimeout(() => URL.revokeObjectURL(url), 1000)
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : 'Export failed')
    } finally {
      setExporting(false)
    }
  }, [exporting])

  const doImport = useCallback(
    async (text: string) => {
      if (importing) return
      setImporting(true)
      setImportError(null)
      setImportResult(null)
      try {
        const entries = parseImport(text)
        const r = await importMemories(entries)
        setImportResult(r)
        setImportText('')
        load(query.trim())
      } catch (e) {
        setImportError(e instanceof Error ? e.message : 'Import failed')
      } finally {
        setImporting(false)
      }
    },
    [importing, load, query],
  )

  const onFilePicked = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const f = e.target.files?.[0]
      e.target.value = '' // allow re-picking the same file
      if (!f) return
      const reader = new FileReader()
      reader.onload = () => void doImport(String(reader.result ?? ''))
      reader.onerror = () => setImportError('Could not read that file.')
      reader.readAsText(f)
    },
    [doImport],
  )

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col px-4 py-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-zinc-100">Memory</h1>
        <p className="mt-1 text-sm text-zinc-500">
          What Actlet remembers about you. Everything here is yours — readable, exportable, and
          deletable. Deleting a memory is permanent and honored everywhere.
        </p>
      </div>

      {/* Controls */}
      <div className="mb-4 flex flex-wrap items-center gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Search memories…"
          className="min-w-0 flex-1 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none"
        />
        <button
          onClick={() => void doExport()}
          disabled={exporting}
          className="rounded-xl border border-zinc-700 px-4 py-2.5 text-sm text-zinc-300 transition hover:bg-zinc-900 disabled:opacity-40"
          title="Download all memories as actlet-memories.json"
        >
          {exporting ? '…' : 'Export'}
        </button>
        <button
          onClick={() => setShowImport((v) => !v)}
          className={`rounded-xl border px-4 py-2.5 text-sm transition ${
            showImport
              ? 'border-zinc-500 bg-zinc-800 text-zinc-100'
              : 'border-zinc-700 text-zinc-300 hover:bg-zinc-900'
          }`}
        >
          Import
        </button>
      </div>

      {/* Import panel */}
      {showImport && (
        <div className="mb-4 rounded-xl border border-zinc-800 bg-zinc-900/60 px-4 py-3">
          <div className="flex flex-wrap items-center gap-2">
            <input
              ref={fileRef}
              type="file"
              accept="application/json,.json"
              onChange={onFilePicked}
              className="hidden"
            />
            <button
              onClick={() => fileRef.current?.click()}
              disabled={importing}
              className="rounded-lg bg-zinc-100 px-3 py-1.5 text-sm font-medium text-zinc-900 transition hover:bg-white disabled:opacity-40"
            >
              Choose JSON file
            </button>
            <span className="text-xs text-zinc-500">or paste JSON below</span>
          </div>
          <textarea
            value={importText}
            onChange={(e) => setImportText(e.target.value)}
            rows={3}
            placeholder='[{"content": "…", "tags": ["…"]}] or {"memories": [...]}'
            disabled={importing}
            className="slim-scroll mt-2 w-full resize-y rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 font-mono text-xs text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none disabled:opacity-50"
          />
          <div className="mt-2 flex items-center gap-2">
            <button
              onClick={() => void doImport(importText)}
              disabled={importing || importText.trim().length === 0}
              className="rounded-lg bg-zinc-100 px-3 py-1.5 text-sm font-medium text-zinc-900 transition hover:bg-white disabled:opacity-40"
            >
              {importing ? '…' : 'Import pasted JSON'}
            </button>
            {importResult && (
              <p className="text-sm text-zinc-300">
                Added {importResult.added}, merged {importResult.merged}, skipped{' '}
                {importResult.skipped}.
              </p>
            )}
          </div>
          {importError && <p className="mt-2 text-sm text-red-400">{importError}</p>}
        </div>
      )}

      {/* Add form */}
      <div className="mb-6 rounded-xl border border-zinc-800 bg-zinc-900/60 px-4 py-3">
        <textarea
          value={newContent}
          onChange={(e) => setNewContent(e.target.value)}
          rows={2}
          placeholder="Something Actlet should remember…"
          disabled={adding}
          className="w-full resize-y rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none disabled:opacity-50"
        />
        <div className="mt-2 flex gap-2">
          <input
            value={newTags}
            onChange={(e) => setNewTags(e.target.value)}
            placeholder="tags, comma-separated (optional)"
            disabled={adding}
            className="flex-1 rounded-lg border border-zinc-700 bg-zinc-900 px-3 py-2 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none disabled:opacity-50"
          />
          <button
            onClick={() => void add()}
            disabled={adding || newContent.trim().length === 0}
            className="shrink-0 rounded-lg bg-zinc-100 px-4 py-2 text-sm font-medium text-zinc-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            {adding ? '…' : 'Remember'}
          </button>
        </div>
        {addNote && <p className="mt-2 text-sm text-emerald-300">{addNote}</p>}
        {addError && <p className="mt-2 text-sm text-red-400">{addError}</p>}
      </div>

      {/* List */}
      <div className="slim-scroll min-h-0 flex-1 overflow-y-auto">
        {loading ? (
          <p className="py-10 text-center text-sm text-zinc-500">Loading memories…</p>
        ) : loadError ? (
          <div className="rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-200">
            <span className="font-medium">Couldn't load memories: </span>
            {loadError}
            <button
              onClick={() => load(query.trim())}
              className="ml-3 underline underline-offset-2 hover:text-red-100"
            >
              Retry
            </button>
          </div>
        ) : memories.length === 0 ? (
          <div className="py-16 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-800 text-2xl">
              🧠
            </div>
            <h2 className="text-lg font-medium text-zinc-200">
              {query.trim() ? 'No memories match that search' : "Actlet doesn't remember anything yet."}
            </h2>
            <p className="mx-auto mt-2 max-w-sm text-sm text-zinc-500">
              {query.trim()
                ? 'Try a different search, or clear it to see everything.'
                : 'Add one above, or ask Actlet to remember this conversation from the chat header.'}
            </p>
          </div>
        ) : (
          <>
            <p className="mb-2 text-xs text-zinc-500">
              {total} {total === 1 ? 'memory' : 'memories'}
              {query.trim() ? ` matching "${query.trim()}"` : ''}
            </p>
            <ul className="space-y-2 pb-4">
              {memories.map((m) => (
                <MemoryCard key={m.id} memory={m} onChanged={() => load(query.trim())} />
              ))}
            </ul>
          </>
        )}
      </div>
    </div>
  )
}
