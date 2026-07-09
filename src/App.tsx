import { useState } from 'react'
import { validateTeslaData, validateDataInvariants } from './schema'
import WeeklySummary from './components/WeeklySummary'
import MetricsCharts from './components/MetricsCharts'
import Categories from './components/Categories'
import StockPriceTile from './components/StockPriceTile'
import './App.css'

// Import data directly - Vite will bundle it
import teslaDataRaw from '../tesla-tracking-data.json'

// Validate data at build time with detailed error reporting
const validationResult = validateTeslaData(teslaDataRaw)

if (!validationResult.success) {
  console.error('❌ Data validation failed:')
  validationResult.errors.forEach(err => console.error(`  - ${err}`))
  // Log errors but don't crash the app in production
  console.warn('⚠️ Continuing with potentially invalid data')
}

const data = validationResult.success ? validationResult.data : teslaDataRaw as any

// Check data invariants (non-blocking)
if (validationResult.success) {
  const invariantErrors = validateDataInvariants(data)
  if (invariantErrors.length > 0) {
    console.warn('⚠️ Data invariant validation warnings:')
    invariantErrors.forEach(err => console.warn(`  - ${err}`))
  } else {
    console.log('✅ Data validation passed')
  }
}

function App() {
  const [activeTab, setActiveTab] = useState('summary')

  return (
    <div className="min-h-screen text-gray-100" style={{ background: '#0a0a0a', fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif' }}>
      {/* Header */}
      <header className="mb-10 p-8 text-center rounded-xl border border-gray-800 mx-1" style={{ background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)' }}>
        <div className="px-1">
          <div className="flex items-center justify-center gap-5 mb-3">
            <img
              src="https://www.tesla.com/themes/custom/tesla_frontend/assets/favicons/favicon-196x196.png"
              alt="Tesla Logo"
              className="w-[60px] h-[60px] object-contain"
              onError={(e) => {
                // Try clearbit as fallback
                e.currentTarget.src = 'https://logo.clearbit.com/tesla.com';
                e.currentTarget.onerror = () => {
                  e.currentTarget.style.display = 'none';
                };
              }}
            />
            <h1 className="text-5xl font-bold text-white m-0">
              Tesla Investor Tracking Dashboard
            </h1>
          </div>
          <p className="text-gray-500 text-sm">
            Last Updated: {data.lastUpdated}
          </p>
        </div>
      </header>

      <div className="px-1">
        {/* Stock Price Tile */}
        <div className="mb-3 text-center">
          <StockPriceTile />
        </div>

        {/* Navigation Tabs */}
        <div className="mb-6">
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
        <main className="py-6">
          {activeTab === 'summary' && <WeeklySummary data={data} />}
          {activeTab === 'charts' && <MetricsCharts data={data} />}
          {activeTab === 'categories' && <Categories data={data} />}
        </main>

        {/* Footer */}
        <footer className="py-8 mt-12 border-t border-gray-700">
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
    </div>
  )
}

export default App
