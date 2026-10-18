import React, { useCallback, useEffect, useState } from 'react'
import { TaskStatus, TaskSummary, createTask, getTasks } from '../api'

export const STATUS_STYLES: Record<TaskStatus, string> = {
  pending: 'bg-zinc-800 text-zinc-300',
  running: 'bg-blue-950 text-blue-300',
  waiting_approval: 'bg-amber-950 text-amber-300',
  paused: 'bg-orange-950 text-orange-300',
  failed: 'bg-red-950 text-red-300',
  completed: 'bg-emerald-950 text-emerald-300',
  cancelled: 'bg-zinc-800 text-zinc-500',
}

export function statusLabel(status: TaskStatus): string {
  return status.replace(/_/g, ' ')
}

export function formatTime(iso: string): string {
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString()
}

export function StatusPill({ status }: { status: TaskStatus }): React.ReactElement {
  return (
    <span
      className={`inline-block shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${STATUS_STYLES[status] ?? STATUS_STYLES.pending}`}
    >
      {statusLabel(status)}
    </span>
  )
}

interface TasksProps {
  onOpenTask: (id: string) => void
}

export default function Tasks({ onOpenTask }: TasksProps): React.ReactElement {
  const [tasks, setTasks] = useState<TaskSummary[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [goal, setGoal] = useState('')
  const [creating, setCreating] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  const refresh = useCallback(() => {
    setLoading(true)
    getTasks()
      .then((d) => {
        setTasks(d.tasks)
        setLoadError(null)
      })
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const create = useCallback(async () => {
    const text = goal.trim()
    if (!text || creating) return
    setCreating(true)
    setCreateError(null)
    try {
      const { id } = await createTask(text)
      setGoal('')
      onOpenTask(id)
    } catch (e) {
      setCreateError(e instanceof Error ? e.message : 'Could not create task')
    } finally {
      setCreating(false)
    }
  }, [goal, creating, onOpenTask])

  const onKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      e.preventDefault()
      void create()
    }
  }

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col px-4 py-6">
      <div className="mb-6">
        <h1 className="text-xl font-semibold text-zinc-100">Tasks</h1>
        <p className="mt-1 text-sm text-zinc-500">
          Delegate an outcome. Actlet plans, acts, and verifies — asking for approval before
          anything consequential.
        </p>
      </div>

      {/* New task */}
      <div className="mb-6">
        <div className="flex gap-2">
          <input
            value={goal}
            onChange={(e) => setGoal(e.target.value)}
            onKeyDown={onKeyDown}
            placeholder="e.g. Research the best noise-cancelling headphones under $300 and summarize with sources"
            disabled={creating}
            className="flex-1 rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none disabled:opacity-50"
          />
          <button
            onClick={() => void create()}
            disabled={creating || goal.trim().length === 0}
            className="shrink-0 rounded-xl bg-zinc-100 px-4 py-2.5 text-sm font-medium text-zinc-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40"
          >
            {creating ? '…' : 'Create'}
          </button>
        </div>
        {createError && <p className="mt-2 text-sm text-red-400">{createError}</p>}
      </div>

      {/* List */}
      <div className="slim-scroll min-h-0 flex-1 overflow-y-auto">
        {loading ? (
          <p className="py-10 text-center text-sm text-zinc-500">Loading tasks…</p>
        ) : loadError ? (
          <div className="rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-200">
            <span className="font-medium">Couldn't load tasks: </span>
            {loadError}
            <button
              onClick={refresh}
              className="ml-3 underline underline-offset-2 hover:text-red-100"
            >
              Retry
            </button>
          </div>
        ) : tasks.length === 0 ? (
          <div className="py-16 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-800 text-2xl">
              ✓
            </div>
            <h2 className="text-lg font-medium text-zinc-200">No tasks yet</h2>
            <p className="mx-auto mt-2 max-w-sm text-sm text-zinc-500">
              Describe an outcome above and Actlet will break it into steps, run them, and check
              its own work.
            </p>
          </div>
        ) : (
          <ul className="space-y-2">
            {tasks.map((t) => (
              <li key={t.id}>
                <button
                  onClick={() => onOpenTask(t.id)}
                  className="block w-full rounded-xl border border-zinc-800 bg-zinc-900/60 px-4 py-3 text-left transition hover:border-zinc-700 hover:bg-zinc-900"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="min-w-0 flex-1 truncate text-sm font-medium text-zinc-100" title={t.goal}>
                      {t.goal}
                    </p>
                    <StatusPill status={t.status} />
                  </div>
                  <div className="mt-2 flex items-center gap-4 text-xs text-zinc-500">
                    <span>
                      Step {t.current_step}/{t.total_steps}
                    </span>
                    <span>Updated {formatTime(t.updated_at)}</span>
                  </div>
                  {t.total_steps > 0 && (
                    <div className="mt-2 h-1 overflow-hidden rounded-full bg-zinc-800">
                      <div
                        className="h-full rounded-full bg-zinc-400 transition-all"
                        style={{ width: `${Math.min(100, (t.current_step / t.total_steps) * 100)}%` }}
                      />
                    </div>
                  )}
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
