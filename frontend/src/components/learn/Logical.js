import React from 'react';
import './LearnContent.css';

const Logical = ({ theme }) => {
  const logicalOperators = [
    {
      name: 'and',
      syntax: 'and(input1, input2)',
      description: 'Logical AND operator, returns true if both operands are true and returns false otherwise',
      example: 'and(Volume > 1000000, Close > Open)',
      explanation: 'Returns true only when both volume exceeds 1M and close is above open'
    },
    {
      name: 'or',
      syntax: 'or(input1, input2)',
      description: 'Logical OR operator returns true if either or both inputs are true and returns false otherwise',
      example: 'or(Volume > ts_sum(Volume, 5)/5, Close > High * 0.95)',
      explanation: 'Returns true when either volume is above average OR close is near daily high'
    },
    {
      name: 'not',
      syntax: 'not(x)',
      description: 'Returns the logical negation of x. If x is true (1), it returns false (0), and if input is false (0), it returns true (1)',
      example: 'not(Close < Open)',
      explanation: 'Returns true when close is NOT below open (i.e., when close >= open)'
    },
    {
      name: 'is_nan',
      syntax: 'is_nan(input)',
      description: 'If input == NaN return 1 else return 0',
      example: 'is_nan(Delta(Close, 1))',
      explanation: 'Returns 1 for the first day when previous close is unavailable'
    },
    {
      name: 'lt',
      syntax: 'lt(input1, input2)',
      description: 'If input1 < input2 return true, else return false',
      example: 'lt(Close, Open)',
      explanation: 'Returns true when closing price is lower than opening price'
    },
    {
      name: 'le',
      syntax: 'le(input1, input2)',
      description: 'Returns true if input1 <= input2, return false otherwise',
      example: 'le(Volume, ts_sum(Volume, 10)/10)',
      explanation: 'Returns true when volume is less than or equal to 10-day average'
    },
    {
      name: 'eq',
      syntax: 'eq(input1, input2)',
      description: 'Returns true if both inputs are same and returns false otherwise',
      example: 'eq(Rank(Close), 1.0)',
      explanation: 'Returns true for the stock with the highest closing price'
    },
    {
      name: 'gt',
      syntax: 'gt(input1, input2)',
      description: 'Logic comparison operators to compares two inputs',
      example: 'gt(Close, High * 0.98)',
      explanation: 'Returns true when close is within 2% of the daily high'
    },
    {
      name: 'ge',
      syntax: 'ge(input1, input2)',
      description: 'Returns true if input1 >= input2, return false otherwise',
      example: 'ge(Volume, 500000)',
      explanation: 'Returns true when volume is at least 500,000 shares'
    },
    {
      name: 'ne',
      syntax: 'ne(input1, input2)',
      description: 'Returns true if both inputs are NOT the same and returns false otherwise',
      example: 'ne(Close, Open)',
      explanation: 'Returns true when closing price differs from opening price'
    }
  ];

  return (
    <div className={`learn-content-wrapper ${theme === 'dark' ? 'dark-theme' : 'light-theme'}`}>
      <h2>🔗 Logical Operators</h2>

      <section className="content-section">
        <p>
          Logical operators allow you to create complex conditional expressions by combining
          multiple conditions. They return 1 (true) or 0 (false) and can be used with
          <code>if_else</code> to create sophisticated trading rules.
        </p>
      </section>

      <div className="operators-grid">
        {logicalOperators.map((op, index) => (
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
        <h3>Complex Logical Expressions</h3>
        <p>You can combine multiple logical operators to create sophisticated conditions:</p>

        <div className="combination-examples">
          <div className="combo-example">
            <code className="formula-code">
              and(gt(Volume, ts_sum(Volume, 5)/5), lt(Close, Open))
            </code>
            <p>High volume AND bearish day (close below open)</p>
          </div>

          <div className="combo-example">
            <code className="formula-code">
              or(and(gt(Close, High * 0.95), gt(Volume, 1000000)), lt(Close, Low * 1.05))
            </code>
            <p>Either (near high AND high volume) OR near daily low</p>
          </div>

          <div className="combo-example">
            <code className="formula-code">
              not(and(eq(Close, Open), eq(High, Low)))
            </code>
            <p>NOT a doji candle (where open=close and high=low)</p>
          </div>
        </div>
      </section>

      <section className="content-section">
        <h3>Using with if_else for Conditional Strategies</h3>
        <p>Logical operators are most powerful when combined with <code>if_else</code>:</p>

        <div className="combination-examples">
          <div className="combo-example">
            <code className="formula-code">
              if_else(and(gt(Volume, ts_sum(Volume, 20)/20), lt(Close, Open)),
                      Rank(-Returns(Close, 1)),
                      Rank(Returns(Close, 1)))
            </code>
            <p>Contrarian strategy on high-volume down days, momentum strategy otherwise</p>
          </div>

          <div className="combo-example">
            <code className="formula-code">
              if_else(or(gt(Close, High * 0.98), lt(Close, Low * 1.02)),
                      0,
                      Rank(ts_delta(Close, 3)))
            </code>
            <p>Only trade when price is not at extremes, using 3-day price change</p>
          </div>
        </div>
      </section>

      <section className="content-section">
        <h3>Tips for Logical Operators</h3>
        <ul className="operator-tips">
          <li><strong>Combine conditions</strong> using <code>and</code> and <code>or</code> for multi-factor signals</li>
          <li><strong>Use comparisons</strong> like <code>gt</code>, <code>lt</code> instead of native operators for clarity</li>
          <li><strong>Handle missing data</strong> with <code>is_nan</code> to avoid errors</li>
          <li><strong>Invert logic</strong> with <code>not</code> to create opposite conditions</li>
          <li><strong>Test complex expressions</strong> step by step to ensure they work as expected</li>
        </ul>
      </section>
    </div>
  );
};

export default Logical;