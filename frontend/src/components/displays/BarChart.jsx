import {
  ResponsiveContainer,
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  Cell,
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

export default function BarChart({
  title,
  description,
  data = [],
  x_key,
  y_keys = [],
  value_prefix = '',
  value_suffix = '',
  orientation = 'vertical',
  show_negative_color = false,
}) {
  const isHorizontal = orientation === 'horizontal'
  const barHeight = isHorizontal ? Math.max(data.length * 28, 120) : 240

  return (
    <div className="rounded-xl border border-slate-700 bg-slate-800/60 p-4">
      <div className="mb-3">
        <h3 className="font-semibold text-white text-sm">{title}</h3>
        {description && <p className="text-xs text-slate-400 mt-0.5">{description}</p>}
      </div>
      <ResponsiveContainer width="100%" height={barHeight}>
        <ReBarChart
          data={data}
          layout={isHorizontal ? 'vertical' : 'horizontal'}
          margin={{ top: 4, right: 16, bottom: isHorizontal ? 4 : 16, left: 8 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          {isHorizontal ? (
            <>
              <XAxis
                type="number"
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                axisLine={false}
                tickLine={false}
                tickFormatter={(v) => formatTick(v, value_prefix, value_suffix)}
              />
              <YAxis
                type="category"
                dataKey={x_key}
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                axisLine={{ stroke: '#334155' }}
                tickLine={false}
                width={120}
              />
            </>
          ) : (
            <>
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
            </>
          )}
          <Tooltip
            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: 8 }}
            labelStyle={{ color: '#94a3b8', fontSize: 12 }}
            itemStyle={{ fontSize: 12 }}
            formatter={(value) => [`${value_prefix}${Number(value).toLocaleString()}${value_suffix}`]}
          />
          {y_keys.length > 1 && (
            <Legend wrapperStyle={{ fontSize: 11, color: '#94a3b8' }} />
          )}
          {y_keys.map((yk, i) => {
            const baseColor = PALETTE[yk.color] ?? DEFAULT_COLORS[i % DEFAULT_COLORS.length]
            return (
              <Bar key={yk.key} dataKey={yk.key} name={yk.label} fill={baseColor} radius={[3, 3, 0, 0]}>
                {show_negative_color &&
                  data.map((entry, idx) => (
                    <Cell
                      key={idx}
                      fill={entry[yk.key] < 0 ? '#ef4444' : baseColor}
                    />
                  ))}
              </Bar>
            )
          })}
        </ReBarChart>
      </ResponsiveContainer>
    </div>
  )
}
