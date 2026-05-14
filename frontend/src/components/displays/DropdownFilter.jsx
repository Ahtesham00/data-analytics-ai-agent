import { useState } from 'react'
import { ChevronDown } from 'lucide-react'

export default function DropdownFilter({ label, options = [], default_option_index = 0, onSelect, disabled }) {
  const [selected, setSelected] = useState(default_option_index)

  function handleChange(e) {
    const idx = Number(e.target.value)
    setSelected(idx)
    onSelect?.(options[idx]?.prompt)
  }

  return (
    <div className="flex items-center gap-2">
      <span className="text-xs font-medium text-slate-400">{label}</span>
      <div className="relative">
        <select
          value={selected}
          onChange={handleChange}
          disabled={disabled}
          className="appearance-none pl-3 pr-7 py-1.5 rounded-lg text-xs font-medium bg-slate-700 border border-slate-600 text-slate-200 cursor-pointer hover:bg-slate-600 transition-colors disabled:opacity-40 disabled:cursor-not-allowed focus:outline-none focus:ring-1 focus:ring-indigo-500"
        >
          {options.map((opt, i) => (
            <option key={i} value={i}>
              {opt.label}
            </option>
          ))}
        </select>
        <ChevronDown size={12} className="absolute right-2 top-1/2 -translate-y-1/2 text-slate-400 pointer-events-none" />
      </div>
    </div>
  )
}
