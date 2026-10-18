import React, { useCallback, useEffect, useRef, useState } from 'react'
import type { TaskDetail, TaskEvent, TaskStatus, TaskStep } from '../api'
import { approveTask, cancelTask, getTask, pauseTask, resumeTask, streamTaskEvents } from '../api'
import { StatusPill, formatTime } from './Tasks'

const EVENT_META: Record<string, { icon: string; label: string; tone: string }> = {
  task_started: { icon: '▶', label: 'Task started', tone: 'text-zinc-300' },
  plan_created: { icon: '🗺', label: 'Plan created', tone: 'text-zinc-300' },
  step_started: { icon: '▸', label: 'Step started', tone: 'text-blue-300' },
  tool_called: { icon: '🔧', label: 'Tool called', tone: 'text-zinc-300' },
  tool_result: { icon: '📥', label: 'Tool result', tone: 'text-zinc-400' },
  approval_required: { icon: '⚠', label: 'Approval required', tone: 'text-amber-300' },
  approval_decided: { icon: '✓', label: 'Approval decided', tone: 'text-zinc-300' },
  step_verified: { icon: '✓', label: 'Step verified', tone: 'text-emerald-300' },
  budget_exceeded: { icon: '💰', label: 'Budget exceeded', tone: 'text-orange-300' },
  task_paused: { icon: '⏸', label: 'Task paused', tone: 'text-orange-300' },
  task_completed: { icon: '✅', label: 'Task completed', tone: 'text-emerald-300' },
  task_failed: { icon: '❌', label: 'Task failed', tone: 'text-red-300' },
  task_cancelled: { icon: '🚫', label: 'Task cancelled', tone: 'text-zinc-400' },
}

function eventMeta(type: string): { icon: string; label: string; tone: string } {
  return EVENT_META[type] ?? { icon: '•', label: type.replace(/_/g, ' '), tone: 'text-zinc-400' }
}

function eventSummary(evt: TaskEvent): string {
  const s = evt.step
  switch (evt.type) {
    case 'plan_created':
      return `${evt.steps?.length ?? 0} steps planned`
    case 'step_started':
    case 'approval_required':
      return s?.description ?? ''
    case 'tool_called':
      return `${s?.tool ?? 'tool'}${s?.description ? ` — ${s.description}` : ''}`
    case 'tool_result':
      return (s?.result ?? '').slice(0, 160)
    case 'approval_decided':
      return evt.approved ? 'Approved — continuing' : 'Rejected — stopping'
    case 'step_verified':
      return s?.description ?? ''
    case 'budget_exceeded':
    case 'task_failed':
      return (evt.error as string) ?? (evt.message as string) ?? ''
    case 'task_paused':
      return (evt.message as string) ?? ''
    default:
      return (evt.message as string) ?? ''
  }
}

interface TaskDetailProps {
  id: string
  onBack: () => void
}

interface FeedEntry {
  key: number
  evt: TaskEvent
  at: Date
}

const TERMINAL: TaskStatus[] = ['completed', 'failed', 'cancelled']

