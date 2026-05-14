import { useState, useRef, useEffect } from 'react'
import { Send, Loader2 } from 'lucide-react'

const PROVIDERS = [
  { value: 'anthropic', label: 'Claude' },
  { value: 'openai', label: 'GPT-4o' },
]

export default function ChatInput({ onSend, isStreaming, provider, onProviderChange }) {
  const [text, setText] = useState('')
  const textareaRef = useRef(null)

  // Auto-resize textarea
  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 180)}px`
  }, [text])

  function handleSubmit(e) {
    e?.preventDefault()
    const trimmed = text.trim()
    if (!trimmed || isStreaming) return
    onSend(trimmed)
    setText('')
  }

  function handleKeyDown(e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit()
    }
  }

  return (
    <div className="px-4 pb-4 pt-3 border-t border-slate-700/60 bg-slate-900">
      <div className="flex items-end gap-2 rounded-xl border border-slate-600 bg-slate-800 px-3 py-2 focus-within:border-indigo-500 transition-colors">
        <textarea
          ref={textareaRef}
          rows={1}
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about your Superstore data..."
          disabled={isStreaming}
          className="flex-1 resize-none bg-transparent text-sm text-slate-100 placeholder-slate-500 outline-none min-h-[24px] max-h-[180px] leading-6 disabled:opacity-50"
        />
        <div className="flex items-center gap-2 flex-shrink-0 pb-0.5">
          <select
            value={provider}
            onChange={(e) => onProviderChange(e.target.value)}
            disabled={isStreaming}
            className="text-xs bg-slate-700 border border-slate-600 text-slate-300 rounded-lg px-2 py-1.5 cursor-pointer hover:bg-slate-600 transition-colors focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:opacity-40"
          >
            {PROVIDERS.map((p) => (
              <option key={p.value} value={p.value}>{p.label}</option>
            ))}
          </select>
          <button
            onClick={handleSubmit}
            disabled={!text.trim() || isStreaming}
            className="w-8 h-8 rounded-lg flex items-center justify-center bg-indigo-600 hover:bg-indigo-500 disabled:bg-slate-700 disabled:text-slate-500 text-white transition-colors"
          >
            {isStreaming ? (
              <Loader2 size={15} className="animate-spin" />
            ) : (
              <Send size={15} />
            )}
          </button>
        </div>
      </div>
      <p className="text-xs text-slate-600 text-center mt-2">
        Shift+Enter for new line · Enter to send
      </p>
    </div>
  )
}
