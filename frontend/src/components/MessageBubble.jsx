import {
  KpiCard,
  StatBlock,
  LineChart,
  BarChart,
  DataTable,
  SuggestionChips,
  DropdownFilter,
} from './displays/index.js'
import { Bot, User } from 'lucide-react'

function RenderBlock({ tool_name, props, onSendMessage, isStreaming }) {
  switch (tool_name) {
    case 'display_kpi_card':
      return <KpiCard {...props} />
    case 'display_stat_block':
      return <StatBlock {...props} />
    case 'display_line_chart':
      return <LineChart {...props} />
    case 'display_bar_chart':
      return <BarChart {...props} />
    case 'display_table':
      return <DataTable {...props} />
    case 'display_suggestion_chips':
      return (
        <SuggestionChips
          {...props}
          onSelect={onSendMessage}
          disabled={isStreaming}
        />
      )
    case 'display_dropdown_filter':
      return (
        <DropdownFilter
          {...props}
          onSelect={onSendMessage}
          disabled={isStreaming}
        />
      )
    default:
      return null
  }
}

function TypingIndicator() {
  return (
    <div className="flex items-center gap-1 h-5 px-1">
      <span className="typing-dot w-2 h-2 rounded-full bg-slate-400 inline-block" />
      <span className="typing-dot w-2 h-2 rounded-full bg-slate-400 inline-block" />
      <span className="typing-dot w-2 h-2 rounded-full bg-slate-400 inline-block" />
    </div>
  )
}

export default function MessageBubble({ message, onSendMessage, isStreaming }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="flex items-start gap-3 justify-end">
        <div className="max-w-[75%] rounded-2xl rounded-tr-sm bg-indigo-600 px-4 py-3 text-sm text-white leading-relaxed whitespace-pre-wrap shadow-sm">
          {message.parts[0]?.content ?? ''}
        </div>
        <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-600 flex items-center justify-center mt-0.5">
          <User size={14} className="text-slate-300" />
        </div>
      </div>
    )
  }

  // Assistant message
  const parts = message.parts ?? []
  const isEmpty = parts.length === 0

  return (
    <div className="flex items-start gap-3">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-indigo-900/60 border border-indigo-700/50 flex items-center justify-center mt-0.5">
        <Bot size={14} className="text-indigo-400" />
      </div>

      <div className="flex-1 min-w-0 space-y-3">
        {isEmpty && message.isStreaming && <TypingIndicator />}

        {parts.map((part, i) => {
          if (part.type === 'text') {
            return part.content ? (
              <p key={i} className="text-sm text-slate-200 leading-relaxed whitespace-pre-wrap">
                {part.content}
                {message.isStreaming && i === parts.length - 1 && (
                  <span className="inline-block w-0.5 h-4 bg-indigo-400 ml-0.5 animate-pulse align-middle" />
                )}
              </p>
            ) : null
          }

          if (part.type === 'render') {
            return (
              <div key={part.render_id ?? i}>
                <RenderBlock
                  tool_name={part.tool_name}
                  props={part.props}
                  onSendMessage={onSendMessage}
                  isStreaming={isStreaming}
                />
              </div>
            )
          }

          return null
        })}

        {message.error && (
          <div className="rounded-lg bg-red-900/30 border border-red-700/50 px-3 py-2 text-sm text-red-300">
            {message.error}
          </div>
        )}
      </div>
    </div>
  )
}
