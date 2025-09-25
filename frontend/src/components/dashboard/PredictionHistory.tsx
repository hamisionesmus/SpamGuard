'use client'

import { useState, useEffect } from 'react'
import { formatDate, getPredictionColor } from '@/lib/utils'

interface PredictionRecord {
  id: string
  prediction: string
  confidence: number
  input_text: string
  created_at: string
}

export function PredictionHistory() {
  const [history, setHistory] = useState<PredictionRecord[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetchHistory()
  }, [])

  const fetchHistory = async () => {
    try {
      const response = await fetch('/api/predict/history')
      if (!response.ok) {
        throw new Error('Failed to fetch history')
      }
      const data = await response.json()
      setHistory(data.history || [])
    } catch (err) {
      setError('Failed to load prediction history')
      console.error('History fetch error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 bg-red-50 border border-red-200 rounded-md">
        <p className="text-red-800">{error}</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Prediction History
        </h2>
        <p className="text-gray-600">
          View your recent spam and fraud detection results.
        </p>
      </div>

      {history.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-gray-400 mb-4">
            <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
          </div>
          <h3 className="text-lg font-medium text-gray-900 mb-2">No predictions yet</h3>
          <p className="text-gray-500">Start by analyzing some text to see your history here.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {history.map((record) => (
            <div key={record.id} className="bg-white border border-gray-200 rounded-lg p-4">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <span className={`inline-flex px-2 py-1 rounded-full text-xs font-medium ${getPredictionColor(record.prediction)}`}>
                      {record.prediction.toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-500">
                      {record.confidence ? `${(record.confidence * 100).toFixed(1)}% confidence` : 'N/A'}
                    </span>
                    <span className="text-sm text-gray-500">
                      {formatDate(record.created_at)}
                    </span>
                  </div>

                  <div className="text-sm text-gray-900 mb-2">
                    <span className="font-medium">Input:</span> {record.input_text.length > 100
                      ? `${record.input_text.substring(0, 100)}...`
                      : record.input_text
                    }
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}