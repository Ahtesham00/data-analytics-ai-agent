import { useState } from 'react'
import { ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'

function formatCell(value, type) {
  if (value === null || value === undefined) return '—'
  if (type === 'currency') {
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(value)
  }
  if (type === 'percent') {
    return `${Number(value).toFixed(1)}%`
  }
  if (type === 'number') {
    return Number(value).toLocaleString()
  }
  if (type === 'date') {
    return new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  }
  return String(value)
}

const alignClass = { left: 'text-left', right: 'text-right', center: 'text-center' }

export default function DataTable({
  title,
  description,
  columns = [],
  data = [],
  default_sort,
  default_order = 'desc',
}) {
  const [sortKey, setSortKey] = useState(default_sort ?? null)
  const [sortDir, setSortDir] = useState(default_order)

  function toggleSort(key) {
    if (sortKey === key) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortKey(key)
      setSortDir('desc')
    }
  }

  const sorted = [...data].sort((a, b) => {
    if (!sortKey) return 0
    const av = a[sortKey]
    const bv = b[sortKey]
    if (av === bv) return 0
    const cmp = av < bv ? -1 : 1
    return sortDir === 'asc' ? cmp : -cmp
  })

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/60 overflow-hidden">
      {(title || description) && (
        <div className="px-4 py-3 border-b border-slate-700">
          {title && <h3 className="font-semibold text-white text-sm">{title}</h3>}
          {description && <p className="text-xs text-slate-400 mt-0.5">{description}</p>}
        </div>
      )}
      <div className="overflow-x-auto scrollbar-thin">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-slate-700">
              {columns.map((col) => {
                const active = sortKey === col.key
                const align = col.align ?? (col.type === 'number' || col.type === 'currency' || col.type === 'percent' ? 'right' : 'left')
                return (
                  <th
                    key={col.key}
                    className={`px-4 py-2.5 font-medium text-slate-400 text-xs uppercase tracking-wider ${alignClass[align]} cursor-pointer select-none hover:text-slate-200 whitespace-nowrap`}
                    onClick={() => toggleSort(col.key)}
                  >
                    <span className="inline-flex items-center gap-1">
                      {col.label}
                      {active ? (
                        sortDir === 'asc' ? <ChevronUp size={12} /> : <ChevronDown size={12} />
                      ) : (
                        <ChevronsUpDown size={12} className="opacity-30" />
                      )}
                    </span>
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {sorted.map((row, ri) => (
              <tr
                key={ri}
                className={`border-b border-slate-700/50 ${ri % 2 === 0 ? 'bg-transparent' : 'bg-slate-700/20'} hover:bg-slate-700/40 transition-colors`}
              >
                {columns.map((col) => {
                  const align = col.align ?? (col.type === 'number' || col.type === 'currency' || col.type === 'percent' ? 'right' : 'left')
                  return (
                    <td key={col.key} className={`px-4 py-2.5 text-slate-300 ${alignClass[align]} whitespace-nowrap`}>
                      {formatCell(row[col.key], col.type)}
                    </td>
                  )
                })}
              </tr>
            ))}
            {sorted.length === 0 && (
              <tr>
                <td colSpan={columns.length} className="px-4 py-8 text-center text-slate-500 text-sm">
                  No data
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  )
}
