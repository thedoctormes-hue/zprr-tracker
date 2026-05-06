interface DashboardProps {
  userId: number
}

const PROVIDERS = [
  { name: 'groq', emoji: '🟢', status: 'Доступен', limit: '300/сутки' },
  { name: 'mistral', emoji: '🟢', status: 'Доступен', limit: '500K/мес' },
  { name: 'google', emoji: '🟡', status: 'Ограничен', limit: '15/сутки' },
  { name: 'together', emoji: '🟢', status: 'Доступен', limit: '$25 кредит' },
  { name: 'cohere', emoji: '🟢', status: 'Доступен', limit: '1M/мес' },
  { name: 'openrouter', emoji: '🟢', status: 'Доступен', limit: 'Premium' },
]

export default function Dashboard({ userId }: DashboardProps) {
  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
        🤖 Провайдеры
      </h2>
      <div className="grid grid-cols-2 gap-3">
        {PROVIDERS.map(p => (
          <div key={p.name} className="bg-gray-50 p-3 rounded-lg">
            <div className="font-medium">{p.emoji} {p.name}</div>
            <div className="text-xs" style={{ color: '#6b7280' }}>{p.status}</div>
            <div className="text-xs" style={{ color: '#9ca3af' }}>{p.limit}</div>
          </div>
        ))}
      </div>
    </div>
  )
}