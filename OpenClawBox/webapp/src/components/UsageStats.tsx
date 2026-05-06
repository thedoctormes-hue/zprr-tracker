interface UsageStatsProps {
  userId: number
}

const STATS = {
  daily_limit: 5000,
  used_today: 1250,
  remaining: 3750,
  percentage: 25
}

export default function UsageStats({ userId }: UsageStatsProps) {
  const percentage = STATS.percentage
  const color = percentage > 75 ? 'bg-red-500' : percentage > 50 ? 'bg-yellow-500' : 'bg-green-500'

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
        📊 Использование (сегодня)
      </h2>
      
      <div className="space-y-3">
        <div className="flex justify-between text-sm">
          <span>Использовано</span>
          <span className="font-medium">{STATS.used_today} токенов</span>
        </div>
        
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div 
            className={`h-2 rounded-full transition-all ${color}`}
            style={{ width: `${percentage}%` }}
          />
        </div>
        
        <div className="flex justify-between text-sm">
          <span>Осталось</span>
          <span className="font-medium">{STATS.remaining} токенов</span>
        </div>
      </div>
    </div>
  )
}