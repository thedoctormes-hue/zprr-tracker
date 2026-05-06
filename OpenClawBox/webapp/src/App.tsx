import { useState } from 'react'
import TelegramLogin from './components/TelegramLogin'
import Dashboard from './components/Dashboard'
import ApiKeyDisplay from './components/ApiKeyDisplay'
import UsageStats from './components/UsageStats'
import './App.css'

function App() {
  const [user, setUser] = useState<{ id: number; api_key?: string } | null>(null)

  if (!user) {
    return <TelegramLogin onAuth={setUser} />
  }

  return (
    <div className="min-h-screen" style={{ background: 'linear-gradient(135deg, #f9fafb 0%, #e0f2fe 100%)' }}>
      <header className="bg-white shadow-sm border-b" style={{ borderColor: '#e5e7eb' }}>
        <div className="max-w-4xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-xl font-bold" style={{ color: '#0ea5e9' }}>🦀 OpenClawBox</h1>
          <span className="text-sm" style={{ color: '#6b7280' }}>ID: {user.id}</span>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-6">
        <ApiKeyDisplay apiKey={user.api_key || ''} />
        <UsageStats userId={user.id} />
        <Dashboard userId={user.id} />
      </main>
    </div>
  )
}

export default App