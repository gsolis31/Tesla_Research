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

function MetricsCharts({ data }: Props) {
  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: true,
    plugins: {
      legend: {
        labels: { color: '#e0e0e0' },
      },
    },
    scales: {
      y: {
        ticks: { color: '#e0e0e0' },
        grid: { color: '#333' },
      },
      x: {
        ticks: { color: '#e0e0e0' },
        grid: { color: '#333' },
      },
    },
  }

  // Cybercab Chart Data
  const cybercabChartData = {
    labels: data.metrics.cybercab.data.map((d) => d.date),
    datasets: [
      {
        label: 'Cybercab Production Count',
        data: data.metrics.cybercab.data.map((d) => d.count),
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: '#3b82f6',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 7,
      },
    ],
  }

  // Robotaxi Fleet Chart Data
  const robotaxiFleetChartData = {
    labels: data.metrics.robotaxiFleet.data.map((d) => d.date),
    datasets: [
      {
        label: 'Total Fleet Size',
        data: data.metrics.robotaxiFleet.data.map((d) => d.count),
        backgroundColor: 'rgba(34, 197, 94, 0.2)',
        borderColor: '#22c55e',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 7,
      },
    ],
  }

  // Job Postings Chart Data
  const jobPostingsChartData = {
    labels: data.metrics.jobPostings.data.map((d) => d.date),
    datasets: [
      {
        label: 'Optimus Job Postings',
        data: data.metrics.jobPostings.data.map((d) => d.count),
        backgroundColor: 'rgba(168, 85, 247, 0.2)',
        borderColor: '#a855f7',
        borderWidth: 3,
        fill: true,
        tension: 0.4,
        pointRadius: 5,
        pointHoverRadius: 7,
      },
    ],
  }

  return (
    <div className="space-y-8">
      {/* Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Cybercab Chart */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold mb-4">Cybercab Production Count</h3>
          <Line data={cybercabChartData} options={chartOptions} />
        </div>

        {/* Robotaxi Fleet Chart */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold mb-4">Total Robotaxi Fleet</h3>
          <Line data={robotaxiFleetChartData} options={chartOptions} />
        </div>

        {/* Job Postings Chart */}
        <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold mb-4">Optimus Job Postings</h3>
          <Line data={jobPostingsChartData} options={chartOptions} />
        </div>
      </div>

      {/* City Table */}
      <div className="bg-gray-800 p-6 rounded-lg border border-gray-700">
        <h3 className="text-lg font-bold mb-4">Robotaxi Service by City</h3>
        <CityTable cities={data.metrics.robotaxiCities.cities} summary={data.metrics.robotaxiCities.summary} />
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
      unsupervised: '🟢 UNSUPERVISED',
      mixed: '🟡 MIXED',
      'safety-monitor-only': '⚪ MONITOR ONLY',
    }
    return (
      <span className={`px-2 py-1 rounded text-xs font-semibold ${badges[serviceType]}`}>
        {labels[serviceType]}
      </span>
    )
  }

  const getStatusBadge = (status: string) => {
    if (status === 'active')
      return <span className="text-green-400 font-semibold">✓ Active</span>
    if (status === 'mapped')
      return <span className="text-gray-500 font-semibold">○ Mapped</span>
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
                      city.activeVehicles > 0 ? 'text-green-400' : 'text-gray-600'
                    }`}
                  >
                    {city.activeVehicles > 0 ? city.activeVehicles : '-'}
                  </span>
                  {city.breakdown && (
                    <div className="text-xs text-gray-500 mt-1">
                      {city.breakdown.unsupervised} unsupervised, {city.breakdown.safetyMonitor}{' '}
                      monitored
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
          {summary.activeCities} active cities, {summary.unsupervisedCapable} with unsupervised
          capability, {summary.totalActiveVehicles} total active vehicles
        </span>
      </div>
    </div>
  )
}

export default MetricsCharts
