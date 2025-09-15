import React from 'react';
import './LearnContent.css';

const Keywords = () => {
  const priceKeywords = [
    {
      keyword: 'Open',
      description: 'Opening price of the trading session',
      usage: 'Used in gap analysis, intraday patterns',
      example: 'Open - Close (overnight gap)'
    },
    {
      keyword: 'Close',
      description: 'Closing price of the trading session',
      usage: 'Most common price point for analysis',
      example: 'Close / Delta(Close, 1) - 1 (daily return)'
    },
    {
      keyword: 'High',
      description: 'Highest price during the trading session',
      usage: 'Momentum analysis, breakout detection',
      example: 'High - Open (intraday strength)'
    },
    {
      keyword: 'Low',
      description: 'Lowest price during the trading session',
      usage: 'Support levels, volatility measurement',
      example: 'Open - Low (downside pressure)'
    },
    {
      keyword: 'Volume',
      description: 'Number of shares traded during the session',
      usage: 'Liquidity analysis, confirmation signals',
      example: 'Volume * (Close - Open) (dollar volume)'
    },
    {
      keyword: 'Vwap',
      description: 'Volume-Weighted Average Price',
      usage: 'Fair value estimation, execution benchmarking',
      example: 'Close - Vwap (premium to fair value)'
    }
  ];

  const derivedMetrics = [
    {
      name: 'Daily Return',
      formula: 'Close / Delta(Close, 1) - 1',
      description: 'Percentage change from previous day'
    },
    {
      name: 'Intraday Range',
      formula: '(High - Low) / Open',
      description: 'Daily volatility normalized by opening price'
    },
    {
      name: 'Gap',
      formula: 'Open - Delta(Close, 1)',
      description: 'Overnight price movement'
    },
    {
      name: 'True Range',
      formula: 'High - Low',
      description: 'Daily price range (simplified version)'
    },
    {
      name: 'Volume Ratio',
      formula: 'Volume / Delta(Volume, 20)',
      description: 'Current volume vs 20-day average'
    }
  ];

  return (
    <div className="learn-content-wrapper">
      <h2>🔑 Market Data Keywords</h2>

      <section className="content-section">
        <p>
          Keywords represent different types of market data that can be used in alpha formulas.
          These are the building blocks of any quantitative strategy.
        </p>
      </section>

      <h3>Price & Volume Data</h3>
      <div className="keywords-grid">
        {priceKeywords.map((item, index) => (
          <div key={index} className="keyword-card">
            <div className="keyword-header">
              <h3 className="keyword-name">{item.keyword}</h3>
            </div>

            <div className="keyword-content">
              <p className="keyword-description">{item.description}</p>

              <div className="keyword-usage">
                <h4>Common Usage:</h4>
                <p>{item.usage}</p>
              </div>

              <div className="keyword-example">
                <h4>Example Formula:</h4>
                <code className="example-code">{item.example}</code>
              </div>
            </div>
          </div>
        ))}
      </div>

      <section className="content-section">
        <h3>Derived Metrics</h3>
        <p>These are common combinations of basic keywords that create meaningful financial metrics:</p>

        <div className="derived-metrics">
          {derivedMetrics.map((metric, index) => (
            <div key={index} className="metric-card">
              <h4 className="metric-name">{metric.name}</h4>
              <code className="metric-formula">{metric.formula}</code>
              <p className="metric-description">{metric.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="content-section">
        <h3>Data Frequency & Timing</h3>
        <div className="timing-info">
          <div className="timing-card">
            <h4>Daily Data</h4>
            <p>Most formulas work with daily OHLCV data. Each row represents one trading day.</p>
          </div>
          <div className="timing-card">
            <h4>Market Hours</h4>
            <p>Open/Close reflect regular trading hours. High/Low include extended hours if available.</p>
          </div>
          <div className="timing-card">
            <h4>Adjustments</h4>
            <p>Prices should be adjusted for splits and dividends for accurate historical analysis.</p>
          </div>
        </div>
      </section>

      <section className="content-section">
        <h3>Best Practices with Keywords</h3>
        <ul className="keyword-tips">
          <li><strong>Close</strong> is the most reliable price point for analysis</li>
          <li><strong>Volume</strong> should be used to confirm price movements</li>
          <li><strong>Vwap</strong> provides context for institutional trading patterns</li>
          <li><strong>High/Low</strong> help measure intraday volatility and momentum</li>
          <li><strong>Open</strong> captures overnight sentiment and gaps</li>
          <li>Always consider the <strong>economic meaning</strong> of your combinations</li>
        </ul>
      </section>

      <section className="content-section">
        <h3>Case Sensitivity</h3>
        <div className="case-note">
          <p>Keywords are <strong>case-insensitive</strong>. These are all equivalent:</p>
          <ul className="case-examples">
            <li><code>Close</code></li>
            <li><code>close</code></li>
            <li><code>CLOSE</code></li>
          </ul>
        </div>
      </section>
    </div>
  );
};

export default Keywords;