import React from 'react';
import './LearnContent.css';

const Documentation = () => {
  return (
    <div className="learn-content-wrapper">
      <h2>📖 General Documentation</h2>

      <section className="content-section">
        <h3>What is Alpha Formula Development?</h3>
        <p>
          Alpha formulas are mathematical expressions used to predict stock returns or identify trading opportunities.
          They combine various market data points (price, volume, etc.) with mathematical operators to create signals
          that can drive investment strategies.
        </p>
      </section>

      <section className="content-section">
        <h3>Getting Started</h3>
        <div className="steps">
          <div className="step">
            <h4>1. Load Data</h4>
            <p>Start by loading your stock data using the "Load Dow Jones 30" button or upload your own CSV file.</p>
          </div>
          <div className="step">
            <h4>2. Set Date Range</h4>
            <p>Define the time period you want to analyze using the date range picker.</p>
          </div>
          <div className="step">
            <h4>3. Create Your Alpha</h4>
            <p>Write your alpha formula using market data keywords and mathematical operators.</p>
          </div>
          <div className="step">
            <h4>4. Backtest & Analyze</h4>
            <p>Run your alpha formula and analyze the performance metrics and charts.</p>
          </div>
        </div>
      </section>

      <section className="content-section">
        <h3>Formula Syntax</h3>
        <div className="syntax-example">
          <h4>Basic Structure:</h4>
          <code className="formula-code">
            operator(data_field, parameters)
          </code>
          <p>Example: <code className="inline-code">Rank(Close - Open)</code></p>
        </div>

        <div className="syntax-example">
          <h4>Complex Example:</h4>
          <code className="formula-code">
            quantile(Rank(Close - Open) * Volume, driver=gaussian, sigma=0.5)
          </code>
        </div>
      </section>

      <section className="content-section">
        <h3>Best Practices</h3>
        <ul className="best-practices">
          <li>Start simple - test basic formulas before adding complexity</li>
          <li>Use proper risk management settings (truncation, position limits)</li>
          <li>Validate your formulas across different time periods</li>
          <li>Consider transaction costs and delays in real trading</li>
          <li>Always backtest before implementing live strategies</li>
        </ul>
      </section>

      <section className="content-section">
        <h3>Common Patterns</h3>
        <div className="patterns">
          <div className="pattern">
            <h4>Mean Reversion</h4>
            <code className="inline-code">Rank(Open - Close)</code>
            <p>Buys stocks that closed lower than they opened</p>
          </div>
          <div className="pattern">
            <h4>Momentum</h4>
            <code className="inline-code">Rank(Close - Delta(Close, 5))</code>
            <p>Buys stocks that have risen over the past 5 days</p>
          </div>
          <div className="pattern">
            <h4>Volume-Price</h4>
            <code className="inline-code">Rank((Close - Open) * Volume)</code>
            <p>Combines price movement with volume strength</p>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Documentation;