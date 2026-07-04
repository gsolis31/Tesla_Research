import { useEffect, useRef } from 'react'

function StockPriceTile() {
  const container = useRef<HTMLDivElement>(null)

  useEffect(() => {
    // Clear any existing widget
    if (container.current) {
      container.current.innerHTML = ''
    }

    // Create TradingView symbol info widget
    const script = document.createElement('script')
    script.src = 'https://s3.tradingview.com/external-embedding/embed-widget-symbol-info.js'
    script.type = 'text/javascript'
    script.async = true
    script.innerHTML = JSON.stringify({
      symbol: 'NASDAQ:TSLA',
      width: 400,
      locale: 'en',
      colorTheme: 'dark',
      isTransparent: false,
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
    <div className="inline-block bg-gray-800 rounded-lg border border-gray-700 overflow-hidden">
      <div className="tradingview-widget-container" style={{ width: '400px', maxHeight: '270px', overflow: 'hidden' }}>
        <div
          ref={container}
          className="tradingview-widget-container__widget"
        />
      </div>
    </div>
  )
}

export default StockPriceTile
