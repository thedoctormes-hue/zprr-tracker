import { useEffect } from 'react'

interface TelegramLoginProps {
  onAuth: (user: { id: number; api_key?: string }) => void
}

export default function TelegramLogin({ onAuth }: TelegramLoginProps) {
  useEffect(() => {
    // Telegram WebApp initialization
    if (typeof window !== 'undefined' && (window as any).Telegram?.WebApp) {
      (window as any).Telegram.WebApp.ready()
      ;(window as any).Telegram.WebApp.expand()
      
      const user = (window as any).Telegram.WebApp.initDataUnsafe?.user
      if (user) {
        onAuth({ id: user.id })
      }
    }
  }, [onAuth])

  return (
    <div className="flex items-center justify-center min-h-screen" style={{ background: 'linear-gradient(135deg, #0ea5e9 0%, #4f46e5 100%)' }}>
      <div className="card max-w-md w-full mx-4 text-center">
        <div className="text-6xl mb-4">🦀</div>
        <h1 className="text-2xl font-bold mb-2">OpenClawBox</h1>
        <p className="text-gray-600 mb-6">
          LLM агрегатор для 60k+ пользователей
        </p>
        <button 
          className="btn btn-primary w-full"
          onClick={() => {
            // Mock auth for demo
            onAuth({ id: 173681771, api_key: 'ocb_sk_demo123456' })
          }}
        >
          Войти через Telegram
        </button>
        <p className="text-xs text-gray-500 mt-4">
          Нажмите для демо-режима
        </p>
      </div>
    </div>
  )
}