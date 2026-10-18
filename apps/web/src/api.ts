/**
 * Actlet API client. Implements EXACTLY the Milestone 2 contract —
 * no invented endpoints.
 *
 * Same-origin in production; in dev Vite proxies /api and /health
 * to http://localhost:8000 (see vite.config.ts).
 */

export interface ChatMessage {
  role: 'user' | 'assistant' | 'system'
  content: string
  created_at?: string
}

export interface ModelInfo {
  id: string
  label: string
  provider: string
  free: boolean
}

export interface Conversation {
  id: string
  title: string
  created_at: string
}

export interface Health {
  ok: boolean
  service: 'actlet-api'
  milestone: number
  model_default: string
}

const TOKEN_KEY = 'actlet_token'

export function getToken(): string {
  return localStorage.getItem(TOKEN_KEY) ?? ''
}

export function setToken(token: string): void {
  if (token) localStorage.setItem(TOKEN_KEY, token)
  else localStorage.removeItem(TOKEN_KEY)
}

function authHeaders(extra: Record<string, string> = {}): Record<string, string> {
  const token = getToken()
  return token ? { ...extra, Authorization: `Bearer ${token}` } : extra
}

async function request<T>(path: string, init: RequestInit = {}): Promise<T> {
  let res: Response
  try {
    res = await fetch(path, { ...init, headers: authHeaders(init.headers as Record<string, string>) })
  } catch {
    throw new Error('Cannot reach the Actlet backend (is it running?)')
  }
  if (!res.ok) {
    // Surface the backend's own message when it explains itself (e.g. 400 on a bare secret).
    let detail = ''
    try {
      const body = (await res.json()) as Record<string, unknown>
      const m = body.message ?? body.detail ?? body.error
      if (typeof m === 'string' && m) detail = `: ${m}`
    } catch {
      /* not JSON — keep the generic message */
    }
    throw new Error(`Backend error ${res.status} on ${path}${detail}`)
  }
  return (await res.json()) as T
}

export const getHealth = () => request<Health>('/health')

export const getModels = () => request<{ default: string; models: ModelInfo[] }>('/api/models')

export const getConversations = () =>
  request<{ conversations: Conversation[] }>('/api/conversations')

export const getConversationMessages = (id: string) =>
  request<{ messages: ChatMessage[] }>(`/api/conversations/${encodeURIComponent(id)}/messages`)

export interface StreamCallbacks {
  onDelta: (text: string) => void
}

/**
 * POST /api/chat as SSE over fetch + ReadableStream (EventSource can't POST).
 * Resolves with the conversation_id from the final {type:"done"} event.
 * Throws on {type:"error"} or transport failure.
 */
export async function streamChat(
  body: { messages: ChatMessage[]; model?: string; conversation_id?: string | null },
  cb: StreamCallbacks,
): Promise<string> {
  let res: Response
  try {
    res = await fetch('/api/chat', {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify(body),
    })
  } catch {
    throw new Error('No model reachable — is Ollama running?')
  }
  if (!res.ok || !res.body) {
    throw new Error(`Chat request failed (${res.status})`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let conversationId = ''

  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let sep: number
    while ((sep = buffer.indexOf('\n\n')) >= 0) {
      const chunk = buffer.slice(0, sep)
      buffer = buffer.slice(sep + 2)
      for (const line of chunk.split('\n')) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue
        let evt: { type: string; text?: string; message?: string; conversation_id?: string }
        try {
          evt = JSON.parse(trimmed.slice(5).trim())
        } catch {
          continue // ignore malformed keep-alive lines
        }
        if (evt.type === 'delta') {
          cb.onDelta(evt.text ?? '')
        } else if (evt.type === 'done') {
          conversationId = evt.conversation_id ?? ''
        } else if (evt.type === 'error') {
          throw new Error(evt.message || 'The model returned an error')
        }
      }
    }
  }
  return conversationId
}

/* ------------------------------------------------------------------ */
/* Tasks (Milestone 3 contract)                                        */
/* ------------------------------------------------------------------ */

export type TaskStatus =
  | 'pending'
  | 'running'
  | 'waiting_approval'
  | 'paused'
  | 'failed'
  | 'completed'
  | 'cancelled'

export interface TaskSummary {
  id: string
  goal: string
  status: TaskStatus
  current_step: number
  total_steps: number
  created_at: string
  updated_at: string
}

export interface TaskStep {
  id: string
  description: string
  tool: string
  args: unknown
  status: string
  result: string | null
}

export interface TaskUsage {
  cost_usd: number
  tokens: number
}

export interface TaskDetail {
  id: string
  goal: string
  status: TaskStatus
  model: string
  steps: TaskStep[]
  usage: TaskUsage
  error: string | null
  pending_approval: { id: string; description: string; tool: string; args: unknown } | null
  created_at: string
  updated_at: string
}

