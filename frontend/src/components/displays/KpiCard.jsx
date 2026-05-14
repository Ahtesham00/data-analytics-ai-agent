import { TrendingUp, TrendingDown, Minus } from 'lucide-react'

const colorMap = {
  default: { border: 'border-slate-600', accent: 'text-slate-400', bg: 'bg-slate-700/40' },
  green:   { border: 'border-green-500', accent: 'text-green-400', bg: 'bg-green-900/20' },
  red:     { border: 'border-red-500',   accent: 'text-red-400',   bg: 'bg-red-900/20' },
  blue:    { border: 'border-blue-500',  accent: 'text-blue-400',  bg: 'bg-blue-900/20' },
  yellow:  { border: 'border-yellow-500',accent: 'text-yellow-400',bg: 'bg-yellow-900/20' },
  purple:  { border: 'border-purple-500',accent: 'text-purple-400',bg: 'bg-purple-900/20' },
}

const TrendIcon = ({ direction, size = 14 }) => {
  if (direction === 'up')      return <TrendingUp size={size} className="text-green-400" />
  if (direction === 'down')    return <TrendingDown size={size} className="text-red-400" />
  return <Minus size={size} className="text-slate-400" />
}

export default function KpiCard({ title, value, subtitle, trend, color = 'default', compact = false }) {
  const c = colorMap[color] ?? colorMap.default

  return (
    <div className={`rounded-xl border ${c.border} ${c.bg} p-4 flex flex-col gap-1 min-w-0`}>
      <span className={`text-xs font-medium uppercase tracking-wider ${c.accent} truncate`}>
        {title}
      </span>
      <span className={`font-bold truncate ${compact ? 'text-2xl' : 'text-3xl'} text-white`}>
        {value}
      </span>
      {subtitle && (
        <span className="text-xs text-slate-400 truncate">{subtitle}</span>
      )}
      {trend && (
        <div className="flex items-center gap-1 mt-1">
          <TrendIcon direction={trend.direction} />
          <span
            className={`text-xs font-semibold ${
              trend.direction === 'up' ? 'text-green-400' :
              trend.direction === 'down' ? 'text-red-400' : 'text-slate-400'
            }`}
          >
            {trend.value}
          </span>
          {trend.label && (
            <span className="text-xs text-slate-500">{trend.label}</span>
          )}
        </div>
      )}
    </div>
  )
}
