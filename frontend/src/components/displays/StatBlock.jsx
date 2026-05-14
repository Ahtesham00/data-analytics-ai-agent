import KpiCard from './KpiCard.jsx'

export default function StatBlock({ stats = [] }) {
  const cols = stats.length <= 2 ? 'grid-cols-2' : stats.length === 3 ? 'grid-cols-3' : 'grid-cols-2 sm:grid-cols-4'

  return (
    <div className={`grid ${cols} gap-3`}>
      {stats.map((stat, i) => (
        <KpiCard key={i} {...stat} compact />
      ))}
    </div>
  )
}
