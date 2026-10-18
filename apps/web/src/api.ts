/**
 * NovaPilot API client. Implements EXACTLY the Milestone 2 contract —
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
  service: 'novapilot-api'
  milestone: number
  model_default: string
}

const TOKEN_KEY = 'novapilot_token'

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
    throw new Error('Cannot reach the NovaPilot backend (is it running?)')
  }
  if (!res.ok) {
    throw new Error(`Backend error ${res.status} on ${path}`)
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
