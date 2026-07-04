import { useState } from 'react'
import type { TeslaData } from './types'
import WeeklySummary from './components/WeeklySummary'
import MetricsCharts from './components/MetricsCharts'
import Categories from './components/Categories'
import TradingViewWidget from './components/TradingViewWidget'
import './App.css'

// Import data directly - Vite will bundle it
import teslaData from '../tesla-tracking-data.json'

function App() {
  const data = teslaData as TeslaData
  const [activeTab, setActiveTab] = useState('summary')

  return (
    <div className="min-h-screen bg-gray-900 text-gray-100">
      {/* Header */}
      <header className="bg-gray-800 border-b border-gray-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-3xl font-bold text-white mb-2">
            Tesla Investor Research Dashboard
          </h1>
          <p className="text-gray-400 text-sm">
            Last Updated: {data.lastUpdated}
          </p>
        </div>
      </header>

      {/* Stock Widget */}
      <div className="max-w-7xl mx-auto px-4 py-4">
        <TradingViewWidget />
      </div>

      {/* Navigation Tabs */}
      <div className="max-w-7xl mx-auto px-4 py-2">
        <div className="flex gap-2 border-b border-gray-700 overflow-x-auto">
          <button
            onClick={() => setActiveTab('summary')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'summary'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Weekly Summary
          </button>
          <button
            onClick={() => setActiveTab('charts')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'charts'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Charts & Metrics
          </button>
          <button
            onClick={() => setActiveTab('categories')}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeTab === 'categories'
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            Categories
          </button>
        </div>
      </div>

      {/* Content */}
      <main className="max-w-7xl mx-auto px-4 py-6">
        {activeTab === 'summary' && <WeeklySummary data={data} />}
        {activeTab === 'charts' && <MetricsCharts data={data} />}
        {activeTab === 'categories' && <Categories data={data} />}
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto px-4 py-8 mt-12 border-t border-gray-700">
        <p className="text-gray-500 text-sm text-center">
          Tesla Investor Research Dashboard • Built with React + TypeScript •{' '}
          <a
            href="https://github.com/gsolis31/Tesla_Research"
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-400 hover:text-blue-300"
          >
            View on GitHub
          </a>
        </p>
      </footer>
    </div>
  )
}

export default App
