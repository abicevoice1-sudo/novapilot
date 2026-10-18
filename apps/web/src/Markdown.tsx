import React from 'react'

/**
 * Tiny markdown-ish renderer — no heavy dependency.
 * Supports fenced code blocks, inline code, **bold**, *italic*,
 * headings, unordered lists, and paragraphs.
 */

function renderInline(text: string, keyPrefix: string): React.ReactNode[] {
  const out: React.ReactNode[] = []
  // split on `code`, **bold**, *italic* — keep delimiters
  const re = /(`[^`]+`|\*\*[^*]+\*\*|\*[^*]+\*)/g
  let last = 0
  let m: RegExpExecArray | null
  let i = 0
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) out.push(text.slice(last, m.index))
    const tok = m[0]
    const key = `${keyPrefix}-i${i++}`
    if (tok.startsWith('`')) {
      out.push(
        <code key={key} className="rounded bg-zinc-800 px-1 py-0.5 font-mono text-[0.85em] text-amber-200">
          {tok.slice(1, -1)}
        </code>,
      )
    } else if (tok.startsWith('**')) {
      out.push(<strong key={key}>{tok.slice(2, -2)}</strong>)
    } else {
      out.push(<em key={key}>{tok.slice(1, -1)}</em>)
    }
    last = m.index + tok.length
  }
  if (last < text.length) out.push(text.slice(last))
  return out
}

function renderBlock(text: string, keyPrefix: string): React.ReactNode[] {
  const lines = text.split('\n')
  const out: React.ReactNode[] = []
  let list: string[] = []
  let para: string[] = []
  let i = 0

  const flushList = () => {
    if (list.length) {
      out.push(
        <ul key={`${keyPrefix}-ul${i++}`} className="my-1 list-disc space-y-0.5 pl-5">
          {list.map((item, k) => (
            <li key={k}>{renderInline(item, `${keyPrefix}-li${k}`)}</li>
          ))}
        </ul>,
      )
      list = []
    }
  }
  const flushPara = () => {
    if (para.length) {
      out.push(
        <p key={`${keyPrefix}-p${i++}`} className="my-1 leading-relaxed">
          {renderInline(para.join(' '), `${keyPrefix}-pt`)}
        </p>,
      )
      para = []
    }
  }

  for (const line of lines) {
    const t = line.trim()
    if (/^#{1,3}\s/.test(t)) {
      flushPara()
      flushList()
      const level = t.match(/^#+/)![0].length
      const content = t.replace(/^#+\s*/, '')
      const cls =
        level === 1
          ? 'text-lg font-semibold mt-3 mb-1'
          : level === 2
            ? 'text-base font-semibold mt-2 mb-1'
            : 'text-sm font-semibold mt-2 mb-1'
      out.push(
        <div key={`${keyPrefix}-h${i++}`} className={cls}>
          {renderInline(content, `${keyPrefix}-ht`)}
        </div>,
      )
    } else if (/^([-*]|\d+\.)\s+/.test(t)) {
      flushPara()
      list.push(t.replace(/^([-*]|\d+\.)\s+/, ''))
    } else if (t === '') {
      flushPara()
      flushList()
    } else {
      para.push(t)
    }
  }
  flushPara()
  flushList()
  return out
}

export function Markdown({ text }: { text: string }): React.ReactElement {
  // Split on fenced code blocks; odd indices are the code contents.
  const parts = text.split(/```(?:\w+)?\n?([\s\S]*?)```/g)
  return (
    <>
      {parts.map((part, idx) =>
        idx % 2 === 1 ? (
          <pre
            key={idx}
            className="slim-scroll my-2 overflow-x-auto rounded-lg border border-zinc-800 bg-zinc-950 p-3"
          >
            <code className="font-mono text-[0.83em] leading-relaxed text-zinc-200">{part.replace(/\n$/, '')}</code>
          </pre>
        ) : (
          <React.Fragment key={idx}>{renderBlock(part, `b${idx}`)}</React.Fragment>
        ),
      )}
    </>
  )
}