export default function TaskDetail({ id, onBack }: TaskDetailProps): React.ReactElement {
  const [detail, setDetail] = useState<TaskDetail | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [feed, setFeed] = useState<FeedEntry[]>([])
  const [streamError, setStreamError] = useState<string | null>(null)
  const [pendingApproval, setPendingApproval] = useState<TaskStep | null>(null)
  const [acting, setActing] = useState(false)
  const [actionError, setActionError] = useState<string | null>(null)

  const feedRef = useRef<HTMLDivElement>(null)
  const keyRef = useRef(0)
  const detailRef = useRef<TaskDetail | null>(null)
  detailRef.current = detail

  const applyEvent = useCallback((evt: TaskEvent) => {
    setFeed((prev) => [...prev, { key: keyRef.current++, evt, at: new Date() }])
    if (evt.type === 'approval_required' && evt.step) setPendingApproval(evt.step)
    if (
      evt.type === 'approval_decided' ||
      evt.type === 'task_completed' ||
      evt.type === 'task_failed' ||
      evt.type === 'task_cancelled'
    ) {
      setPendingApproval(null)
    }
    setDetail((prev) => {
      if (!prev) return prev
      const next: TaskDetail = { ...prev, steps: prev.steps.map((s) => ({ ...s })) }
      const upsertStep = (step: TaskStep) => {
        const i = next.steps.findIndex((s) => s.id === step.id)
        if (i >= 0) next.steps[i] = { ...next.steps[i], ...step }
        else next.steps.push(step)
      }
      switch (evt.type) {
        case 'task_started':
          next.status = 'running'
          break
        case 'plan_created':
          if (evt.steps) next.steps = evt.steps.map((s) => ({ ...s }))
          break
        case 'step_started':
        case 'tool_called':
        case 'tool_result':
        case 'step_verified':
          if (evt.step) upsertStep(evt.step)
          break
        case 'approval_required':
          next.status = 'waiting_approval'
          break
        case 'approval_decided':
          if (next.status === 'waiting_approval') next.status = 'running'
          break
        case 'budget_exceeded':
        case 'task_paused':
          next.status = 'paused'
          if (evt.error) next.error = String(evt.error)
          else if (evt.message) next.error = String(evt.message)
          break
        case 'task_completed':
          next.status = 'completed'
          if (evt.usage) next.usage = evt.usage
          break
        case 'task_failed':
          next.status = 'failed'
          if (evt.error) next.error = String(evt.error)
          break
        case 'task_cancelled':
          next.status = 'cancelled'
          break
        default:
          break
      }
      return next
    })
  }, [])

  // Load snapshot, then attach the live (replay + stream) event feed.
  useEffect(() => {
    let cancelled = false
    const abort = new AbortController()
    setDetail(null)
    setFeed([])
    setPendingApproval(null)
    setLoadError(null)
    setStreamError(null)
    keyRef.current = 0

    getTask(id)
      .then((d) => {
        if (cancelled) return
        setDetail(d)
        if (d.pending_approval) {
          const p = d.pending_approval
          setPendingApproval({ ...p, status: 'waiting_approval', result: null })
        } else if (d.status === 'waiting_approval') {
          const awaiting = d.steps.find((s) => s.status === 'waiting_approval')
          if (awaiting) setPendingApproval(awaiting)
        }
        return streamTaskEvents(id, applyEvent, abort.signal)
      })
      .catch((e: Error) => {
        if (cancelled) return
        if (detailRef.current) setStreamError(e.message)
        else setLoadError(e.message)
      })

    return () => {
      cancelled = true
      abort.abort()
    }
  }, [id, applyEvent])

  // Auto-scroll the feed.
  useEffect(() => {
    const el = feedRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [feed])

  const runAction = useCallback(
    async (fn: () => Promise<{ status: TaskStatus }>, label: string) => {
      setActing(true)
      setActionError(null)
      try {
        const { status } = await fn()
        setDetail((prev) => (prev ? { ...prev, status } : prev))
        if (status !== 'waiting_approval') setPendingApproval(null)
      } catch (e) {
        setActionError(`${label} failed: ${e instanceof Error ? e.message : 'unknown error'}`)
      } finally {
        setActing(false)
      }
    },
    [],
  )

  if (loadError) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-6">
        <button onClick={onBack} className="mb-4 text-sm text-zinc-400 hover:text-zinc-200">
          ← All tasks
        </button>
        <div className="rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-200">
          <span className="font-medium">Couldn't load task: </span>
          {loadError}
        </div>
      </div>
    )
  }

  if (!detail) {
    return (
      <div className="mx-auto max-w-4xl px-4 py-6">
        <button onClick={onBack} className="mb-4 text-sm text-zinc-400 hover:text-zinc-200">
          ← All tasks
        </button>
        <p className="py-10 text-center text-sm text-zinc-500">Loading task…</p>
      </div>
    )
  }

  const doneSteps = detail.steps.filter((s) =>
    ['verified', 'completed', 'done', 'succeeded'].includes(s.status),
  ).length
  const totalSteps = detail.steps.length
  const pct = totalSteps > 0 ? Math.min(100, (doneSteps / totalSteps) * 100) : 0
  const showApproval = detail.status === 'waiting_approval' && pendingApproval
  const showError = (detail.status === 'failed' || detail.status === 'paused') && detail.error

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col px-4 py-6">
      <button onClick={onBack} className="mb-4 self-start text-sm text-zinc-400 hover:text-zinc-200">
        ← All tasks
      </button>

      {/* Header */}
      <div className="mb-4">
        <div className="flex items-start justify-between gap-3">
          <h1 className="min-w-0 flex-1 text-lg font-semibold text-zinc-100">{detail.goal}</h1>
          <StatusPill status={detail.status} />
        </div>
        <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-zinc-500">
          <span>Model: {detail.model || 'default'}</span>
          <span>
            Usage: ${detail.usage.cost_usd.toFixed(4)} · {detail.usage.tokens.toLocaleString()} tokens
          </span>
          <span>Updated {formatTime(detail.updated_at)}</span>
        </div>
        {totalSteps > 0 && (
          <div className="mt-3">
            <div className="mb-1 flex justify-between text-xs text-zinc-500">
              <span>
                {doneSteps}/{totalSteps} steps verified
              </span>
            </div>
            <div className="h-1.5 overflow-hidden rounded-full bg-zinc-800">
              <div className="h-full rounded-full bg-zinc-400 transition-all" style={{ width: `${pct}%` }} />
            </div>
          </div>
        )}
      </div>

      {/* Action + error banners */}
      {actionError && (
        <div className="mb-3 rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-2.5 text-sm text-red-200">
          {actionError}
        </div>
      )}
      {streamError && (
        <div className="mb-3 rounded-xl border border-amber-900/50 bg-amber-950/40 px-4 py-2.5 text-sm text-amber-200">
          Live updates interrupted: {streamError}. The snapshot above is the last known state.
        </div>
      )}
      {showError && (
        <div className="mb-3 rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-2.5 text-sm text-red-200">
          <span className="font-medium">
            {detail.status === 'paused' ? 'Paused: ' : 'Failed: '}
          </span>
          {detail.error}
        </div>
      )}

      {/* Approval card */}
      {showApproval && pendingApproval && (
        <div className="mb-4 rounded-xl border border-amber-700/60 bg-amber-950/30 p-4">
          <div className="mb-1 flex items-center gap-2 text-sm font-semibold text-amber-200">
            <span>⚠</span> Approval required
          </div>
          <p className="text-sm text-zinc-200">{pendingApproval.description}</p>
          <p className="mt-1 text-xs text-zinc-400">
            Tool: <span className="font-mono text-amber-200">{pendingApproval.tool}</span>
          </p>
          {pendingApproval.args !== undefined && pendingApproval.args !== null && (
            <pre className="slim-scroll mt-2 max-h-40 overflow-auto rounded-lg bg-zinc-950 p-3 font-mono text-xs text-zinc-300">
              {JSON.stringify(pendingApproval.args, null, 2)}
            </pre>
          )}
          <div className="mt-3 flex gap-2">
            <button
              onClick={() => void runAction(() => approveTask(id, true), 'Approve')}
              disabled={acting}
              className="rounded-lg bg-emerald-500 px-4 py-2 text-sm font-medium text-zinc-950 transition hover:bg-emerald-400 disabled:opacity-40"
            >
              Approve
            </button>
            <button
              onClick={() => void runAction(() => approveTask(id, false), 'Reject')}
              disabled={acting}
              className="rounded-lg border border-red-700 bg-red-950/60 px-4 py-2 text-sm font-medium text-red-200 transition hover:bg-red-900/60 disabled:opacity-40"
            >
              Reject
            </button>
          </div>
          <p className="mt-2 text-[11px] text-zinc-500">
            Nothing runs until you decide. Rejecting stops the task safely.
          </p>
        </div>
      )}

      {/* Controls */}
      {!TERMINAL.includes(detail.status) && (
        <div className="mb-4 flex gap-2">
          {detail.status === 'running' && (
            <button
              onClick={() => void runAction(() => pauseTask(id), 'Pause')}
              disabled={acting}
              className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 transition hover:bg-zinc-800 disabled:opacity-40"
            >
              ⏸ Pause
            </button>
          )}
          {detail.status === 'paused' && (
            <button
              onClick={() => void runAction(() => resumeTask(id), 'Resume')}
              disabled={acting}
              className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 transition hover:bg-zinc-800 disabled:opacity-40"
            >
              ▶ Resume
            </button>
          )}
          <button
            onClick={() => void runAction(() => cancelTask(id), 'Cancel')}
            disabled={acting}
            className="rounded-lg border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 transition hover:bg-zinc-800 disabled:opacity-40"
          >
            Cancel
          </button>
        </div>
      )}

      <div className="grid min-h-0 flex-1 gap-4 md:grid-cols-2">
        {/* Steps */}
        <div className="flex min-h-0 flex-col">
          <h2 className="mb-2 text-sm font-medium text-zinc-300">Steps</h2>
          <div className="slim-scroll min-h-0 flex-1 overflow-y-auto rounded-xl border border-zinc-800 bg-zinc-900/40 p-3">
            {detail.steps.length === 0 ? (
              <p className="py-6 text-center text-xs text-zinc-500">
                No steps yet — the plan appears here once Nova creates it.
              </p>
            ) : (
              <ol className="space-y-2">
                {detail.steps.map((s, i) => (
                  <li key={s.id} className="rounded-lg bg-zinc-950/60 px-3 py-2">
                    <div className="flex items-start gap-2">
                      <span className="mt-0.5 text-xs text-zinc-600">{i + 1}</span>
                      <div className="min-w-0 flex-1">
                        <p className="text-sm text-zinc-200">{s.description}</p>
                        <p className="mt-0.5 font-mono text-[11px] text-zinc-500">
                          {s.tool} · <span className="text-zinc-400">{s.status}</span>
                        </p>
                        {s.result && (
                          <p className="mt-1 line-clamp-3 text-xs text-zinc-500">{s.result}</p>
                        )}
                      </div>
                    </div>
                  </li>
                ))}
              </ol>
            )}
          </div>
        </div>

        {/* Live event feed */}
        <div className="flex min-h-0 flex-col">
          <h2 className="mb-2 text-sm font-medium text-zinc-300">
            Activity
            <span className="ml-2 inline-block h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400 align-middle" />
          </h2>
          <div
            ref={feedRef}
            className="slim-scroll min-h-0 flex-1 overflow-y-auto rounded-xl border border-zinc-800 bg-zinc-900/40 p-3"
          >
            {feed.length === 0 ? (
              <p className="py-6 text-center text-xs text-zinc-500">
                Waiting for activity… events stream here live.
              </p>
            ) : (
              <ol className="space-y-2">
                {feed.map(({ key, evt, at }) => {
                  const meta = eventMeta(String(evt.type))
                  const summary = eventSummary(evt)
                  return (
                    <li key={key} className="flex items-start gap-2 text-xs">
                      <span className={`mt-0.5 w-5 shrink-0 text-center ${meta.tone}`}>
                        {meta.icon}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className={`font-medium ${meta.tone}`}>{meta.label}</p>
                        {summary && <p className="mt-0.5 break-words text-zinc-500">{summary}</p>}
                        <p className="mt-0.5 text-[10px] text-zinc-600">
                          {at.toLocaleTimeString()}
                        </p>
                      </div>
                    </li>
                  )
                })}
              </ol>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
