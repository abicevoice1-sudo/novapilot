import React, { useCallback, useEffect, useRef, useState } from 'react'
import {
  ChatMessage,
  Conversation,
  ModelInfo,
  extractMemories,
  getConversationMessages,
  getConversations,
  getModels,
  streamChat,
} from '../api'
import { Markdown } from '../Markdown'

export default function Chat(): React.ReactElement {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [convosError, setConvosError] = useState<string | null>(null)
  const [currentId, setCurrentId] = useState<string | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [loadingHistory, setLoadingHistory] = useState(false)
  const [models, setModels] = useState<ModelInfo[]>([])
  const [modelsError, setModelsError] = useState<string | null>(null)
  const [selectedModel, setSelectedModel] = useState<string>('')
  const [input, setInput] = useState('')
  const [streaming, setStreaming] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [remembering, setRemembering] = useState(false)
  const [rememberNote, setRememberNote] = useState<string | null>(null)

  const scrollRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)
  const rememberTimer = useRef<number | null>(null)

  // Load models + conversation list on mount.
  useEffect(() => {
    getModels()
      .then((d) => {
        setModels(d.models)
        setSelectedModel(d.default)
      })
      .catch((e: Error) => setModelsError(e.message))
    refreshConversations()
  }, [])

  const refreshConversations = useCallback(() => {
    getConversations()
      .then((d) => {
        setConversations(d.conversations)
        setConvosError(null)
      })
      .catch((e: Error) => setConvosError(e.message))
  }, [])

  // Auto-scroll on new content.
  useEffect(() => {
    const el = scrollRef.current
    if (el) el.scrollTop = el.scrollHeight
  }, [messages, streaming])

  const selectConversation = useCallback(async (id: string) => {
    if (id === currentId || streaming) return
    setCurrentId(id)
    setError(null)
    setLoadingHistory(true)
    try {
      const d = await getConversationMessages(id)
      setMessages(d.messages)
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Could not load messages')
      setMessages([])
    } finally {
      setLoadingHistory(false)
    }
  }, [currentId])

  const newChat = useCallback(() => {
    if (streaming) return
    setCurrentId(null)
    setMessages([])
    setError(null)
    inputRef.current?.focus()
  }, [streaming])

  const send = useCallback(async () => {
    const text = input.trim()
    if (!text || streaming) return
    setError(null)
    setInput('')

    const history: ChatMessage[] = [...messages, { role: 'user', content: text }]
    setMessages([...history, { role: 'assistant', content: '' }])
    setStreaming(true)

    try {
      const conversationId = await streamChat(
        {
          messages: history.map(({ role, content }) => ({ role, content })),
          model: selectedModel || undefined,
          conversation_id: currentId,
        },
        {
          onDelta: (delta) =>
            setMessages((prev) => {
              const next = [...prev]
              const last = next[next.length - 1]
              next[next.length - 1] = { ...last, content: last.content + delta }
              return next
            }),
        },
      )
      if (conversationId && conversationId !== currentId) {
        setCurrentId(conversationId)
      }
      refreshConversations()
    } catch (e) {
      // Drop the empty assistant bubble; the banner carries the honest error.
      setMessages((prev) => {
        const last = prev[prev.length - 1]
        return last && last.role === 'assistant' && last.content === '' ? prev.slice(0, -1) : prev
      })
      setError(e instanceof Error ? e.message : 'Something went wrong')
    } finally {
      setStreaming(false)
      inputRef.current?.focus()
    }
  }, [input, streaming, messages, selectedModel, currentId, refreshConversations])

  const onKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      void send()
    }
  }

  // Auto-grow the textarea.
  useEffect(() => {
    const el = inputRef.current
    if (el) {
      el.style.height = 'auto'
      el.style.height = `${Math.min(el.scrollHeight, 160)}px`
    }
  }, [input])

  const canSend = !streaming && input.trim().length > 0 && models.length > 0

  const remember = useCallback(async () => {
    if (!currentId || streaming || remembering) return
    setRemembering(true)
    setRememberNote(null)
    try {
      const r = await extractMemories(currentId)
      setRememberNote(`Remembered ${r.count} ${r.count === 1 ? 'thing' : 'things'}`)
    } catch (e) {
      setRememberNote(e instanceof Error ? e.message : 'Could not extract memories')
    } finally {
      setRemembering(false)
      if (rememberTimer.current) window.clearTimeout(rememberTimer.current)
      rememberTimer.current = window.setTimeout(() => setRememberNote(null), 6000)
    }
  }, [currentId, streaming, remembering])

  // Clear the pending timer on unmount.
  useEffect(
    () => () => {
      if (rememberTimer.current) window.clearTimeout(rememberTimer.current)
    },
    [],
  )

  return (
    <div className="flex h-full">
      {/* Sidebar */}
      <aside className="flex w-64 shrink-0 flex-col border-r border-zinc-800 bg-zinc-950 max-md:hidden">
        <div className="p-3">
          <button
            onClick={newChat}
            className="w-full rounded-lg bg-zinc-100 px-3 py-2 text-sm font-medium text-zinc-900 transition hover:bg-white"
          >
            + New chat
          </button>
        </div>
        <div className="slim-scroll flex-1 overflow-y-auto px-2 pb-3">
          {convosError ? (
            <p className="px-2 py-3 text-xs text-zinc-500">
              Couldn't load conversations: {convosError}
            </p>
          ) : conversations.length === 0 ? (
            <p className="px-2 py-3 text-xs text-zinc-500">No conversations yet.</p>
          ) : (
            conversations.map((c) => (
              <button
                key={c.id}
                onClick={() => void selectConversation(c.id)}
                className={`mb-1 block w-full truncate rounded-lg px-3 py-2 text-left text-sm transition ${
                  c.id === currentId
                    ? 'bg-zinc-800 text-zinc-100'
                    : 'text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200'
                }`}
                title={c.title}
              >
                {c.title || 'Untitled'}
              </button>
            ))
          )}
        </div>
        <div className="border-t border-zinc-800 p-3 text-[11px] leading-relaxed text-zinc-600">
          Actlet answers from your backend — nothing here is simulated.
        </div>
      </aside>

      {/* Main panel */}
      <div className="flex min-w-0 flex-1 flex-col">
        {/* Model bar */}
        <div className="flex items-center gap-2 border-b border-zinc-800 bg-zinc-950 px-4 py-2">
          <label htmlFor="model" className="text-xs text-zinc-500">
            Model
          </label>
          {modelsError ? (
            <span className="text-xs text-red-400">Couldn't load models: {modelsError}</span>
          ) : models.length === 0 ? (
            <span className="text-xs text-zinc-500">Loading models…</span>
          ) : (
            <select
              id="model"
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              disabled={streaming}
              className="max-w-full rounded-md border border-zinc-700 bg-zinc-900 px-2 py-1 text-sm text-zinc-200 focus:border-zinc-500 focus:outline-none"
            >
              {models.map((m) => (
                <option key={m.id} value={m.id}>
                  {m.label} · {m.provider}
                  {m.free ? ' · free' : ''}
                </option>
              ))}
            </select>
          )}
          <button
            onClick={() => void remember()}
            disabled={!currentId || streaming || remembering}
            title={
              currentId
                ? 'Ask Actlet to extract lasting memories from this conversation'
                : 'Open a conversation first'
            }
            className="rounded-lg px-3 py-1.5 text-sm text-zinc-400 transition hover:bg-zinc-900 hover:text-zinc-200 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {remembering ? '…' : '🧠 Remember this'}
          </button>
          {rememberNote && (
            <span className="max-w-xs truncate text-xs text-zinc-500" title={rememberNote}>
              {rememberNote}
            </span>
          )}
          <button
            onClick={newChat}
            className="ml-auto rounded-lg px-3 py-1.5 text-sm text-zinc-400 hover:bg-zinc-900 hover:text-zinc-200 md:hidden"
          >
            + New
          </button>
        </div>

        {/* Error banner */}
        {error && (
          <div className="border-b border-red-900/50 bg-red-950/40 px-4 py-2.5 text-sm text-red-200">
            <span className="font-medium">Something went wrong: </span>
            {error}
          </div>
        )}

        {/* Messages */}
        <div ref={scrollRef} className="slim-scroll flex-1 overflow-y-auto px-4 py-6">
          <div className="mx-auto max-w-3xl">
            {loadingHistory ? (
              <p className="py-10 text-center text-sm text-zinc-500">Loading messages…</p>
            ) : messages.length === 0 ? (
              <div className="py-16 text-center">
                <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-zinc-800 text-2xl">
                  ✦
                </div>
                <h2 className="text-lg font-medium text-zinc-200">Start a conversation</h2>
                <p className="mx-auto mt-2 max-w-sm text-sm text-zinc-500">
                  Ask Actlet anything. It remembers across sessions, researches with sources, and
                  shows its work as it streams.
                </p>
              </div>
            ) : (
              messages.map((m, i) => (
                <div key={i} className={`mb-5 flex ${m.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-2.5 text-[0.95rem] ${
                      m.role === 'user'
                        ? 'bg-zinc-100 text-zinc-900'
                        : 'border border-zinc-800 bg-zinc-900 text-zinc-100'
                    }`}
                  >
                    {m.role === 'user' ? (
                      <p className="whitespace-pre-wrap leading-relaxed">{m.content}</p>
                    ) : (
                      <div className={streaming && i === messages.length - 1 ? 'stream-caret' : ''}>
                        <Markdown text={m.content} />
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        {/* Input */}
        <div className="border-t border-zinc-800 bg-zinc-950 px-4 py-3">
          <div className="mx-auto flex max-w-3xl items-end gap-2">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={onKeyDown}
              rows={1}
              placeholder={models.length === 0 ? 'Waiting for models…' : 'Message Actlet…  (Enter to send, Shift+Enter for newline)'}
              disabled={streaming || models.length === 0}
              className="slim-scroll max-h-40 flex-1 resize-none rounded-xl border border-zinc-700 bg-zinc-900 px-4 py-2.5 text-sm text-zinc-100 placeholder-zinc-500 focus:border-zinc-500 focus:outline-none disabled:opacity-50"
            />
            <button
              onClick={() => void send()}
              disabled={!canSend}
              className="rounded-xl bg-zinc-100 px-4 py-2.5 text-sm font-medium text-zinc-900 transition hover:bg-white disabled:cursor-not-allowed disabled:opacity-40"
            >
              {streaming ? '…' : 'Send'}
            </button>
          </div>
          <p className="mx-auto mt-2 max-w-3xl text-[11px] text-zinc-600">
            Streaming live from your backend. Budgets are enforced per task — a paused task tells you why.
          </p>
        </div>
      </div>
    </div>
  )
}
