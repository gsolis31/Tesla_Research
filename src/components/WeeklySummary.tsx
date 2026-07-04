import type { TeslaData, KeyChange } from '../types'

interface Props {
  data: TeslaData
}

function WeeklySummary({ data }: Props) {
  const latestWeek = data.weeklySummaries[0]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'positive':
        return 'border-green-500 bg-green-500/10'
      case 'negative':
        return 'border-red-500 bg-red-500/10'
      default:
        return 'border-yellow-500 bg-yellow-500/10'
    }
  }

  const getStatusEmoji = (status: string) => {
    switch (status) {
      case 'positive':
        return '🟢'
      case 'negative':
        return '🔴'
      default:
        return '🟡'
    }
  }

  const hasRealityGap = (change: KeyChange) => {
    return (
      change.sentiment?.headline &&
      change.sentiment?.reality &&
      change.sentiment.headline !== change.sentiment.reality
    )
  }

  return (
    <div>
      <h2 className="text-2xl font-bold mb-6">Week of {latestWeek.weekOf}</h2>

      {/* Key Changes */}
      <div className="space-y-6">
        {latestWeek.keyChanges.map((change, index) => (
          <div
            key={index}
            className={`border-l-4 rounded-lg p-6 ${getStatusColor(
              change.status
            )} transition-all hover:shadow-lg`}
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center gap-2">
                <span className="text-xs font-semibold px-2 py-1 bg-gray-700 rounded">
                  {change.category}
                </span>
                {hasRealityGap(change) && (
                  <span className="text-xs font-semibold px-2 py-1 bg-yellow-600 rounded flex items-center gap-1">
                    ⚠️ Reality Check
                  </span>
                )}
              </div>
              <span className="text-2xl">{getStatusEmoji(change.status)}</span>
            </div>

            <h3 className="text-xl font-bold mb-3">{change.title}</h3>
            <p className="text-gray-300 mb-4 leading-relaxed">
              {change.description}
            </p>

            {/* Sentiment Analysis */}
            {change.sentiment && (
              <div className="mb-4 p-4 bg-gray-800/50 rounded-lg">
                <h4 className="font-semibold text-sm mb-2 text-gray-400">
                  Sentiment Analysis
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                  <div>
                    <span className="text-gray-500">Headline:</span>
                    <span className="ml-2 capitalize">{change.sentiment.headline}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Reality:</span>
                    <span className="ml-2 capitalize">{change.sentiment.reality}</span>
                  </div>
                  <div className="md:col-span-2">
                    <span className="text-gray-500">Confidence:</span>
                    <span className="ml-2 capitalize">{change.sentiment.confidence}</span>
                  </div>
                  <div className="md:col-span-2">
                    <p className="text-gray-300 italic">{change.sentiment.rationale}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Evidence */}
            {change.evidence && (
              <div className="mb-4 space-y-3">
                {change.evidence.positive_signals.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-green-400">
                      Positive Signals
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-300">
                      {change.evidence.positive_signals.map((signal, i) => (
                        <li key={i}>{signal}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {change.evidence.negative_signals.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-sm mb-2 text-red-400">
                      Negative Signals
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-sm text-gray-300">
                      {change.evidence.negative_signals.map((signal, i) => (
                        <li key={i}>{signal}</li>
                      ))}
                    </ul>
                  </div>
                )}

                <div className="p-3 bg-gray-800/50 rounded text-sm">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-2">
                    <div>
                      <span className="text-gray-500">Actual:</span>
                      <span className="ml-2">{change.evidence.key_metrics.actual}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Target:</span>
                      <span className="ml-2">{change.evidence.key_metrics.target}</span>
                    </div>
                    <div>
                      <span className="text-gray-500">Trajectory:</span>
                      <span className="ml-2">{change.evidence.key_metrics.trajectory}</span>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Source */}
            <a
              href={change.source}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-400 hover:text-blue-300 text-sm inline-flex items-center gap-1"
            >
              <span>View Source</span>
              <svg
                className="w-4 h-4"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"
                />
              </svg>
            </a>
          </div>
        ))}
      </div>

      {/* Trends */}
      {latestWeek.trends && latestWeek.trends.length > 0 && (
        <div className="mt-8 p-6 bg-gray-800 rounded-lg border border-gray-700">
          <h3 className="text-lg font-bold mb-4">Key Trends</h3>
          <ul className="space-y-2">
            {latestWeek.trends.map((trend, index) => (
              <li key={index} className="flex items-start gap-2">
                <span className="text-blue-400 mt-1">•</span>
                <span className="text-gray-300">{trend}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

export default WeeklySummary
