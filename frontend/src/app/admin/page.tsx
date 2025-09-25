'use client'

import { useState } from 'react'
import Link from 'next/link'

type AdminTabType = 'users' | 'models' | 'stats' | 'jobs'

export default function AdminPanel() {
  const [activeTab, setActiveTab] = useState<AdminTabType>('stats')

  const tabs = [
    { id: 'stats', label: 'System Stats', icon: '📊' },
    { id: 'users', label: 'User Management', icon: '👥' },
    { id: 'models', label: 'Model Management', icon: '🤖' },
    { id: 'jobs', label: 'Background Jobs', icon: '⚙️' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Admin Panel</h1>
              <p className="text-gray-600">System administration and monitoring</p>
            </div>
            <div className="flex items-center space-x-4">
              <Link
                href="/dashboard"
                className="text-blue-600 hover:text-blue-800 font-medium"
              >
                ← Back to Dashboard
              </Link>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tab Navigation */}
        <div className="mb-8">
          <nav className="flex space-x-8" aria-label="Admin Tabs">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as AdminTabType)}
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
          {activeTab === 'stats' && <SystemStats />}
          {activeTab === 'users' && <UserManagement />}
          {activeTab === 'models' && <ModelManagement />}
          {activeTab === 'jobs' && <BackgroundJobs />}
        </div>
      </div>
    </div>
  )
}

function SystemStats() {
  // Mock data - in real app, fetch from API
  const stats = {
    totalUsers: 1250,
    totalPredictions: 45670,
    activeModels: 3,
    systemHealth: 'Healthy',
    uptime: '99.9%',
    recentErrors: 2
  }

  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900">System Statistics</h2>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="flex items-center">
            <div className="text-2xl mr-3">👥</div>
            <div>
              <p className="text-sm font-medium text-blue-600">Total Users</p>
              <p className="text-2xl font-bold text-blue-900">{stats.totalUsers.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-green-50 p-4 rounded-lg">
          <div className="flex items-center">
            <div className="text-2xl mr-3">🔍</div>
            <div>
              <p className="text-sm font-medium text-green-600">Total Predictions</p>
              <p className="text-2xl font-bold text-green-900">{stats.totalPredictions.toLocaleString()}</p>
            </div>
          </div>
        </div>

        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="flex items-center">
            <div className="text-2xl mr-3">🤖</div>
            <div>
              <p className="text-sm font-medium text-purple-600">Active Models</p>
              <p className="text-2xl font-bold text-purple-900">{stats.activeModels}</p>
            </div>
          </div>
        </div>
      </div>

      <div className="border-t pt-6">
        <h3 className="text-md font-semibold text-gray-900 mb-4">System Health</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="flex justify-between">
            <span className="text-gray-600">Status:</span>
            <span className="font-medium text-green-600">{stats.systemHealth}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Uptime:</span>
            <span className="font-medium">{stats.uptime}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Recent Errors:</span>
            <span className="font-medium text-red-600">{stats.recentErrors}</span>
          </div>
        </div>
      </div>
    </div>
  )
}

function UserManagement() {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900">User Management</h2>
      <p className="text-gray-600">Manage user accounts, roles, and permissions.</p>

      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">User Management Interface</h3>
        <p className="text-gray-500">List, edit, and manage user accounts and permissions.</p>
      </div>
    </div>
  )
}

function ModelManagement() {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900">Model Management</h2>
      <p className="text-gray-600">Monitor and manage ML models, versions, and retraining.</p>

      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Model Management Interface</h3>
        <p className="text-gray-500">View model performance, trigger retraining, and manage versions.</p>
      </div>
    </div>
  )
}

function BackgroundJobs() {
  return (
    <div className="space-y-6">
      <h2 className="text-lg font-semibold text-gray-900">Background Jobs</h2>
      <p className="text-gray-600">Monitor and manage background tasks and job queues.</p>

      <div className="text-center py-12">
        <div className="text-gray-400 mb-4">
          <svg className="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">Job Management Interface</h3>
        <p className="text-gray-500">View running jobs, check status, and manage background tasks.</p>
      </div>
    </div>
  )
}