export type TaskEventType =
  | 'task_started'
  | 'plan_created'
  | 'step_started'
  | 'tool_called'
  | 'tool_result'
  | 'approval_required'
  | 'approval_decided'
  | 'step_verified'
  | 'budget_exceeded'
  | 'task_paused'
  | 'task_completed'
  | 'task_failed'
  | 'task_cancelled'

export interface TaskEvent {
  type: TaskEventType | string
  step?: TaskStep
  steps?: TaskStep[]
  usage?: TaskUsage
  error?: string | null
  approved?: boolean
  message?: string
  [key: string]: unknown
}

export const createTask = (goal: string, model?: string) =>
  request<{ id: string; status: TaskStatus }>('/api/tasks', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(model ? { goal, model } : { goal }),
  })

export const getTasks = () => request<{ tasks: TaskSummary[] }>('/api/tasks')

export const getTask = (id: string) =>
  request<TaskDetail>(`/api/tasks/${encodeURIComponent(id)}`)

export const approveTask = (id: string, approved: boolean) =>
  request<{ status: TaskStatus }>(`/api/tasks/${encodeURIComponent(id)}/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ approved }),
  })

export const cancelTask = (id: string) =>
  request<{ status: TaskStatus }>(`/api/tasks/${encodeURIComponent(id)}/cancel`, {
    method: 'POST',
  })

export const pauseTask = (id: string) =>
  request<{ status: TaskStatus }>(`/api/tasks/${encodeURIComponent(id)}/pause`, {
    method: 'POST',
  })

export const resumeTask = (id: string) =>
  request<{ status: TaskStatus }>(`/api/tasks/${encodeURIComponent(id)}/resume`, {
    method: 'POST',
  })

/**
 * GET /api/tasks/{id}/events as SSE over fetch + ReadableStream.
 * The backend first replays history, then streams live events.
 * Resolves when the stream closes (terminal states close it server-side).
 * Throws on transport failure; task_failed / budget_exceeded arrive as events.
 */
export async function streamTaskEvents(
  id: string,
  onEvent: (evt: TaskEvent) => void,
  signal?: AbortSignal,
): Promise<void> {
  let res: Response
  try {
    res = await fetch(`/api/tasks/${encodeURIComponent(id)}/events`, {
      headers: authHeaders({ Accept: 'text/event-stream' }),
      signal,
    })
  } catch (e) {
    if (e instanceof DOMException && e.name === 'AbortError') return
    throw new Error('Lost connection to the task stream — is the backend running?')
  }
  if (!res.ok || !res.body) {
    throw new Error(`Task stream failed (${res.status})`)
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''

  for (;;) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    let sep: number
    while ((sep = buffer.indexOf('\n\n')) >= 0) {
      const chunk = buffer.slice(0, sep)
      buffer = buffer.slice(sep + 2)
      for (const line of chunk.split('\n')) {
        const trimmed = line.trim()
        if (!trimmed.startsWith('data:')) continue
        try {
          onEvent(JSON.parse(trimmed.slice(5).trim()) as TaskEvent)
        } catch {
          continue // ignore malformed keep-alive lines
        }
      }
    }
  }
}

/* ------------------------------------------------------------------ */
/* Memory (Milestone 4 contract)                                       */
/* ------------------------------------------------------------------ */

export interface Memory {
  id: string
  content: string
  tags: string[]
  source: string
  created_at: string
  updated_at: string
}

export interface MemoryList {
  memories: Memory[]
  total: number
  query?: string
}

export const getMemories = (q?: string, limit?: number, offset?: number) => {
  const params = new URLSearchParams()
  if (q) params.set('q', q)
  if (limit !== undefined) params.set('limit', String(limit))
  if (offset !== undefined) params.set('offset', String(offset))
  const qs = params.toString()
  return request<MemoryList>(`/api/memories${qs ? `?${qs}` : ''}`)
}

export const addMemory = (content: string, tags: string[]) =>
  request<{ memory: Memory; merged: boolean }>('/api/memories', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, tags }),
  })

export const getMemory = (id: string) =>
  request<Memory>(`/api/memories/${encodeURIComponent(id)}`)

export const updateMemory = (id: string, content?: string, tags?: string[]) =>
  request<Memory>(`/api/memories/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content, tags }),
  })

