import {
  ResponsiveContainer,
  LineChart as ReLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from 'recharts'

const PALETTE = {
  blue:   '#3b82f6',
  green:  '#22c55e',
  purple: '#a855f7',
  orange: '#f97316',
  red:    '#ef4444',
  yellow: '#eab308',
}

const DEFAULT_COLORS = ['#3b82f6', '#22c55e', '#a855f7', '#f97316', '#ef4444', '#eab308']

function formatTick(value, prefix = '', suffix = '') {
  if (typeof value === 'number') {
    if (Math.abs(value) >= 1_000_000) return `${prefix}${(value / 1_000_000).toFixed(1)}M${suffix}`
    if (Math.abs(value) >= 1_000)     return `${prefix}${(value / 1_000).toFixed(1)}k${suffix}`
    return `${prefix}${value}${suffix}`
  }
  return String(value)
}

export default function LineChart({ title, description, data = [], x_key, y_keys = [], value_prefix = '', value_suffix = '' }) {
  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-4">
      <div className="mb-3">
        <h3 className="font-semibold text-white text-sm">{title}</h3>
        {description && <p className="text-xs text-slate-400 mt-0.5">{description}</p>}
      </div>
      <ResponsiveContainer width="100%" height={240}>
        <ReLineChart data={data} margin={{ top: 4, right: 16, bottom: 4, left: 8 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis
            dataKey={x_key}
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={{ stroke: '#334155' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#94a3b8', fontSize: 11 }}
            axisLine={false}
            tickLine={false}
            tickFormatter={(v) => formatTick(v, value_prefix, value_suffix)}
          />
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
            labelStyle={{ color: '#94a3b8', fontSize: 12 }}
            itemStyle={{ fontSize: 12 }}
            formatter={(value) => [`${value_prefix}${Number(value).toLocaleString()}${value_suffix}`]}
          />
          {y_keys.length > 1 && (
            <Legend
              wrapperStyle={{ fontSize: 11, color: '#94a3b8' }}
            />
          )}
          {y_keys.map((yk, i) => (
            <Line
              key={yk.key}
              type="monotone"
              dataKey={yk.key}
              name={yk.label}
              stroke={PALETTE[yk.color] ?? DEFAULT_COLORS[i % DEFAULT_COLORS.length]}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4 }}
            />
          ))}
        </ReLineChart>
      </ResponsiveContainer>
    </div>
  )
}
