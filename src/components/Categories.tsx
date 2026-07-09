import { useState } from 'react'
import type { TeslaData, Category } from '../types'

interface Props {
  data: TeslaData
}

function Categories({ data }: Props) {
  const [activeCategory, setActiveCategory] = useState('cybercab')

  const categories = [
    { id: 'cybercab', label: 'Cybercab', data: data.categories.cybercab },
    { id: 'fsd', label: 'FSD Approvals', data: data.categories.fsd },
    { id: 'optimus', label: 'Optimus Production', data: data.categories.optimus },
    { id: 'aiChip', label: 'AI Chip Production', data: data.categories.aiChip },
    { id: 'battery4680', label: '4680 Battery Cell Production', data: data.categories.battery4680 },
    { id: 'terafab', label: 'Terafab Manufacturing', data: data.categories.terafab },
    { id: 'jobPostings', label: 'Job Postings', data: data.categories.jobPostings },
  ]

  const activeData = categories.find((c) => c.id === activeCategory)?.data as Category

  return (
    <div>
      {/* Category Tabs */}
      <div className="flex gap-2 border-b border-gray-700 overflow-x-auto mb-6">
        {categories.map((cat) => (
          <button
            key={cat.id}
            onClick={() => setActiveCategory(cat.id)}
            className={`px-4 py-2 font-medium transition-colors whitespace-nowrap ${
              activeCategory === cat.id
                ? 'text-blue-400 border-b-2 border-blue-400'
                : 'text-gray-400 hover:text-gray-200'
            }`}
          >
            {cat.label}
          </button>
        ))}
      </div>

      {/* Category Content */}
      <div>
        <h2 className="text-2xl font-bold mb-2">{activeData?.title}</h2>
        <div className="text-gray-400 text-sm mb-4">
          Last Updated: {activeData?.latestUpdate}
        </div>

        {/* Critical News */}
        <div className="bg-blue-500/10 border-l-4 border-blue-500 p-4 rounded mb-6">
          <strong className="text-blue-400">Latest:</strong>{' '}
          <span className="text-gray-300">{activeData?.criticalNews}</span>
        </div>

        {/* Key Points */}
        {activeData?.keyPoints && activeData.keyPoints.length > 0 && (
          <div className="mb-6">
            <h3 className="text-lg font-bold mb-3">Key Points</h3>
            <ul className="space-y-2">
              {activeData.keyPoints.map((point: string, index: number) => (
                <li key={index} className="flex items-start gap-2">
                  <span className="text-blue-400 mt-1">•</span>
                  <span className="text-gray-300">{point}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Timeline */}
        {activeData?.timeline && activeData.timeline.length > 0 && (
          <div>
            <h3 className="text-lg font-bold mb-3">Timeline</h3>
            <div className="space-y-3">
              {activeData.timeline.map((item: { date: string; event: string }, index: number) => (
                <div key={index} className="flex gap-4 border-l-2 border-gray-700 pl-4">
                  <div className="text-sm font-semibold text-gray-400 min-w-[100px]">
                    {item.date}
                  </div>
                  <div className="text-gray-300">{item.event}</div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Categories
