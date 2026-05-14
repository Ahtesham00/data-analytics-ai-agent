import { Sparkles } from 'lucide-react'

export default function SuggestionChips({ suggestions = [], onSelect, disabled }) {
  return (
    <div className="flex flex-wrap gap-2 mt-1">
      {suggestions.map((chip, i) => (
        <button
          key={i}
          onClick={() => !disabled && onSelect?.(chip.prompt)}
          disabled={disabled}
          className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-slate-700 hover:bg-indigo-600/80 border border-slate-600 hover:border-indigo-500 text-slate-300 hover:text-white transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
        >
          <Sparkles size={11} className="text-indigo-400" />
          {chip.label}
        </button>
      ))}
    </div>
  )
}
