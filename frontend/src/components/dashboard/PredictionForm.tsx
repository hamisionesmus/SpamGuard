'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { formatConfidence, getPredictionColor } from '@/lib/utils'

interface PredictionResult {
  prediction: string
  confidence: number
  explanation?: any
  model_version: string
}

export function PredictionForm() {
  const [text, setText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<PredictionResult | null>(null)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!text.trim()) return

    setIsLoading(true)
    setError('')
    setResult(null)

    try {
      const response = await fetch('/api/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      })

      if (!response.ok) {
        throw new Error('Prediction failed')
      }

      const data = await response.json()
      setResult(data)
    } catch (err) {
      setError('Failed to get prediction. Please try again.')
      console.error('Prediction error:', err)
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-2">
          Spam & Fraud Detection
        </h2>
        <p className="text-gray-600">
          Enter text to analyze for spam or fraudulent content using our AI models.
        </p>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="text" className="block text-sm font-medium text-gray-700 mb-2">
            Text to Analyze
          </label>
          <textarea
            id="text"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="Enter email content, message, or any text to analyze..."
            className="w-full h-32 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
            required
          />
        </div>

        <Button
          type="submit"
          disabled={isLoading || !text.trim()}
          className="w-full sm:w-auto"
        >
          {isLoading ? 'Analyzing...' : 'Analyze Text'}
        </Button>
      </form>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-md">
          <p className="text-red-800">{error}</p>
        </div>
      )}

      {result && (
        <div className="p-6 bg-white border border-gray-200 rounded-lg">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Analysis Result
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="mb-4">
                <span className="text-sm font-medium text-gray-500">Prediction</span>
                <div className={`mt-1 inline-flex px-3 py-1 rounded-full text-sm font-medium ${getPredictionColor(result.prediction)}`}>
                  {result.prediction.toUpperCase()}
                </div>
              </div>

              <div className="mb-4">
                <span className="text-sm font-medium text-gray-500">Confidence</span>
                <div className="mt-1 text-2xl font-bold text-gray-900">
                  {formatConfidence(result.confidence)}
                </div>
              </div>

              <div>
                <span className="text-sm font-medium text-gray-500">Model Version</span>
                <div className="mt-1 text-sm text-gray-900">
                  {result.model_version}
                </div>
              </div>
            </div>

            <div>
              <span className="text-sm font-medium text-gray-500">Explanation</span>
              {result.explanation?.keywords_found?.length > 0 ? (
                <div className="mt-2">
                  <p className="text-sm text-gray-600 mb-2">
                    {result.explanation.reason}
                  </p>
                  <div className="flex flex-wrap gap-1">
                    {result.explanation.keywords_found.map((keyword: string, index: number) => (
                      <span
                        key={index}
                        className="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-100 text-blue-800"
                      >
                        {keyword}
                      </span>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="mt-2 text-sm text-gray-500">
                  No specific keywords detected
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}