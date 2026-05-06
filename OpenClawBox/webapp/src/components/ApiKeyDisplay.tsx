import { useState } from 'react'

interface ApiKeyDisplayProps {
  apiKey: string
}

export default function ApiKeyDisplay({ apiKey }: ApiKeyDisplayProps) {
  const [copied, setCopied] = useState(false)

  const copyToClipboard = () => {
    navigator.clipboard.writeText(apiKey)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="card">
      <h2 className="text-lg font-semibold mb-3 flex items-center gap-2">
        🔑 Ваш API ключ
      </h2>
      <div className="flex items-center gap-2">
        <code className="flex-1 bg-gray-100 px-3 py-2 rounded font-mono text-sm break-all">
          {apiKey}
        </code>
        <button 
          className="btn btn-primary"
          onClick={copyToClipboard}
        >
          {copied ? '✓' : '📋'}
        </button>
      </div>
      <p className="text-sm text-gray-500 mt-2">
        Используйте этот ключ для доступа к API
      </p>
    </div>
  )
}