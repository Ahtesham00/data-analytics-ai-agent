import { useState, useEffect, useCallback, useRef } from 'react'
import Sidebar from './components/Sidebar.jsx'
import ChatWindow from './components/ChatWindow.jsx'
import {
  getConversations,
  createConversation,
  getConversation,
  updateConversation,
  deleteConversation,
  sendMessage,
} from './api/client.js'
import { parseSSEStream } from './lib/parseSSE.js'

/**
 * Convert a DB message (with `content` + `tool_renders`) to the internal
 * `parts` format used for rendering.
 */
function dbMessageToParts(msg) {
  const parts = []
  if (msg.content) {
    parts.push({ type: 'text', content: msg.content })
  }
  if (Array.isArray(msg.tool_renders)) {
    for (const render of msg.tool_renders) {
      parts.push({
        type: 'render',
        render_id: render.render_id,
        tool_name: render.tool_name,
        props: render.props,
      })
    }
  }
  return parts
}

export default function App() {
  const [conversations, setConversations] = useState([])
  const [activeId, setActiveId] = useState(null)
  const [messages, setMessages] = useState([])
  const [isStreaming, setIsStreaming] = useState(false)
  const [provider, setProvider] = useState('anthropic')
  const [loadingConv, setLoadingConv] = useState(false)
  const [error, setError] = useState(null)

  // Ref to the in-progress streaming message id
  const streamingMsgIdRef = useRef(null)

  // ── Load conversations on mount ───────────────────────────────────────────
  useEffect(() => {
    getConversations()
      .then((list) => {
        setConversations(list)
        if (list.length > 0) {
          selectConversation(list[0].conversation_id)
        }
      })
      .catch(() => setError('Failed to load conversations'))
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  // ── Select a conversation ─────────────────────────────────────────────────
  const selectConversation = useCallback(async (id) => {
    setActiveId(id)
    setLoadingConv(true)
    setError(null)
    try {
      const conv = await getConversation(id)
      setProvider(conv.provider ?? 'anthropic')
      const msgs = (conv.messages ?? []).map((m) => ({
        id: m.message_id,
        role: m.role,
        parts: dbMessageToParts(m),
        isStreaming: false,
        error: null,
      }))
      setMessages(msgs)
    } catch {
      setError('Failed to load conversation')
    } finally {
      setLoadingConv(false)
    }
  }, [])

  // ── Create new conversation ───────────────────────────────────────────────
  const handleNew = useCallback(async (prov = provider) => {
    try {
      const conv = await createConversation(prov)
      setConversations((prev) => [conv, ...prev])
      setActiveId(conv.conversation_id)
      setMessages([])
      setProvider(prov)
    } catch {
      setError('Failed to create conversation')
    }
  }, [provider])

  // ── Delete conversation ───────────────────────────────────────────────────
  const handleDelete = useCallback(async (id) => {
    try {
      await deleteConversation(id)
      setConversations((prev) => prev.filter((c) => c.conversation_id !== id))
      if (activeId === id) {
        setActiveId(null)
        setMessages([])
      }
    } catch {
      setError('Failed to delete conversation')
    }
  }, [activeId])

  // ── Rename conversation ───────────────────────────────────────────────────
  const handleRename = useCallback(async (id, title) => {
    try {
      const updated = await updateConversation(id, { title })
      setConversations((prev) =>
        prev.map((c) => (c.conversation_id === id ? { ...c, title: updated.title } : c))
      )
    } catch {
      setError('Failed to rename conversation')
    }
  }, [])

  // ── Send message + stream response ───────────────────────────────────────
  const handleSend = useCallback(async (text) => {
    if (isStreaming) return

    let convId = activeId

    // Auto-create a conversation if none is active
    if (!convId) {
      try {
        const conv = await createConversation(provider)
        setConversations((prev) => [conv, ...prev])
        setActiveId(conv.conversation_id)
        convId = conv.conversation_id
      } catch {
        setError('Failed to create conversation')
        return
      }
    }

    // Add user message
    const userMsgId = crypto.randomUUID()
    setMessages((prev) => [
      ...prev,
      { id: userMsgId, role: 'user', parts: [{ type: 'text', content: text }], isStreaming: false, error: null },
    ])

    // Add placeholder assistant message
    const assistantMsgId = crypto.randomUUID()
    streamingMsgIdRef.current = assistantMsgId
    setMessages((prev) => [
      ...prev,
      { id: assistantMsgId, role: 'assistant', parts: [], isStreaming: true, error: null },
    ])

    setIsStreaming(true)
    setError(null)

    try {
      const response = await sendMessage(convId, text, provider)

      for await (const { event, data } of parseSSEStream(response)) {
        const msgId = streamingMsgIdRef.current
        if (!msgId) break

        if (event === 'text') {
          setMessages((prev) =>
            prev.map((m) => {
              if (m.id !== msgId) return m
              const parts = [...m.parts]
              const last = parts[parts.length - 1]
              if (last && last.type === 'text') {
                return {
                  ...m,
                  parts: [...parts.slice(0, -1), { type: 'text', content: last.content + data.content }],
                }
              }
              return { ...m, parts: [...parts, { type: 'text', content: data.content }] }
            })
          )
        } else if (event === 'tool_display') {
          setMessages((prev) =>
            prev.map((m) => {
              if (m.id !== msgId) return m
              return {
                ...m,
                parts: [
                  ...m.parts,
                  {
                    type: 'render',
                    render_id: data.render_id,
                    tool_name: data.tool_name,
                    props: data.props,
                  },
                ],
              }
            })
          )
        } else if (event === 'error') {
          setMessages((prev) =>
            prev.map((m) => {
              if (m.id !== msgId) return m
              return { ...m, isStreaming: false, error: data.message }
            })
          )
        } else if (event === 'done') {
          // Finalize message and refresh conversation title
          setMessages((prev) =>
            prev.map((m) => {
              if (m.id !== msgId) return m
              return { ...m, id: data.message_id ?? m.id, isStreaming: false }
            })
          )
          // Refresh sidebar title (it may have been auto-set by the backend)
          getConversations()
            .then(setConversations)
            .catch(() => {})
        }
      }
    } catch (err) {
      const msgId = streamingMsgIdRef.current
      if (msgId) {
        setMessages((prev) =>
          prev.map((m) => {
            if (m.id !== msgId) return m
            return { ...m, isStreaming: false, error: err.message }
          })
        )
      }
    } finally {
      streamingMsgIdRef.current = null
      setIsStreaming(false)
    }
  }, [activeId, isStreaming, provider])

  // ── Provider change ───────────────────────────────────────────────────────
  const handleProviderChange = useCallback((prov) => {
    setProvider(prov)
    if (activeId) {
      updateConversation(activeId, { provider: prov }).catch(() => {})
    }
  }, [activeId])

  // ── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="flex h-full bg-slate-900">
      <Sidebar
        conversations={conversations}
        activeId={activeId}
        onSelect={selectConversation}
        onNew={handleNew}
        onDelete={handleDelete}
        onRename={handleRename}
        provider={provider}
      />

      <div className="flex flex-col flex-1 min-w-0">
        {/* Top bar */}
        <div className="flex items-center justify-between px-5 py-3 border-b border-slate-700/60 bg-slate-900/80 backdrop-blur-sm flex-shrink-0">
          <div className="min-w-0">
            {activeId ? (
              <h1 className="font-semibold text-sm text-white truncate">
                {conversations.find((c) => c.conversation_id === activeId)?.title ?? 'Chat'}
              </h1>
            ) : (
              <h1 className="font-semibold text-sm text-slate-400">Select or start a conversation</h1>
            )}
          </div>
          {activeId && (
            <span className="flex-shrink-0 text-xs text-slate-500 ml-4">
              {provider === 'openai' ? 'GPT-4o' : 'Claude'}
            </span>
          )}
        </div>

        {/* Error banner */}
        {error && (
          <div className="mx-4 mt-3 px-4 py-2.5 rounded-lg bg-red-900/30 border border-red-700/50 text-red-300 text-sm flex items-center justify-between">
            {error}
            <button onClick={() => setError(null)} className="ml-3 text-red-400 hover:text-red-200 text-xs">
              Dismiss
            </button>
          </div>
        )}

        {loadingConv ? (
          <div className="flex-1 flex items-center justify-center">
            <div className="flex flex-col items-center gap-3">
              <div className="w-8 h-8 rounded-full border-2 border-indigo-500 border-t-transparent animate-spin" />
              <span className="text-xs text-slate-500">Loading conversation...</span>
            </div>
          </div>
        ) : (
          <ChatWindow
            messages={messages}
            isStreaming={isStreaming}
            provider={provider}
            onProviderChange={handleProviderChange}
            onSendMessage={handleSend}
          />
        )}
      </div>
    </div>
  )
}
