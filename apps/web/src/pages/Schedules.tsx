import React, { useCallback, useEffect, useState } from 'react'
import {
  Schedule,
  ScheduleTrigger,
  createSchedule,
  deleteSchedule,
  getSchedules,
  runScheduleNow,
  updateSchedule,
} from '../api'
import { formatTime } from './Tasks'

type TriggerMode = 'when' | 'cron' | 'interval'

interface FormState {
  name: string
  goal: string
  mode: TriggerMode
  when: string
  cron: string
  interval: string
  tools: string
}

function emptyForm(): FormState {
  return { name: '', goal: '', mode: 'when', when: '', cron: '', interval: '', tools: '' }
}

function formFromSchedule(s: Schedule): FormState {
  if (s.cron) return { name: s.name, goal: s.goal, mode: 'cron', when: '', cron: s.cron, interval: '', tools: s.preapproved_tools.join(', ') }
  if (s.interval_sec !== null) return { name: s.name, goal: s.goal, mode: 'interval', when: '', cron: '', interval: String(s.interval_sec), tools: s.preapproved_tools.join(', ') }
  return { name: s.name, goal: s.goal, mode: 'when', when: s.when, cron: '', interval: '', tools: s.preapproved_tools.join(', ') }
}

function buildTrigger(f: FormState): ScheduleTrigger {
  if (f.mode === 'cron') return { mode: 'cron', cron: f.cron.trim() }
  if (f.mode === 'interval') return { mode: 'interval', interval_sec: Number(f.interval) }
  return { mode: 'when', when: f.when.trim() }
}

function parseTools(s: string): string[] {
  return s.split(',').map((t) => t.trim()).filter(Boolean)
}

const inputCls =
  'w-full rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none disabled:opacity-50'
const btnPrimary =
  'rounded-xl bg-zinc-100 px-4 py-2.5 text-sm font-medium text-zinc-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40'
const btnGhost =
  'rounded-xl border border-zinc-700 px-3 py-1.5 text-sm text-zinc-300 transition hover:border-zinc-500 hover:text-zinc-100 disabled:cursor-not-allowed disabled:opacity-40'

function ScheduleForm({
  initial,
  submitLabel,
  onSubmit,
  onCancel,
  busy,
  error,
}: {
  initial: FormState
  submitLabel: string
  onSubmit: (f: FormState) => void
  onCancel: () => void
  busy: boolean
  error: string | null
}): React.ReactElement {
  const [f, setF] = useState<FormState>(initial)
  const set = (patch: Partial<FormState>) => setF((prev) => ({ ...prev, ...patch }))

  const modes: { id: TriggerMode; label: string }[] = [
    { id: 'when', label: 'Natural language' },
    { id: 'cron', label: 'Cron' },
    { id: 'interval', label: 'Interval' },
  ]

  const triggerOk =
    f.mode === 'when' ? f.when.trim().length > 0
    : f.mode === 'cron' ? f.cron.trim().length > 0
    : f.interval.trim().length > 0 && Number.isFinite(Number(f.interval)) && Number(f.interval) > 0

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 p-4">
      <div className="grid gap-3">
        <input
          value={f.name}
          onChange={(e) => set({ name: e.target.value })}
          placeholder="Schedule name — e.g. Morning briefing"
          disabled={busy}
          className={inputCls}
        />
        <textarea
          value={f.goal}
          onChange={(e) => set({ goal: e.target.value })}
          placeholder="What should Nova do each run? — e.g. Summarize overnight tech news and save the top 5 to memory"
          disabled={busy}
          rows={3}
          className={`${inputCls} resize-y`}
        />
        <div>
          <div className="mb-2 flex gap-1">
            {modes.map((m) => (
              <button
                key={m.id}
                type="button"
                onClick={() => set({ mode: m.id })}
                disabled={busy}
                className={`rounded-lg px-3 py-1.5 text-xs transition ${
                  f.mode === m.id ? 'bg-zinc-700 text-zinc-100' : 'text-zinc-500 hover:text-zinc-300'
                }`}
              >
                {m.label}
              </button>
            ))}
          </div>
          {f.mode === 'when' && (
            <input
              value={f.when}
              onChange={(e) => set({ when: e.target.value })}
              placeholder="every morning at 8, every 5m, daily at 18:30…"
              disabled={busy}
              className={inputCls}
            />
          )}
          {f.mode === 'cron' && (
            <input
              value={f.cron}
              onChange={(e) => set({ cron: e.target.value })}
              placeholder="0 8 * * *  (min hour day month weekday)"
              disabled={busy}
              className={`${inputCls} font-mono`}
            />
          )}
          {f.mode === 'interval' && (
            <div className="flex items-center gap-2">
              <input
                value={f.interval}
                onChange={(e) => set({ interval: e.target.value.replace(/[^0-9]/g, '') })}
                placeholder="3600"
                disabled={busy}
                inputMode="numeric"
                className={`${inputCls} font-mono`}
              />
              <span className="shrink-0 text-sm text-zinc-500">seconds</span>
            </div>
          )}
        </div>
        <div>
          <input
            value={f.tools}
            onChange={(e) => set({ tools: e.target.value })}
            placeholder="web_fetch, read_file  (optional)"
            disabled={busy}
            className={`${inputCls} font-mono`}
          />
          <p className="mt-1.5 text-xs text-zinc-500">
            Tools this schedule may use without asking. Leave empty for fully supervised
            (recommended) — approvals still apply on every run.
          </p>
        </div>
      </div>
      {error && <p className="mt-3 text-sm text-red-400">{error}</p>}
      <div className="mt-3 flex gap-2">
        <button
          onClick={() => onSubmit(f)}
          disabled={busy || !f.name.trim() || !f.goal.trim() || !triggerOk}
          className={btnPrimary}
        >
          {busy ? '…' : submitLabel}
        </button>
        <button onClick={onCancel} disabled={busy} className={btnGhost}>
          Cancel
        </button>
      </div>
    </div>
  )
}

