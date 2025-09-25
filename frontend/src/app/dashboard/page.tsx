'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { PredictionForm } from '@/components/dashboard/PredictionForm'
import { PredictionHistory } from '@/components/dashboard/PredictionHistory'
import { Analytics } from '@/components/dashboard/Analytics'

type TabType = 'predict' | 'history' | 'analytics'

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabType>('predict')

  const tabs = [
    { id: 'predict', label: 'Make Prediction', icon: '🔍' },
    { id: 'history', label: 'Prediction History', icon: '📋' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">SpamGuard Dashboard</h1>
              <p className="text-gray-600">AI-powered spam and fraud detection</p>
            </div>
            <div className="flex items-center space-x-4">
              <Button variant="outline" size="sm">
                API Keys
              </Button>
              <Button variant="outline" size="sm">
                Settings
              </Button>
              <Button variant="outline" size="sm">
                Logout
              </Button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <nav className="flex space-x-8" aria-label="Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as TabType)}
                className={`flex items-center px-1 py-2 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        {/* Tab Content */}
        <div className="bg-white rounded-lg shadow-sm p-6">
          {activeTab === 'predict' && <PredictionForm />}
          {activeTab === 'history' && <PredictionHistory />}
          {activeTab === 'analytics' && <Analytics />}
        </div>
      </div>
    </div>
  )
}