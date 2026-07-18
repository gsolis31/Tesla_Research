import { Line } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import type { TeslaData } from '../types'
import ProductionDelivery from './ProductionDelivery'

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
)

interface Props {
  data: TeslaData
}

/** Shared options with taller plot area (axes no longer crushed). */
function makeChartOptions(yTitle?: string) {
  return {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#e0e0e0', boxWidth: 12, padding: 12 },
      },
      tooltip: {
        callbacks: {
          // Show full note if present on raw data is handled via label only
        },
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        ticks: { color: '#e0e0e0', padding: 8 },
        grid: { color: '#333' },
        title: yTitle
          ? { display: true, text: yTitle, color: '#9ca3af', font: { size: 11 } }
          : undefined,
      },
      x: {
        ticks: {
          color: '#e0e0e0',
          maxRotation: 45,
          minRotation: 0,
          autoSkip: true,
          maxTicksLimit: 8,
        },
        grid: { color: '#333' },
      },
    },
  }
}

function MetricsCharts({ data }: Props) {
  const chartOptions = makeChartOptions()
  const fleetOptions = makeChartOptions('Vehicles')

  // Cybercab Chart Data
  const cybercabChartData = {
    labels: data.metrics.cybercab.data.map((d) => d.date),
    datasets: [
      {
        label: 'Cybercab units (production / staged)',
        data: data.metrics.cybercab.data.map((d) => d.count),
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3b82f6',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 7,
      },
    ],
  }

  // Active robotaxi fleet only (never DMV registrations)
  const robotaxiFleetChartData = {
    labels: data.metrics.robotaxiFleet.data.map((d) => d.date),
    datasets: [
      {
        label: 'Active in-service fleet',
        data: data.metrics.robotaxiFleet.data.map((d) => d.count),
        backgroundColor: 'rgba(34, 197, 94, 0.15)',
        borderColor: '#22c55e',
        borderWidth: 3,
        fill: true,
        tension: 0.35,
        pointRadius: 4,
        pointHoverRadius: 7,
      },
    ],
  }

  const registered = data.metrics.robotaxiRegistered
  const robotaxiRegisteredChartData = registered
    ? {
        labels: registered.data.map((d) => d.date),
        datasets: [
          {
            label: 'TX DMV robotaxi registrations',
            data: registered.data.map((d) => d.count),
            backgroundColor: 'rgba(251, 146, 60, 0.15)',
            borderColor: '#fb923c',
            borderWidth: 3,
            fill: true,
            tension: 0.35,
            pointRadius: 5,
            pointHoverRadius: 7,
          },
        ],
      }
    : null

  // Job Postings Chart Data
  const jobPostingsChartData = {
    labels: data.metrics.jobPostings.data.map((d) => d.date),
    datasets: [
      {
        label: 'Optimus job postings',
        data: data.metrics.jobPostings.data.map((d) => d.count),
        backgroundColor: 'rgba(168, 85, 247, 0.2)',
        borderColor: '#a855f7',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 4,
        pointHoverRadius: 7,
      },
    ],
  }

  const latestActive =
    data.metrics.robotaxiFleet.data[data.metrics.robotaxiFleet.data.length - 1]
  const latestReg =
    registered && registered.data.length
      ? registered.data[registered.data.length - 1]
      : null

  return (
    <div className="space-y-8">
      {/* Metrics Charts — taller panels so axes are readable */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Cybercab Chart */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold mb-1">Cybercab Production</h3>
          <p className="text-xs text-gray-500 mb-3">Production / staged unit counts over time</p>
          <div className="h-80 md:h-96">
            <Line data={cybercabChartData} options={chartOptions} />
          </div>
        </div>

        {/* Job Postings Chart */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold mb-1">Optimus Job Postings</h3>
          <p className="text-xs text-gray-500 mb-3">Open AI / robotics roles (when counted)</p>
          <div className="h-80 md:h-96">
            <Line data={jobPostingsChartData} options={chartOptions} />
          </div>
        </div>

        {/* Active Robotaxi Fleet — full width on large screens when paired with registered */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold mb-1">Active Robotaxi Fleet</h3>
          <p className="text-xs text-gray-400 mb-1">
            Vehicles reported <strong className="text-gray-300">in service</strong> (rides / online
            fleet) — not DMV registrations
          </p>
          {latestActive && (
            <p className="text-sm text-green-400/90 mb-3">
              Latest: <strong>{latestActive.count}</strong> active
              <span className="text-gray-500"> as of {latestActive.date}</span>
            </p>
          )}
          <div className="h-80 md:h-[28rem]">
            <Line data={robotaxiFleetChartData} options={fleetOptions} />
          </div>
        </div>

        {/* TX Registrations — separate chart so 175 never distorts active series */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold mb-1">Texas Robotaxi Registrations</h3>
          <p className="text-xs text-gray-400 mb-1">
            Texas DMV automated-vehicle <strong className="text-gray-300">registry</strong> (pipeline
            / permitted cars) — not the same as active rides
          </p>
          {latestReg ? (
            <p className="text-sm text-orange-400/90 mb-3">
              Latest: <strong>{latestReg.count}</strong> registered
              <span className="text-gray-500"> as of {latestReg.date}</span>
              {latestActive && (
                <span className="text-gray-500">
                  {' '}
                  · active fleet still ~{latestActive.count}
                </span>
              )}
            </p>
          ) : (
            <p className="text-sm text-gray-500 mb-3">No registration series yet</p>
          )}
          <div className="h-80 md:h-[28rem]">
            {robotaxiRegisteredChartData ? (
              <Line data={robotaxiRegisteredChartData} options={fleetOptions} />
            ) : (
              <div className="h-full flex items-center justify-center text-gray-600 text-sm">
                No registration data
              </div>
            )}
          </div>
        </div>
      </div>

      {/* City Table */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-lg font-bold mb-1">Robotaxi Service by City</h3>
        <p className="text-xs text-gray-500 mb-4">
          Active fleet by city (in-service estimates). Updated{' '}
          {data.metrics.robotaxiCities.lastUpdated}.
        </p>
        <CityTable
          cities={data.metrics.robotaxiCities.cities}
          summary={data.metrics.robotaxiCities.summary}
        />
      </div>

      {/* Production & Delivery Section */}
      <div className="border-t border-gray-700 pt-8">
        <ProductionDelivery data={data.categories.productionDelivery} />
      </div>
    </div>
  )
}

// City Table Component
function CityTable({ cities, summary }: { cities: any[]; summary: any }) {
  const getServiceBadge = (serviceType: string) => {
    const badges: Record<string, string> = {
      unsupervised: 'bg-green-600 text-white',
      mixed: 'bg-yellow-600 text-black',
      'safety-monitor-only': 'bg-gray-600 text-white',
    }
    const labels: Record<string, string> = {
      unsupervised: 'UNSUPERVISED',
      mixed: 'MIXED',
      'safety-monitor-only': 'MONITOR ONLY',
    }
    return (
      <span className={`px-2 py-1 rounded text-xs font-semibold ${badges[serviceType] || 'bg-gray-700'}`}>
        {labels[serviceType] || serviceType}
      </span>
    )
  }

  const getStatusBadge = (status: string) => {
    if (status === 'active')
      return <span className="text-green-400 font-semibold">Active</span>
    if (status === 'mapped')
      return <span className="text-gray-500 font-semibold">Mapped only</span>
    return status
  }

  return (
    <div>
      <div className="overflow-x-auto">
        <table className="w-full border-collapse text-sm">
          <thead>
            <tr className="border-b-2 border-gray-700">
              <th className="text-left p-3 text-gray-300">City</th>
              <th className="text-left p-3 text-gray-300">Status</th>
              <th className="text-left p-3 text-gray-300">Service Type</th>
              <th className="text-center p-3 text-gray-300">Active Fleet</th>
              <th className="text-left p-3 text-gray-300">Vehicle Type</th>
            </tr>
          </thead>
          <tbody>
            {cities.map((city, index) => (
              <tr
                key={city.name}
                className={index % 2 === 0 ? 'bg-gray-800/50' : 'bg-gray-900/50'}
              >
                <td className="p-3 font-semibold text-white">{city.name}</td>
                <td className="p-3">{getStatusBadge(city.status)}</td>
                <td className="p-3">{getServiceBadge(city.serviceType)}</td>
                <td className="p-3 text-center">
                  <span
                    className={`font-semibold ${
                      (city.activeVehicles ?? 0) > 0 ? 'text-green-400' : 'text-gray-600'
                    }`}
                  >
                    {(city.activeVehicles ?? 0) > 0 ? city.activeVehicles : '—'}
                  </span>
                  {city.breakdown && (
                    <div className="text-xs text-gray-500 mt-1">
                      {city.breakdown.unsupervised} unsupervised
                      {city.breakdown.cybercabTesting
                        ? ` · ${city.breakdown.cybercabTesting} Cybercab test`
                        : ''}
                    </div>
                  )}
                </td>
                <td className="p-3 text-gray-400">{city.vehicleType}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Summary */}
      <div className="mt-4 p-4 bg-green-500/10 border-l-4 border-green-500 text-sm">
        <strong className="text-gray-200">Summary:</strong>{' '}
        <span className="text-gray-400">
          {summary.activeCities} active cities (with vehicles), {summary.unsupervisedCapable}{' '}
          unsupervised/mixed capable, {summary.totalActiveVehicles} total active vehicles
          {summary.mappedOnly > 0 ? ` · ${summary.mappedOnly} mapped-only` : ''}
        </span>
        <p className="text-xs text-gray-500 mt-2">
          Active = status “active” and activeVehicles &gt; 0. Does not include Texas DMV
          registrations ({summary.totalActiveVehicles} ≠ registry counts).
        </p>
      </div>
    </div>
  )
}

export default MetricsCharts
