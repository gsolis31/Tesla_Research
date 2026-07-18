import { useState, useMemo } from 'react'
import { Line } from 'react-chartjs-2'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import type { ProductionDeliveryCategory, QuarterlyData } from '../types'

interface Props {
  data: ProductionDeliveryCategory
}

// Helper to extract number from production field (can be number, object, or null)
function getProductionNumber(production: number | { total: number } | null): number {
  if (production === null) return 0
  if (typeof production === 'number') return production
  return production.total
}

// Helper to extract number from delivery/deliveries field
function getDeliveryNumber(q: QuarterlyData): number {
  if (q.deliveries) return q.deliveries.total
  return q.delivery ?? 0
}

function ProductionDelivery({ data }: Props) {
  // Filter state
  const [yearFilter, setYearFilter] = useState<string>('all')
  const [selectedQuarters, setSelectedQuarters] = useState<Set<string>>(new Set(['Q1', 'Q2', 'Q3', 'Q4']))
  const [groupByYear, setGroupByYear] = useState<boolean>(false)

  // Chart visibility state
  const [showProduction, setShowProduction] = useState<boolean>(true)
  const [showDeliveries, setShowDeliveries] = useState<boolean>(true)
  const [showLabels, setShowLabels] = useState<boolean>(false)

  // Full quarterly table is long — collapsed by default
  const [quarterlyTableOpen, setQuarterlyTableOpen] = useState<boolean>(false)

  // Get unique years from data
  const years = useMemo(() => {
    const yearSet = new Set(data.quarterlyData.map((q) => q.quarter.split('-')[1]))
    return Array.from(yearSet).sort().reverse()
  }, [data.quarterlyData])

  // Filter data based on selections
  const filteredData = useMemo(() => {
    let filtered = data.quarterlyData

    // Year filter
    if (yearFilter !== 'all') {
      filtered = filtered.filter((q) => q.quarter.includes(`-${yearFilter}`))
    }

    // Quarter filter (only include selected quarters)
    filtered = filtered.filter((q) => {
      const quarter = q.quarter.split('-')[0] // Get "Q1", "Q2", etc.
      return selectedQuarters.has(quarter)
    })

    return filtered
  }, [data.quarterlyData, yearFilter, selectedQuarters])

  // Helper function to sort quarters chronologically
  const sortQuartersChronologically = (data: QuarterlyData[]) => {
    return data.slice().sort((a, b) => {
      // Extract year and quarter number for proper chronological sorting
      // Format: "Q1-15" or "H1-2026" or "2026"
      const getYearQuarter = (str: string) => {
        if (str.startsWith('Q')) {
          // Q1-15 format
          const [q, y] = str.split('-')
          const quarter = parseInt(q.substring(1))
          const year = parseInt('20' + y)
          return year * 10 + quarter
        } else if (str.startsWith('H')) {
          // H1-2026 format
          const [h, y] = str.split('-')
          const half = parseInt(h.substring(1))
          return parseInt(y) * 10 + half
        } else {
          // Year only (2026)
          return parseInt(str) * 10
        }
      }
      return getYearQuarter(a.quarter) - getYearQuarter(b.quarter)
    })
  }

  // Transform data based on grouping
  const displayData = useMemo(() => {
    if (!groupByYear) {
      // Show individual quarters
      return sortQuartersChronologically(filteredData)
    }

    // Group by year - combine selected quarters per year
    const grouped: Record<string, QuarterlyData[]> = {}
    filteredData.forEach((q) => {
      const year = q.quarter.split('-')[1]
      if (!grouped[year]) grouped[year] = []
      grouped[year].push(q)
    })

    const result: QuarterlyData[] = []

    Object.entries(grouped).forEach(([year, quarters]) => {
      if (quarters.length > 0) {
        const totalProd = quarters.reduce((sum, q) => sum + getProductionNumber(q.production), 0)
        const totalDel = quarters.reduce((sum, q) => sum + getDeliveryNumber(q), 0)

        // Create label showing which quarters are included
        const quarterLabels = Array.from(selectedQuarters).sort().join('+')
        const label = selectedQuarters.size === 4 ? `20${year}` : `${quarterLabels}-${year}`

        result.push({
          quarter: label,
          production: totalProd,
          delivery: totalDel,
        })
      }
    })

    // Sort chronologically (oldest first)
    return sortQuartersChronologically(result)
  }, [filteredData, groupByYear, selectedQuarters])

  // Chart data (use displayData which respects filters)
  const chartData = useMemo(() => {
    const datasets = []

    if (showProduction) {
      datasets.push({
        label: 'Production',
        data: displayData.map((q) => getProductionNumber(q.production)),
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3b82f6',
        borderWidth: 2,
        tension: 0.4,
      })
    }

    if (showDeliveries) {
      datasets.push({
        label: 'Deliveries',
        data: displayData.map((q) => getDeliveryNumber(q)),
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        borderColor: '#22c55e',
        borderWidth: 2,
        tension: 0.4,
      })
    }

    return {
      labels: displayData.map((q) => q.quarter),
      datasets,
    }
  }, [displayData, showProduction, showDeliveries])

  const chartOptions = useMemo(() => ({
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        labels: { color: '#e0e0e0' },
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            return `${context.dataset.label}: ${context.parsed.y.toLocaleString()}`
          },
        },
      },
      datalabels: {
        display: showLabels,
        color: '#e0e0e0',
        anchor: 'end' as const,
        align: 'top' as const,
        offset: 4,
        formatter: (value: any) => {
          return value ? value.toLocaleString() : ''
        },
        font: {
          size: 10,
          weight: 'bold' as const,
        },
      },
    },
    scales: {
      y: {
        ticks: {
          color: '#e0e0e0',
          callback: function (value: any) {
            return value.toLocaleString()
          },
        },
        grid: { color: '#333' },
      },
      x: {
        ticks: { color: '#e0e0e0' },
        grid: { color: '#333' },
      },
    },
  }), [showLabels])

  return (
    <div>
      <h2 className="text-2xl font-bold mb-2">{data.title}</h2>
      <div className="text-gray-400 text-sm mb-4">Last Updated: {data.latestUpdate}</div>

      {/* Critical News */}
      <div className="bg-blue-500/10 border-l-4 border-blue-500 p-4 rounded mb-6">
        <strong className="text-blue-400">Latest:</strong>{' '}
        <span className="text-gray-300">{data.criticalNews}</span>
      </div>

      {/* Filters */}
      <div className="bg-gray-800 p-4 rounded-lg border border-gray-700 mb-6">
        <h3 className="text-sm font-semibold mb-3 text-gray-400">FILTERS & VIEW OPTIONS</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          {/* Year Filter */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-300">Year</label>
            <select
              value={yearFilter}
              onChange={(e) => setYearFilter(e.target.value)}
              className="w-full bg-gray-700 border border-gray-600 rounded px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="all">All Years</option>
              {years.map((year) => (
                <option key={year} value={year}>
                  20{year}
                </option>
              ))}
            </select>
          </div>

          {/* Quarter Selection (Checkboxes) */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-300">
              Quarters to Include
            </label>
            <div className="flex gap-3">
              {['Q1', 'Q2', 'Q3', 'Q4'].map((q) => (
                <label key={q} className="flex items-center gap-2 cursor-pointer">
                  <input
                    type="checkbox"
                    checked={selectedQuarters.has(q)}
                    onChange={(e) => {
                      const newSet = new Set(selectedQuarters)
                      if (e.target.checked) {
                        newSet.add(q)
                      } else {
                        newSet.delete(q)
                      }
                      setSelectedQuarters(newSet)
                    }}
                    className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-2 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-300">{q}</span>
                </label>
              ))}
            </div>
            <div className="mt-2">
              <button
                onClick={() => setSelectedQuarters(new Set(['Q1', 'Q2', 'Q3', 'Q4']))}
                className="text-xs text-blue-400 hover:text-blue-300 underline mr-3"
              >
                Select All
              </button>
              <button
                onClick={() => setSelectedQuarters(new Set())}
                className="text-xs text-gray-400 hover:text-gray-300 underline"
              >
                Clear
              </button>
            </div>
          </div>

          {/* Group By Year Toggle */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-300">Display Mode</label>
            <label className="flex items-center gap-3 cursor-pointer bg-gray-700 p-3 rounded border border-gray-600 hover:border-gray-500">
              <input
                type="checkbox"
                checked={groupByYear}
                onChange={(e) => setGroupByYear(e.target.checked)}
                className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-2 focus:ring-blue-500"
              />
              <div>
                <div className="text-sm font-medium text-gray-200">Group by Year</div>
                <div className="text-xs text-gray-400">
                  Combine selected quarters per year
                </div>
              </div>
            </label>
          </div>

          {/* Chart Visibility Toggles */}
          <div>
            <label className="block text-sm font-medium mb-2 text-gray-300">Chart Lines</label>
            <div className="space-y-2">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showProduction}
                  onChange={(e) => setShowProduction(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-blue-500 focus:ring-2 focus:ring-blue-500"
                />
                <span className="text-sm text-gray-300">Production</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showDeliveries}
                  onChange={(e) => setShowDeliveries(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-green-500 focus:ring-2 focus:ring-green-500"
                />
                <span className="text-sm text-gray-300">Deliveries</span>
              </label>
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={showLabels}
                  onChange={(e) => setShowLabels(e.target.checked)}
                  className="w-4 h-4 rounded border-gray-600 bg-gray-700 text-purple-500 focus:ring-2 focus:ring-purple-500"
                />
                <span className="text-sm text-gray-300">Show Numbers</span>
              </label>
            </div>
          </div>
        </div>

        {/* Active Filters Display */}
        {(yearFilter !== 'all' || selectedQuarters.size < 4 || groupByYear) && (
          <div className="mt-4 flex flex-wrap gap-2 items-center">
            <span className="text-xs text-gray-400">Active:</span>
            {yearFilter !== 'all' && (
              <span className="text-xs bg-blue-600 text-white px-2 py-1 rounded">
                Year: 20{yearFilter}
              </span>
            )}
            {selectedQuarters.size < 4 && selectedQuarters.size > 0 && (
              <span className="text-xs bg-green-600 text-white px-2 py-1 rounded">
                Quarters: {Array.from(selectedQuarters).sort().join(', ')}
              </span>
            )}
            {groupByYear && (
              <span className="text-xs bg-purple-600 text-white px-2 py-1 rounded">
                Grouped by Year
              </span>
            )}
            <button
              onClick={() => {
                setYearFilter('all')
                setSelectedQuarters(new Set(['Q1', 'Q2', 'Q3', 'Q4']))
                setGroupByYear(false)
              }}
              className="text-xs text-blue-400 hover:text-blue-300 underline ml-2"
            >
              Reset All
            </button>
          </div>
        )}
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Total Production (All Time)</div>
          <div className="text-2xl font-bold text-blue-400">
            {parseInt(data.totalProduction).toLocaleString()}
          </div>
        </div>
        <div className="bg-gray-800 p-4 rounded-lg border border-gray-700">
          <div className="text-gray-400 text-sm mb-1">Total Deliveries (All Time)</div>
          <div className="text-2xl font-bold text-green-400">
            {parseInt(data.totalDeliveries).toLocaleString()}
          </div>
        </div>
      </div>

      {/* Chart */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 mb-6">
        <h3 className="text-lg font-bold mb-4">Quarterly Production & Deliveries</h3>
        <div className="h-80 md:h-96">
          <Line
            data={chartData}
            options={{ ...chartOptions, maintainAspectRatio: false }}
            plugins={[ChartDataLabels]}
          />
        </div>
      </div>

      {/* Annual Summary — high-level view first */}
      {data.annualSummary && data.annualSummary.length > 0 && (
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 mb-6">
          <h3 className="text-lg font-bold mb-4">Annual Summary</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b-2 border-gray-700">
                  <th className="text-left p-3 text-gray-300">Year</th>
                  <th className="text-right p-3 text-gray-300">Deliveries</th>
                  <th className="text-right p-3 text-gray-300">YoY Growth</th>
                </tr>
              </thead>
              <tbody>
                {data.annualSummary
                  .slice()
                  .reverse()
                  .map((year, index) => (
                    <tr
                      key={year.year}
                      className={index % 2 === 0 ? 'bg-gray-900/50' : 'bg-gray-800/50'}
                    >
                      <td className="p-3 font-semibold">{year.year}</td>
                      <td className="p-3 text-right text-green-400">
                        {year.deliveries.toLocaleString()}
                      </td>
                      <td
                        className={`p-3 text-right font-semibold ${
                          year.yoyGrowth != null && year.yoyGrowth >= 0
                            ? 'text-green-400'
                            : year.yoyGrowth != null
                              ? 'text-red-400'
                              : 'text-gray-500'
                        }`}
                      >
                        {year.yoyGrowth != null ? (
                          <>
                            {year.yoyGrowth >= 0 ? '+' : ''}
                            {year.yoyGrowth.toFixed(2)}%
                          </>
                        ) : (
                          'N/A'
                        )}
                      </td>
                    </tr>
                  ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Quarterly Data Table — collapsed by default (long history) */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700 mb-6">
        <button
          type="button"
          onClick={() => setQuarterlyTableOpen((open) => !open)}
          className="w-full flex items-center justify-between gap-4 text-left group"
          aria-expanded={quarterlyTableOpen}
        >
          <div>
            <h3 className="text-lg font-bold group-hover:text-blue-400 transition-colors">
              Quarterly Data
            </h3>
            <p className="text-xs text-gray-500 mt-1">
              {displayData.length} {groupByYear ? 'years' : 'quarters'} shown
              {' · '}
              {data.quarterlyData.length} total in dataset
              {!quarterlyTableOpen && ' · click to expand'}
            </p>
          </div>
          <span
            className={`text-gray-400 text-xl shrink-0 transition-transform ${
              quarterlyTableOpen ? 'rotate-180' : ''
            }`}
            aria-hidden
          >
            ▾
          </span>
        </button>

        {quarterlyTableOpen && (
          <div className="mt-4">
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b-2 border-gray-700">
                    <th className="text-left p-3 text-gray-300">Quarter</th>
                    <th className="text-right p-3 text-gray-300">Production</th>
                    <th className="text-right p-3 text-gray-300">Deliveries</th>
                    <th className="text-right p-3 text-gray-300">Difference</th>
                  </tr>
                </thead>
                <tbody>
                  {displayData.map((q, index) => (
                    <tr
                      key={q.quarter}
                      className={index % 2 === 0 ? 'bg-gray-900/50' : 'bg-gray-800/50'}
                    >
                      <td className="p-3 font-semibold">{q.quarter}</td>
                      <td className="p-3 text-right text-blue-400">
                        {typeof q.production === 'object' && q.production !== null
                          ? q.production.total?.toLocaleString()
                          : q.production?.toLocaleString() || '-'}
                      </td>
                      <td className="p-3 text-right text-green-400">
                        {getDeliveryNumber(q).toLocaleString()}
                      </td>
                      <td className="p-3 text-right text-gray-400">
                        {q.production
                          ? (
                              getDeliveryNumber(q) - getProductionNumber(q.production)
                            ).toLocaleString()
                          : '-'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
            <div className="text-xs text-gray-500 mt-3">
              Showing {displayData.length} {groupByYear ? 'years' : 'quarters'} filtered by the
              controls above
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default ProductionDelivery
