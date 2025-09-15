import React from 'react';
import './LearnContent.css';

const Operators = () => {
  const operators = [
    {
      name: 'Rank',
      syntax: 'Rank(expression)',
      description: 'Cross-sectional ranking of values from 0 to 1',
      example: 'Rank(Close - Open)',
      explanation: 'Ranks all stocks by their daily price change, with highest getting 1.0'
    },
    {
      name: 'Delta',
      syntax: 'Delta(expression, n)',
      description: 'Difference between current value and value n periods ago',
      example: 'Delta(Close, 5)',
      explanation: 'Current close price minus close price 5 days ago'
    },
    {
      name: 'Sum',
      syntax: 'Sum(expression, n)',
      description: 'Rolling sum over the last n periods',
      example: 'Sum(Volume, 10)',
      explanation: 'Total volume over the past 10 trading days'
    },
    {
      name: 'Ts_Rank',
      syntax: 'Ts_rank(expression, n)',
      description: 'Time-series rank of current value within the last n periods',
      example: 'Ts_rank(Close, 20)',
      explanation: 'Rank of today\'s close price within the past 20 days'
    },
    {
      name: 'Ts_ArgMax',
      syntax: 'Ts_argmax(expression, n)',
      description: 'Number of periods since the maximum value in the last n periods',
      example: 'Ts_argmax(High, 30)',
      explanation: 'Days since the highest price in the past 30 days'
    },
    {
      name: 'Abs',
      syntax: 'Abs(expression)',
      description: 'Absolute value of the expression',
      example: 'Abs(Close - Open)',
      explanation: 'Absolute daily price change, always positive'
    },
    {
      name: 'Sqrt',
      syntax: 'Sqrt(expression)',
      description: 'Square root of the expression',
      example: 'Sqrt(Volume)',
      explanation: 'Square root of trading volume'
    },
    {
      name: 'quantile',
      syntax: 'quantile(expression, driver=gaussian, sigma=1.0)',
      description: 'Quantile transformation with distribution mapping',
      example: 'quantile(Close - Open, driver=gaussian, sigma=0.5)',
      explanation: 'Transforms daily returns using normal distribution'
    }
  ];

  return (
    <div className="learn-content-wrapper">
      <h2>⚙️ Mathematical Operators</h2>

      <section className="content-section">
        <p>
          Operators are functions that transform market data into alpha signals.
          They can be applied to individual data fields or combined expressions.
        </p>
      </section>

      <div className="operators-grid">
        {operators.map((op, index) => (
          <div key={index} className="operator-card">
            <div className="operator-header">
              <h3 className="operator-name">{op.name}</h3>
              <code className="operator-syntax">{op.syntax}</code>
            </div>

            <div className="operator-content">
              <p className="operator-description">{op.description}</p>

              <div className="operator-example">
                <h4>Example:</h4>
                <code className="example-code">{op.example}</code>
                <p className="example-explanation">{op.explanation}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <section className="content-section">
        <h3>Combining Operators</h3>
        <p>Operators can be nested and combined to create sophisticated alpha formulas:</p>

        <div className="combination-examples">
          <div className="combo-example">
            <code className="formula-code">
              Rank(Sum(Close - Open, 5))
            </code>
            <p>Ranks stocks by their 5-day cumulative price change</p>
          </div>

          <div className="combo-example">
            <code className="formula-code">
              Delta(Rank(Close), 1) * Sqrt(Volume)
            </code>
            <p>Change in rank weighted by volume strength</p>
          </div>

          <div className="combo-example">
            <code className="formula-code">
              Abs(Ts_rank(Close, 20) - 0.5)
            </code>
            <p>Distance from median rank over 20-day window</p>
          </div>
        </div>
      </section>

      <section className="content-section">
        <h3>Tips for Using Operators</h3>
        <ul className="operator-tips">
          <li><strong>Rank</strong> is essential for creating market-neutral signals</li>
          <li><strong>Delta</strong> helps capture momentum and mean reversion</li>
          <li><strong>Time-series functions</strong> (Ts_rank, Ts_argmax) add temporal context</li>
          <li><strong>Mathematical functions</strong> (Abs, Sqrt) help normalize distributions</li>
          <li><strong>quantile</strong> is powerful for creating normally-distributed signals</li>
        </ul>
      </section>
    </div>
  );
};

export default Operators;