import { useEffect, useRef } from 'react'
import MessageBubble from './MessageBubble.jsx'
import ChatInput from './ChatInput.jsx'
import { BarChart2, Sparkles } from 'lucide-react'

const STARTER_PROMPTS = [
  'What are the total sales by region?',
  'Show me profit trends over time',
  'Which product categories are most profitable?',
  'Top 10 customers by revenue',
]

function WelcomeScreen({ onSelect }) {
  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 text-center">
      <div className="w-16 h-16 rounded-2xl bg-indigo-900/50 border border-indigo-700/50 flex items-center justify-center mb-5">
        <BarChart2 size={32} className="text-indigo-400" />
      </div>
      <h2 className="text-xl font-semibold text-white mb-2">Superstore Analytics AI</h2>
      <p className="text-slate-400 text-sm max-w-sm mb-8">
        Ask questions about your Superstore data in plain English. The AI will query the database and visualize results for you.
      </p>
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 w-full max-w-md">
        {STARTER_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            onClick={() => onSelect(prompt)}
            className="flex items-center gap-2 px-4 py-3 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-indigo-600/50 text-left text-sm text-slate-300 hover:text-white transition-all group"
          >
            <Sparkles size={14} className="text-indigo-500 flex-shrink-0 group-hover:text-indigo-400" />
            {prompt}
          </button>
        ))}
      </div>
    </div>
  )
}

export default function ChatWindow({
  messages,
  isStreaming,
  provider,
  onProviderChange,
  onSendMessage,
}) {
  const bottomRef = useRef(null)
  const scrollRef = useRef(null)

  // Auto-scroll to bottom when messages update
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const hasMessages = messages.length > 0

  return (
    <div className="flex flex-col flex-1 min-h-0">
      {/* Messages area */}
      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto scrollbar-thin"
      >
        {hasMessages ? (
          <div className="max-w-3xl mx-auto px-4 py-6 space-y-6">
            {messages.map((msg) => (
              <MessageBubble
                key={msg.id}
                message={msg}
                onSendMessage={onSendMessage}
                isStreaming={isStreaming}
              />
            ))}
            <div ref={bottomRef} />
          </div>
        ) : (
          <WelcomeScreen onSelect={onSendMessage} />
        )}
      </div>

      {/* Input */}
      <ChatInput
        onSend={onSendMessage}
        isStreaming={isStreaming}
        provider={provider}
        onProviderChange={onProviderChange}
      />
    </div>
  )
}
