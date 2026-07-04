import { useEffect, useRef } from 'react'

function TradingViewWidget() {
  const container = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Clear any existing widget
    if (container.current) {
      container.current.innerHTML = ''
    }

    // Create TradingView widget script
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-advanced-chart.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = JSON.stringify({
      autosize: true,
      symbol: 'NASDAQ:TSLA',
      interval: 'D',
      timezone: 'Etc/UTC',
      theme: 'dark',
      style: '1',
      locale: 'en',
      enable_publishing: false,
      backgroundColor: 'rgba(19, 23, 34, 1)',
      gridColor: 'rgba(42, 46, 57, 0.06)',
      hide_top_toolbar: false,
      hide_legend: false,
      save_image: false,
      container_id: 'tradingview_widget',
    })

    if (container.current) {
      container.current.appendChild(script)
    }

    // Cleanup
    return () => {
      if (container.current) {
        container.current.innerHTML = ''
      }
    }
  }, [])

  return (
    <div className="tradingview-widget-container bg-gray-800 rounded-lg overflow-hidden border border-gray-700">
      <div
        ref={container}
        className="tradingview-widget-container__widget"
        style={{ height: '400px', width: '100%' }}
      />
    </div>
  )
}

export default TradingViewWidget
