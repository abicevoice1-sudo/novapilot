import React, { useEffect, useState } from 'react'
import Chat from './pages/Chat'
import Settings from './pages/Settings'
import Tasks from './pages/Tasks'
import TaskDetail from './pages/TaskDetail'
import { getHealth } from './api'

type Route =
  | { name: 'chat' }
  | { name: 'settings' }
  | { name: 'tasks' }
  | { name: 'task'; id: string }

function parseRoute(pathname: string): Route {
  if (pathname === '/settings') return { name: 'settings' }
  if (pathname === '/tasks') return { name: 'tasks' }
  const m = /^\/tasks\/([^/]+)$/.exec(pathname)
  if (m) return { name: 'task', id: decodeURIComponent(m[1]) }
  return { name: 'chat' }
}

function useRoute(): { route: Route; navigate: (to: string) => void } {
  const [route, setRoute] = useState<Route>(() => parseRoute(window.location.pathname))
  useEffect(() => {
    const onPop = () => setRoute(parseRoute(window.location.pathname))
    window.addEventListener('popstate', onPop)
    return () => window.removeEventListener('popstate', onPop)
  }, [])
  const navigate = (to: string) => {
    window.history.pushState({}, '', to)
    setRoute(parseRoute(to))
  }
  return { route, navigate }
}

function HealthDot(): React.ReactElement {
  const [ok, setOk] = useState<boolean | null>(null)
  useEffect(() => {
    let alive = true
    const check = () =>
      getHealth()
        .then((h) => alive && setOk(h.ok))
        .catch(() => alive && setOk(false))
    void check()
    const id = setInterval(check, 30000)
    return () => {
      alive = false
      clearInterval(id)
    }
  }, [])
  const color = ok === null ? 'bg-zinc-600' : ok ? 'bg-emerald-400' : 'bg-red-400'
  const label = ok === null ? 'checking backend…' : ok ? 'backend healthy' : 'backend unreachable'
  return (
    <span title={label} className={`inline-block h-2.5 w-2.5 rounded-full ${color}`} aria-label={label} />
  )
}

export default function App(): React.ReactElement {
  const { route, navigate } = useRoute()

  const link = (to: string, label: string, active: boolean) => (
    <button
      key={to}
      onClick={() => navigate(to)}
      className={`rounded-lg px-3 py-1.5 text-sm transition ${
        active ? 'bg-zinc-800 text-zinc-100' : 'text-zinc-400 hover:text-zinc-200'
      }`}
    >
      {label}
    </button>
  )

  return (
    <div className="flex h-full flex-col bg-zinc-950">
      <header className="flex items-center gap-4 border-b border-zinc-800 px-4 py-2.5">
        <button onClick={() => navigate('/')} className="flex items-center gap-2" aria-label="NovaPilot home">
          <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-zinc-100 text-base text-zinc-900">
            ✦
          </span>
          <span className="text-[15px] font-semibold tracking-tight text-zinc-100">NovaPilot</span>
        </button>
        <nav className="flex items-center gap-1">
          {link('/', 'Chat', route.name === 'chat')}
          {link('/tasks', 'Tasks', route.name === 'tasks' || route.name === 'task')}
          {link('/settings', 'Settings', route.name === 'settings')}
        </nav>
        <div className="ml-auto flex items-center gap-2">
          <HealthDot />
        </div>
      </header>
      <main className="min-h-0 flex-1">
        {route.name === 'settings' ? (
          <Settings />
        ) : route.name === 'tasks' ? (
          <Tasks onOpenTask={(id) => navigate(`/tasks/${encodeURIComponent(id)}`)} />
        ) : route.name === 'task' ? (
          <TaskDetail key={route.id} id={route.id} onBack={() => navigate('/tasks')} />
        ) : (
          <Chat />
        )}
      </main>
    </div>
  )
}
