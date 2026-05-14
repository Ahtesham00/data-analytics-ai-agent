import { useState } from 'react'
import {
  Plus,
  MessageSquare,
  Trash2,
  Pencil,
  Check,
  X,
  BarChart2,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react'

function ConversationItem({ conv, isActive, onSelect, onDelete, onRename }) {
  const [editing, setEditing] = useState(false)
  const [draftTitle, setDraftTitle] = useState('')
  const [hovering, setHovering] = useState(false)

  function startEdit(e) {
    e.stopPropagation()
    setDraftTitle(conv.title)
    setEditing(true)
  }

  function commitEdit(e) {
    e?.stopPropagation()
    const trimmed = draftTitle.trim()
    if (trimmed && trimmed !== conv.title) {
      onRename(conv.conversation_id, trimmed)
    }
    setEditing(false)
  }

  function cancelEdit(e) {
    e?.stopPropagation()
    setEditing(false)
  }

  function handleDelete(e) {
    e.stopPropagation()
    onDelete(conv.conversation_id)
  }

  const providerBadge = conv.provider === 'openai'
    ? 'bg-green-900/40 text-green-400 border-green-700/40'
    : 'bg-indigo-900/40 text-indigo-400 border-indigo-700/40'

  return (
    <div
      onClick={() => !editing && onSelect(conv.conversation_id)}
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
      className={`group flex items-center gap-2 px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${isActive
          ? 'bg-slate-700 text-white'
          : 'hover:bg-slate-800 text-slate-400 hover:text-slate-200'
        }`}
    >
      <MessageSquare size={14} className="flex-shrink-0" />

      {editing ? (
        <input
          autoFocus
          value={draftTitle}
          onChange={(e) => setDraftTitle(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter') commitEdit()
            if (e.key === 'Escape') cancelEdit()
          }}
          onClick={(e) => e.stopPropagation()}
          className="flex-1 min-w-0 bg-slate-600 text-white text-xs rounded px-1.5 py-0.5 outline-none focus:ring-1 focus:ring-indigo-500"
        />
      ) : (
        <span className="flex-1 min-w-0 text-xs font-medium truncate">{conv.title}</span>
      )}

      {editing ? (
        <div className="flex items-center gap-1 flex-shrink-0">
          <button onClick={commitEdit} className="text-green-400 hover:text-green-300 p-0.5">
            <Check size={12} />
          </button>
          <button onClick={cancelEdit} className="text-slate-500 hover:text-slate-300 p-0.5">
            <X size={12} />
          </button>
        </div>
      ) : (
        (hovering || isActive) && (
          <div className="flex items-center gap-1 flex-shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">
            <button
              onClick={startEdit}
              className="p-0.5 text-slate-500 hover:text-slate-200 transition-colors"
              title="Rename"
            >
              <Pencil size={12} />
            </button>
            <button
              onClick={handleDelete}
              className="p-0.5 text-slate-500 hover:text-red-400 transition-colors"
              title="Delete"
            >
              <Trash2 size={12} />
            </button>
          </div>
        )
      )}

      {!editing && !hovering && !isActive && (
        <span className={`flex-shrink-0 text-[9px] font-medium px-1.5 py-0.5 rounded border ${providerBadge}`}>
          {conv.provider === 'openai' ? 'GPT' : 'Claude'}
        </span>
      )}
    </div>
  )
}

export default function Sidebar({
  conversations,
  activeId,
  onSelect,
  onNew,
  onDelete,
  onRename,
  provider,
}) {
  const [collapsed, setCollapsed] = useState(false)

  if (collapsed) {
    return (
      <div className="flex flex-col items-center gap-3 w-12 bg-slate-950 border-r border-slate-700/50 py-4">
        <div className="w-8 h-8 rounded-lg bg-indigo-900/50 flex items-center justify-center">
          <BarChart2 size={16} className="text-indigo-400" />
        </div>
        <button
          onClick={onNew}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          title="New chat"
        >
          <Plus size={16} />
        </button>
        <div className="flex-1" />
        <button
          onClick={() => setCollapsed(false)}
          className="w-8 h-8 rounded-lg flex items-center justify-center text-slate-500 hover:text-slate-200 hover:bg-slate-800 transition-colors"
        >
          <ChevronRight size={16} />
        </button>
      </div>
    )
  }

  return (
    <div className="flex flex-col w-64 bg-slate-950 border-r border-slate-700/50 flex-shrink-0">
      {/* Header */}
      <div className="flex items-center gap-2 px-4 py-4 border-b border-slate-800">
        <div className="w-7 h-7 rounded-lg bg-indigo-900/60 flex items-center justify-center flex-shrink-0">
          <BarChart2 size={14} className="text-indigo-400" />
        </div>
        <span className="flex-1 font-semibold text-sm text-white truncate">Data Analytics AI Agent</span>
        <button
          onClick={() => setCollapsed(true)}
          className="text-slate-600 hover:text-slate-300 transition-colors"
        >
          <ChevronLeft size={16} />
        </button>
      </div>

      {/* New chat button */}
      <div className="px-3 py-3">
        <button
          onClick={() => onNew(provider)}
          className="w-full flex items-center gap-2 px-3 py-2 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 border border-indigo-700/40 hover:border-indigo-600/60 text-indigo-300 hover:text-indigo-200 text-xs font-medium transition-all"
        >
          <Plus size={14} />
          New Conversation
        </button>
      </div>

      {/* Conversation list */}
      <div className="flex-1 overflow-y-auto scrollbar-thin px-2 pb-2 space-y-0.5">
        {conversations.length === 0 ? (
          <p className="text-xs text-slate-600 px-3 py-4 text-center">No conversations yet</p>
        ) : (
          conversations.map((conv) => (
            <ConversationItem
              key={conv.conversation_id}
              conv={conv}
              isActive={conv.conversation_id === activeId}
              onSelect={onSelect}
              onDelete={onDelete}
              onRename={onRename}
            />
          ))
        )}
      </div>
    </div>
  )
}