export const deleteMemory = (id: string) =>
  request<{ deleted: boolean }>(`/api/memories/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })

export interface MemoryExport {
  memories: { content: string; tags: string[]; source: string }[]
}

export const exportMemories = () => request<MemoryExport>('/api/memories/export')

export interface MemoryImportEntry {
  content: string
  tags?: string[]
}

export const importMemories = (memories: MemoryImportEntry[]) =>
  request<{ added: number; merged: number; skipped: number }>('/api/memories/import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ memories }),
  })

export const extractMemories = (conversationId: string) =>
  request<{ added: Memory[]; count: number }>(
    `/api/conversations/${encodeURIComponent(conversationId)}/extract-memories`,
    { method: 'POST' },
  )

// Browser screenshots. The endpoint requires the same Bearer auth as the rest
// of the API, but <img> tags can't set headers, so this returns a plain URL
// against the same origin (Vite dev proxy / nginx both serve /api). When no
// token is set the API is open and images load directly; when a token IS set
// the image request 401s — callers must handle onError gracefully.
export const shotUrl = (name: string): string => `/api/shots/${encodeURIComponent(name)}`

// Extract the screenshot artifact name from a task event payload, if present.
export const shotNameOf = (evt: TaskEvent): string | null => {
  const artifacts = evt.artifacts
  if (artifacts && typeof artifacts === 'object' && !Array.isArray(artifacts)) {
    const shot = (artifacts as Record<string, unknown>).shot
    if (typeof shot === 'string' && shot.length > 0) return shot
  }
  return null
}

/* ------------------------------------------------------------------ */
/* Schedules (Milestone 6 contract)                                    */
/* ------------------------------------------------------------------ */

export interface Schedule {
  id: string
  name: string
  goal: string
  cron: string | null
  interval_sec: number | null
  when: string
  preapproved_tools: string[]
  enabled: boolean
  last_run_at: string | null
  last_task_id: string | null
  next_run_at: string | null
  run_count: number
  created_at: string
}

export type ScheduleTrigger =
  | { mode: 'when'; when: string }
  | { mode: 'cron'; cron: string }
  | { mode: 'interval'; interval_sec: number }

export interface ScheduleCreate {
  name: string
  goal: string
  preapproved_tools?: string[]
}

export const getSchedules = () => request<{ schedules: Schedule[] }>('/api/schedules')

export const createSchedule = (body: ScheduleCreate & ScheduleTrigger) =>
  request<Schedule>('/api/schedules', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

export const updateSchedule = (
  id: string,
  body: Partial<ScheduleCreate> & { enabled?: boolean } & Partial<ScheduleTrigger>,
) =>
  request<Schedule>(`/api/schedules/${encodeURIComponent(id)}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

export const deleteSchedule = (id: string) =>
  request<{ deleted: boolean }>(`/api/schedules/${encodeURIComponent(id)}`, {
    method: 'DELETE',
  })

export const runScheduleNow = (id: string) =>
  request<{ fired: boolean; task_id: string }>(
    `/api/schedules/${encodeURIComponent(id)}/run-now`,
    { method: 'POST' },
  )

/* ------------------------------------------------------------------ */
/* Skills + dreaming (Milestone 6 contract)                             */
/* ------------------------------------------------------------------ */

export interface Skill {
  name: string
  description: string
  instructions: string
  tools: string[]
  created_from: string[]
  use_count: number
}

export interface SkillCreate {
  name: string
  description: string
  instructions: string
  tools?: string[]
}

export interface DreamFact {
  id: string
  content: string
}

export interface DreamResult {
  tasks_considered: number
  facts_stored: number
  facts: DreamFact[]
}

export interface MakeSkillResult {
  skipped: boolean
  name?: string
}

export const getSkills = () => request<{ skills: Skill[] }>('/api/skills')

export const createSkill = (body: SkillCreate) =>
  request<Skill>('/api/skills', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })

export const deleteSkill = (name: string) =>
  request<{ deleted: boolean }>(`/api/skills/${encodeURIComponent(name)}`, {
    method: 'DELETE',
  })

export const runDreaming = () =>
  request<DreamResult>('/api/dreaming/run', { method: 'POST' })

export const makeSkill = (taskId: string) =>
  request<MakeSkillResult>(`/api/tasks/${encodeURIComponent(taskId)}/make-skill`, {
    method: 'POST',
  })

export interface SkillExport {
  name: string
  filename: string
  content: string
}

export const exportSkill = (name: string) =>
  request<SkillExport>(`/api/skills/${encodeURIComponent(name)}/export`)

export const importSkill = (content: string) =>
  request<Skill>('/api/skills/import', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ content }),
  })

/* ------------------------------------------------------------------ */
/* Channels (Milestone 7 contract)                                     */
/* ------------------------------------------------------------------ */

export interface ChannelStatus {
  connected: boolean
}

export const getChannels = () =>
  request<{ channels: Record<string, ChannelStatus> }>('/api/channels')

/* ------------------------- Agent control ------------------------- */

export interface AgentStatus {
  paused: boolean
  quiet_hours: boolean
}

export const getAgentStatus = () => request<AgentStatus>('/api/agent/status')

export const pauseAgent = () =>
  request<{ paused: boolean }>('/api/agent/pause', { method: 'POST' })

export const resumeAgent = () =>
  request<{ paused: boolean }>('/api/agent/resume', { method: 'POST' })
