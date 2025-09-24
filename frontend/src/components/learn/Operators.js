import React from 'react';
import './LearnContent.css';

const Operators = ({ theme }) => {
  const operatorCategories = {
    arithmetic: [
      {
        name: 'add',
        syntax: 'add(x, y, ..., filter=false)',
        description: 'Add all inputs (at least 2 inputs required). If filter = true, filter all input NaN to 0 before adding',
        example: 'add(Returns(Close, 1), Returns(Volume, 1), filter=true)',
        explanation: 'Add price and volume returns, treating NaN values as 0'
      },
      {
        name: 'subtract',
        syntax: 'subtract(x, y, filter=false)',
        description: 'x - y. If filter = true, filter all input NaN to 0 before subtracting',
        example: 'subtract(Close, Open, filter=true)',
        explanation: 'Calculate daily price change, treating NaN values as 0'
      },
      {
        name: 'multiply',
        syntax: 'multiply(x, y, ..., filter=false)',
        description: 'Multiply all inputs. At least 2 inputs are required. Filter sets the NaN values to 1',
        example: 'multiply(Returns(Close, 1), Volume, filter=true)',
        explanation: 'Multiply returns by volume, treating NaN values as 1'
      },
      {
        name: 'divide',
        syntax: 'divide(x, y)',
        description: 'x / y',
        example: 'divide(Close, Open)',
        explanation: 'Calculate the ratio of closing price to opening price'
      },
      {
        name: 'power',
        syntax: 'power(x, y)',
        description: 'x ^ y',
        example: 'power(Returns(Close, 1), 2)',
        explanation: 'Square the daily returns'
      },
      {
        name: 'signed_power',
        syntax: 'signed_power(x, y)',
        description: 'x raised to the power of y such that final result preserves sign of x',
        example: 'signed_power(Returns(Close, 1), 2)',
        explanation: 'Square the magnitude of returns while preserving their sign'
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
        name: 'log',
        syntax: 'log(x)',
        description: 'Natural logarithm. For example: log(High/Low) uses natural logarithm of high/low ratio as stock weights',
        example: 'log(divide(High, Low))',
        explanation: 'Natural log of the daily price range ratio'
      },
      {
        name: 'inverse',
        syntax: 'inverse(x)',
        description: '1 / x',
        example: 'inverse(Returns(Close, 1))',
        explanation: 'Take the reciprocal of daily returns'
      },
      {
        name: 'reverse',
        syntax: 'reverse(x)',
        description: '-x',
        example: 'reverse(Returns(Close, 1))',
        explanation: 'Flip the sign of daily returns for contrarian strategy'
      },
      {
        name: 'sign',
        syntax: 'sign(x)',
        description: 'Returns the sign of x. If input = NaN, return NaN',
        example: 'sign(Returns(Close, 1))',
        explanation: 'Get the direction of daily returns (+1, -1, or 0)'
      },
      {
        name: 'max',
        syntax: 'max(x, y, ...)',
        description: 'Maximum value of all inputs. At least 2 inputs are required',
        example: 'max(Close, Open, High)',
        explanation: 'Return the highest value among close, open, and high prices'
      },
      {
        name: 'min',
        syntax: 'min(x, y, ...)',
        description: 'Minimum value of all inputs. At least 2 inputs are required',
        example: 'min(Close, Open, Low)',
        explanation: 'Return the lowest value among close, open, and low prices'
      }
    ],

    logical: [
      {
        name: 'if_else',
        syntax: 'if_else(event_condition, Alpha_expression_1, Alpha_expression_2)',
        description: 'Conditional operator that returns Alpha_expression_1 when event_condition is true, otherwise Alpha_expression_2',
        example: 'if_else(Volume > ts_sum(Volume, 5)/5, 2 * (-ts_delta(Close, 3)), (-ts_delta(Close, 3)))',
        explanation: 'If volume exceeds 5-day average, take larger position based on price reversion, otherwise take normal position'
      },
      {
        name: 'and_op',
        syntax: 'and_op(input1, input2)',
        description: 'Logical AND operator. Returns true if both operands are true and returns false otherwise. Converts inputs to boolean: > 0 means True, <= 0 means False',
        example: 'and_op(Volume > ts_sum(Volume, 5)/5, Returns(Close, 1) > 0)',
        explanation: 'Returns 1 when both volume is above average AND returns are positive'
      },
      {
        name: 'or_op',
        syntax: 'or_op(input1, input2)',
        description: 'Logical OR operator. Returns true if either or both inputs are true and returns false otherwise',
        example: 'or_op(Volume > ts_sum(Volume, 10)/10, abs(Returns(Close, 1)) > 0.05)',
        explanation: 'Returns 1 when either volume is high OR daily return exceeds 5%'
      },
      {
        name: 'not_op',
        syntax: 'not_op(x)',
        description: 'Returns the logical negation of x. If x is true (1), it returns false (0), and if input is false (0), it returns true (1)',
        example: 'not_op(Returns(Close, 1) > 0)',
        explanation: 'Returns 1 when returns are NOT positive (for contrarian strategies)'
      },
      {
        name: 'lt_op',
        syntax: 'lt_op(input1, input2)',
        description: 'If input1 < input2 return true, else return false',
        example: 'lt_op(Close, ts_mean(Close, 20))',
        explanation: 'Returns 1 when current price is below 20-day moving average'
      },
      {
        name: 'le_op',
        syntax: 'le_op(input1, input2)',
        description: 'Returns true if input1 <= input2, return false otherwise',
        example: 'le_op(Volume, ts_mean(Volume, 10))',
        explanation: 'Returns 1 when volume is at or below 10-day average'
      },
      {
        name: 'gt_op',
        syntax: 'gt_op(input1, input2)',
        description: 'Logic comparison operators to compares two inputs',
        example: 'gt_op(Volume, ts_mean(Volume, 20))',
        explanation: 'Returns 1 when volume exceeds 20-day average'
      },
      {
        name: 'ge_op',
        syntax: 'ge_op(input1, input2)',
        description: 'Returns true if input1 >= input2, return false otherwise',
        example: 'ge_op(Returns(Close, 1), 0)',
        explanation: 'Returns 1 when daily returns are non-negative'
      },
      {
        name: 'eq_op',
        syntax: 'eq_op(input1, input2)',
        description: 'Returns true if both inputs are same and returns false otherwise',
        example: 'eq_op(sign(Returns(Close, 1)), sign(Returns(Close, 5)))',
        explanation: 'Returns 1 when 1-day and 5-day return signs match (trend consistency)'
      },
      {
        name: 'ne_op',
        syntax: 'ne_op(input1, input2)',
        description: 'Returns true if both inputs are NOT the same and returns false otherwise',
        example: 'ne_op(sign(Returns(Close, 1)), sign(Returns(Open, 1)))',
        explanation: 'Returns 1 when close and open return directions differ (gap events)'
      },
      {
        name: 'is_nan',
        syntax: 'is_nan(input_val)',
        description: 'If input == NaN return 1 else return 0',
        example: 'is_nan(Returns(Close, 1))',
        explanation: 'Identifies missing return data (useful for data quality checks)'
      }
    ],

    timeSeries: [
      {
        name: 'Delta',
        syntax: 'Delta(expression, n)',
        description: 'Difference between current value and value n periods ago',
        example: 'Delta(Close, 5)',
        explanation: 'Current close price minus close price 5 days ago'
      },
      {
        name: 'ts_delta',
        syntax: 'ts_delta(expression, periods=1)',
        description: 'Time-series difference calculation',
        example: 'ts_delta(Close, 3)',
        explanation: 'Current close minus close from 3 periods ago'
      },
      {
        name: 'Sum',
        syntax: 'Sum(expression, n)',
        description: 'Rolling sum over the last n periods',
        example: 'Sum(Volume, 10)',
        explanation: 'Total volume over the past 10 trading days'
      },
      {
        name: 'ts_sum',
        syntax: 'ts_sum(expression, periods)',
        description: 'Time-series rolling sum with proper period handling',
        example: 'ts_sum(Volume, 10)',
        explanation: 'Sum of volume over the past 10 periods'
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
        name: 'ts_arg_min',
        syntax: 'ts_arg_min(x, d)',
        description: 'Returns the relative index of the min value in the time series for the past d days. If current day has the min value, returns 0. If previous day has the min value, returns 1.',
        example: 'ts_arg_min(Close, 6)',
        explanation: 'If values for past 6 days are [6,2,8,5,9,4] with min value 2 one day before today, returns 1'
      },
      {
        name: 'ts_av_diff',
        syntax: 'ts_av_diff(x, d)',
        description: 'Returns x - ts_mean(x, d), but deals with NaNs carefully. NaNs are ignored during mean computation',
        example: 'ts_av_diff(Close, 6)',
        explanation: 'If d=6 and values are [6,2,8,5,9,NaN] then ts_mean=6 (ignoring NaN), so result = 6-6 = 0'
      },
      {
        name: 'ts_backfill',
        syntax: 'ts_backfill(x, lookback=252, k=1, ignore="NAN")',
        description: 'Replaces NaN values with the last available non-NaN value. Improves weight coverage and may help reduce drawdown risk',
        example: 'ts_backfill(Close, 252)',
        explanation: 'If current close is NaN, use the most recent available non-NaN close value from past 252 days'
      },
      {
        name: 'Returns',
        syntax: 'Returns(price_series, periods=1)',
        description: 'Calculate multi-period returns safely',
        example: 'Returns(Close, 5)',
        explanation: '5-day return calculation with proper handling of missing data'
      },
      {
        name: 'hump',
        syntax: 'hump(alpha_values, hump=0.01)',
        description: 'Limits alpha changes to reduce turnover and transaction costs',
        example: 'hump(Rank(Returns(Close, 1)), 0.02)',
        explanation: 'Smooths momentum signals with 2% turnover control'
      }
    ],

    grouping: [
      {
        name: 'Rank',
        syntax: 'Rank(expression)',
        description: 'Cross-sectional ranking of values from 0 to 1',
        example: 'Rank(Close - Open)',
        explanation: 'Ranks all stocks by their daily price change, with highest getting 1.0'
      },
      {
        name: 'quantile',
        syntax: 'quantile(expression, driver=gaussian, sigma=1.0)',
        description: 'Quantile transformation with distribution mapping',
        example: 'quantile(Close - Open, driver=gaussian, sigma=0.5)',
        explanation: 'Transforms daily returns using normal distribution'
      },
      {
        name: 'bucket',
        syntax: 'bucket(expression, buckets="0.2,0.5,0.7", skipBoth=True)',
        description: 'Convert float values into discrete group indices',
        example: 'bucket(Rank(Volume), buckets="0.2,0.5,0.7")',
        explanation: 'Groups stocks by volume ranks into specified buckets for analysis'
      },
      {
        name: 'densify',
        syntax: 'densify(x)',
        description: 'Converts a grouping field of many buckets into lesser number of only available buckets so as to make working with grouping fields computationally efficient',
        example: 'densify(bucket(Rank(Volume), buckets="0.2,0.5,0.8"))',
        explanation: 'Compress volume rank buckets to use only consecutive indices'
      },
      {
        name: 'group_neutralize',
        syntax: 'group_neutralize(values, groups)',
        description: 'Subtract group means to create market-neutral signals',
        example: 'group_neutralize(Returns(Close, 1), my_groups)',
        explanation: 'Removes group-specific bias from returns for cleaner alpha'
      },
      {
        name: 'scale',
        syntax: 'scale(x, scale=1, longscale=1, shortscale=1)',
        description: 'Scales input to booksize. Can scale long and short positions separately. Normalizes so sum of abs(x) equals 1. May help reduce outliers',
        example: 'scale(Returns(Close, 1), longscale=4, shortscale=3)',
        explanation: 'Scale daily returns with 4x leverage for long positions and 3x leverage for short positions'
      }
    ],

    conditional: [
      {
        name: 'trade_when',
        syntax: 'trade_when(trigger_condition, alpha_expression, exit_condition)',
        description: 'Conditional trading based on market conditions',
        example: 'trade_when(Volume > ts_sum(Volume, 5)/5, Rank(-Returns(Close, 1)), -1)',
        explanation: 'Only trade when volume exceeds 5-day average, hold contrarian positions'
      }
    ]
  };

  const categoryTitles = {
    arithmetic: '🧮 Arithmetic Operators',
    logical: '🔀 Logical & Comparison Operators',
    timeSeries: '📈 Time Series Operators',
    grouping: '📊 Grouping & Ranking Operators',
    conditional: '⚡ Conditional Trading Operators'
  };

  return (
    <div className={`learn-content-wrapper ${theme === 'dark' ? 'dark-theme' : 'light-theme'}`}>
      <h2>⚙️ Mathematical Operators</h2>

      <section className="content-section">
        <p>
          Operators are functions that transform market data into alpha signals.
          They can be applied to individual data fields or combined expressions.
        </p>
      </section>

      {Object.keys(operatorCategories).map((category) => (
        <section key={category} className="operator-category">
          <h3 className="category-title">{categoryTitles[category]}</h3>

          <div className="operators-grid">
            {operatorCategories[category].map((op, index) => (
              <div key={index} className="operator-card">
                <div className="operator-header">
                  <h4 className="operator-name">{op.name}</h4>
                  <code className="operator-syntax">{op.syntax}</code>
                </div>

                <div className="operator-content">
                  <p className="operator-description">{op.description}</p>

                  <div className="operator-example">
                    <h5>Example:</h5>
                    <code className="example-code">{op.example}</code>
                    <p className="example-explanation">{op.explanation}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </section>
      ))}

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
              if_else(Volume > ts_sum(Volume, 5)/5, Rank(-Returns(Close, 1)), Rank(Returns(Close, 1)))
            </code>
            <p>Contrarian strategy on high volume days, momentum strategy otherwise</p>
          </div>

          <div className="combo-example">
            <code className="formula-code">
              and_op(gt_op(Volume, ts_mean(Volume, 10)), lt_op(Close, ts_mean(Close, 20)))
            </code>
            <p>Logical combination: high volume AND price below moving average (breakout setup)</p>
          </div>
        </div>
      </section>

      <section className="content-section">
        <h3>Category Overview</h3>
        <div className="category-overview">
          <div className="overview-item">
            <h4>🧮 Arithmetic Operators</h4>
            <p>Basic mathematical operations like addition, multiplication, logarithms, and power functions. Essential for combining signals and mathematical transformations.</p>
          </div>

          <div className="overview-item">
            <h4>🔀 Logical & Comparison Operators</h4>
            <p>Boolean logic and comparison functions for building conditional strategies and filtering signals based on market conditions.</p>
          </div>

          <div className="overview-item">
            <h4>📈 Time Series Operators</h4>
            <p>Functions that work with historical data including rolling calculations, differences, and time-based transformations.</p>
          </div>

          <div className="overview-item">
            <h4>📊 Grouping & Ranking Operators</h4>
            <p>Cross-sectional operations for ranking, bucketing, and normalizing signals across stocks for market-neutral strategies.</p>
          </div>

          <div className="overview-item">
            <h4>⚡ Conditional Trading Operators</h4>
            <p>Advanced operators for implementing conditional trading logic with entry and exit conditions.</p>
          </div>
        </div>
      </section>

      <section className="content-section">
        <h3>Best Practices by Category</h3>
        <div className="best-practices-categorized">
          <div className="practice-category">
            <h4>Arithmetic Operations</h4>
            <ul>
              <li>Use <code>filter=true</code> in add/multiply/subtract for NaN handling</li>
              <li>Apply <code>signed_power</code> to reduce outliers while preserving direction</li>
              <li>Leverage <code>log</code> for ratio-based strategies and volatility measures</li>
            </ul>
          </div>

          <div className="practice-category">
            <h4>Logical & Comparison</h4>
            <ul>
              <li>Combine multiple conditions with <code>and_op</code> and <code>or_op</code></li>
              <li>Use comparison operators for threshold-based filtering</li>
              <li>Apply <code>is_nan</code> for data quality checks</li>
            </ul>
          </div>

          <div className="practice-category">
            <h4>Time Series</h4>
            <ul>
              <li>Use <code>ts_backfill</code> to improve data coverage</li>
              <li>Apply <code>hump</code> to reduce turnover and transaction costs</li>
              <li>Leverage <code>ts_av_diff</code> for NaN-safe mean deviation</li>
            </ul>
          </div>

          <div className="practice-category">
            <h4>Grouping & Ranking</h4>
            <ul>
              <li><code>Rank</code> is essential for market-neutral signals</li>
              <li>Use <code>scale</code> for proper position sizing</li>
              <li>Apply <code>densify</code> after bucketing for efficiency</li>
            </ul>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Operators;