function ScheduleCard({
  schedule,
  onChanged,
  onDeleted,
  onOpenTask,
}: {
  schedule: Schedule
  onChanged: (s: Schedule) => void
  onDeleted: (id: string) => void
  onOpenTask: (id: string) => void
}): React.ReactElement {
  const [editing, setEditing] = useState(false)
  const [confirmDelete, setConfirmDelete] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [runMsg, setRunMsg] = useState<string | null>(null)

  const toggleEnabled = async () => {
    setBusy(true)
    setError(null)
    try {
      onChanged(await updateSchedule(schedule.id, { enabled: !schedule.enabled }))
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not update schedule')
    } finally {
      setBusy(false)
    }
  }

  const save = async (f: FormState) => {
    setBusy(true)
    setError(null)
    try {
      onChanged(
        await updateSchedule(schedule.id, {
          name: f.name.trim(),
          goal: f.goal.trim(),
          preapproved_tools: parseTools(f.tools),
          ...buildTrigger(f),
        }),
      )
      setEditing(false)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not save schedule')
    } finally {
      setBusy(false)
    }
  }

  const remove = async () => {
    setBusy(true)
    try {
      await deleteSchedule(schedule.id)
      onDeleted(schedule.id)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not delete schedule')
      setBusy(false)
      setConfirmDelete(false)
    }
  }

  const fire = async () => {
    setBusy(true)
    setRunMsg(null)
    setError(null)
    try {
      const { task_id } = await runScheduleNow(schedule.id)
      setRunMsg(`Run started — task ${task_id.slice(0, 8)}…`)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not start run')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="rounded-xl border border-zinc-800 bg-zinc-900/60 px-4 py-3">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <div className="flex items-center gap-2">
            <h3 className="truncate text-sm font-medium text-zinc-100">{schedule.name}</h3>
            <button
              onClick={() => void toggleEnabled()}
              disabled={busy}
              title={schedule.enabled ? 'Disable schedule' : 'Enable schedule'}
              className={`relative h-5 w-9 shrink-0 rounded-full transition ${
                schedule.enabled ? 'bg-emerald-600' : 'bg-zinc-700'
              } disabled:opacity-50`}
            >
              <span
                className="absolute top-0.5 h-4 w-4 rounded-full bg-white transition-all"
                style={{ left: schedule.enabled ? '1.125rem' : '0.125rem' }}
              />
            </button>
            {!schedule.enabled && <span className="text-xs text-zinc-500">paused</span>}
          </div>
          <p className="mt-1 text-sm text-zinc-400">{schedule.goal}</p>
          <div className="mt-2 flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-zinc-500">
            <span title="Cadence">🕐 {schedule.when}</span>
            <span title="Runs so far">runs: {schedule.run_count}</span>
            {schedule.last_run_at && <span title="Last run">last: {formatTime(schedule.last_run_at)}</span>}
            {schedule.next_run_at && schedule.enabled && (
              <span title="Next run">next: {formatTime(schedule.next_run_at)}</span>
            )}
          </div>
          <div className="mt-2 flex flex-wrap items-center gap-1.5">
            {schedule.preapproved_tools.length === 0 ? (
              <span className="text-xs italic text-zinc-600">fully supervised — approvals apply on every run</span>
            ) : (
              schedule.preapproved_tools.map((t) => (
                <span key={t} className="rounded-full bg-zinc-800 px-2 py-0.5 font-mono text-xs text-zinc-300">
                  {t}
                </span>
              ))
            )}
          </div>
          {schedule.last_task_id && (
            <button
              onClick={() => onOpenTask(schedule.last_task_id!)}
              className="mt-2 text-xs text-zinc-400 underline underline-offset-2 hover:text-zinc-200"
            >
              View last run →
            </button>
          )}
        </div>
        <div className="flex shrink-0 flex-col gap-1.5">
          <button onClick={() => void fire()} disabled={busy} className={btnGhost}>
            ▶ Run now
          </button>
          <button onClick={() => setEditing((v) => !v)} disabled={busy} className={btnGhost}>
            Edit
          </button>
          {confirmDelete ? (
            <button onClick={() => void remove()} disabled={busy} className="rounded-xl border border-red-800 bg-red-950 px-3 py-1.5 text-sm text-red-200 transition hover:bg-red-900 disabled:opacity-40">
              Yes, delete
            </button>
          ) : (
            <button onClick={() => setConfirmDelete(true)} disabled={busy} className={btnGhost}>
              Delete
            </button>
          )}
        </div>
      </div>
      {runMsg && <p className="mt-2 text-sm text-emerald-400">{runMsg}</p>}
      {error && <p className="mt-2 text-sm text-red-400">{error}</p>}
      {editing && (
        <div className="mt-3">
          <ScheduleForm
            initial={formFromSchedule(schedule)}
            submitLabel="Save"
            onSubmit={(f) => void save(f)}
            onCancel={() => setEditing(false)}
            busy={busy}
            error={error}
          />
        </div>
      )}
    </div>
  )
}

interface SchedulesProps {
  onOpenTask: (id: string) => void
}

export default function Schedules({ onOpenTask }: SchedulesProps): React.ReactElement {
  const [schedules, setSchedules] = useState<Schedule[]>([])
  const [loading, setLoading] = useState(true)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [creating, setCreating] = useState(false)
  const [busy, setBusy] = useState(false)
  const [createError, setCreateError] = useState<string | null>(null)

  const refresh = useCallback(() => {
    setLoading(true)
    getSchedules()
      .then((d) => {
        setSchedules(d.schedules)
        setLoadError(null)
      })
      .catch((e: Error) => setLoadError(e.message))
      .finally(() => setLoading(false))
  }, [])

  useEffect(() => {
    refresh()
  }, [refresh])

  const create = async (f: FormState) => {
    setBusy(true)
    setCreateError(null)
    try {
      const s = await createSchedule({
        name: f.name.trim(),
        goal: f.goal.trim(),
        preapproved_tools: parseTools(f.tools),
        ...buildTrigger(f),
      })
      setSchedules((prev) => [s, ...prev])
      setCreating(false)
    } catch (e) {
      setCreateError(e instanceof Error ? e.message : 'Could not create schedule')
    } finally {
      setBusy(false)
    }
  }

  const onChanged = (s: Schedule) =>
    setSchedules((prev) => prev.map((x) => (x.id === s.id ? s : x)))
  const onDeleted = (id: string) => setSchedules((prev) => prev.filter((x) => x.id !== id))

  return (
    <div className="mx-auto flex h-full max-w-4xl flex-col px-4 py-6">
      <div className="mb-6 flex items-start justify-between gap-3">
        <div>
          <h1 className="text-xl font-semibold text-zinc-100">Schedules</h1>
          <p className="mt-1 text-sm text-zinc-500">
            Recurring agent tasks. Nova wakes up on a cadence, plans, and runs — asking for
            approval unless you've pre-approved its tools.
          </p>
        </div>
        {!creating && (
          <button onClick={() => setCreating(true)} className={btnPrimary}>
            + New schedule
          </button>
        )}
      </div>

      {creating && (
        <div className="mb-6">
          <ScheduleForm
            initial={emptyForm()}
            submitLabel="Create schedule"
            onSubmit={(f) => void create(f)}
            onCancel={() => {
              setCreating(false)
              setCreateError(null)
            }}
            busy={busy}
            error={createError}
          />
        </div>
      )}

      <div className="slim-scroll min-h-0 flex-1 overflow-y-auto">
        {loading ? (
          <p className="py-10 text-center text-sm text-zinc-500">Loading schedules…</p>
        ) : loadError ? (
          <div className="rounded-xl border border-red-900/50 bg-red-950/40 px-4 py-3 text-sm text-red-200">
            <span className="font-medium">Couldn't load schedules: </span>
            {loadError}
            <button onClick={refresh} className="ml-3 underline underline-offset-2 hover:text-red-100">
              Retry
            </button>
          </div>
        ) : schedules.length === 0 && !creating ? (
          <div className="py-16 text-center">
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-800 text-2xl">
              🕐
            </div>
            <h2 className="text-lg font-medium text-zinc-200">No schedules yet</h2>
            <p className="mx-auto mt-2 max-w-md text-sm text-zinc-500">
              Schedules run agent tasks on a cadence — approvals still apply unless you
              pre-approve tools.
            </p>
          </div>
        ) : (
          <ul className="space-y-2">
            {schedules.map((s) => (
              <li key={s.id}>
                <ScheduleCard
                  schedule={s}
                  onChanged={onChanged}
                  onDeleted={onDeleted}
                  onOpenTask={onOpenTask}
                />
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
