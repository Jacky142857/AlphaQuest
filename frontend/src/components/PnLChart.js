// frontend/src/components/PnLChart.js
import React, { useState, useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Brush, ReferenceLine } from 'recharts';
import ChartEmptyState from './ChartEmptyState';
import './ChartEmptyState.css';

const PnLChart = ({ data, metrics, loading, isDataUploaded, hasFormula, onSaveAlpha }) => {
  const [selectedMetric, setSelectedMetric] = useState('pnl');

  // Available metrics for display
  const availableMetrics = [
    { key: 'pnl', label: 'Portfolio Value', color: '#4a90e2', icon: '📈' },
    { key: 'returns', label: 'Daily Returns', color: '#28a745', icon: '📊' },
    { key: 'drawdown', label: 'Drawdown', color: '#dc3545', icon: '📉' },
    { key: 'cumulative_returns', label: 'Cumulative Returns', color: '#6f42c1', icon: '🚀' }
  ];

  // Prepare data for chart with multiple metrics
  const chartData = useMemo(() => {
    if (!data) return [];

    return data.dates.map((date, index) => {
      const pnlValue = data.values[index];
      const prevPnlValue = index > 0 ? data.values[index - 1] : 1;
      const dailyReturn = ((pnlValue - prevPnlValue) / prevPnlValue) * 100;

      // Calculate running maximum for drawdown
      const runningMax = Math.max(...data.values.slice(0, index + 1));
      const drawdown = ((pnlValue - runningMax) / runningMax) * 100;

      // Cumulative returns percentage
      const cumulativeReturn = ((pnlValue - 1) * 100);

      return {
        date: date,
        pnl: pnlValue,
        returns: dailyReturn,
        drawdown: drawdown,
        cumulative_returns: cumulativeReturn,
        formatted_date: new Date(date).toLocaleDateString()
      };
    });
  }, [data]);

  // Get current metric info
  const currentMetric = availableMetrics.find(m => m.key === selectedMetric);

  if (loading) {
    return (
      <div className="chart-container">
        <h2>PnL Chart</h2>
        <div className="loading">
          Calculating alpha strategy...
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="chart-container">
        <h2>PnL Chart</h2>
        <ChartEmptyState
          hasData={isDataUploaded}
          hasFormula={hasFormula}
        />
      </div>
    );
  }

  // Custom tooltip with enhanced information
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      const value = payload[0].value;
      const dataPoint = chartData.find(d => d.date === label);

      const formatValue = (val, metric) => {
        switch (metric) {
          case 'pnl':
            return val.toFixed(4);
          case 'returns':
          case 'drawdown':
          case 'cumulative_returns':
            return `${val >= 0 ? '+' : ''}${val.toFixed(2)}%`;
          default:
            return val.toFixed(4);
        }
      };


      return (
        <div style={{
          backgroundColor: '#2a3b5c',
          border: '1px solid #4a5568',
          borderRadius: '8px',
          padding: '16px',
          color: 'white',
          boxShadow: '0 4px 12px rgba(0,0,0,0.3)',
          minWidth: '200px'
        }}>
          <p style={{
            margin: '0 0 12px 0',
            color: '#b0b0b0',
            fontSize: '14px',
            fontWeight: '600'
          }}>
            📅 {new Date(label).toLocaleDateString('en-US', {
              weekday: 'short',
              year: 'numeric',
              month: 'short',
              day: 'numeric'
            })}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ color: '#b0b0b0', fontSize: '13px' }}>{currentMetric?.label}:</span>
              <span style={{
                color: currentMetric?.color || '#4a90e2',
                fontWeight: '600',
                fontSize: '14px'
              }}>
                {formatValue(value, selectedMetric)}
              </span>
            </div>
            {dataPoint && selectedMetric !== 'pnl' && (
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ color: '#b0b0b0', fontSize: '13px' }}>Portfolio Value:</span>
                <span style={{
                  color: '#4a90e2',
                  fontWeight: '600',
                  fontSize: '14px'
                }}>
                  {dataPoint.pnl.toFixed(4)}
                </span>
              </div>
            )}
          </div>
        </div>
      );
    }
    return null;
  };

  // Format date for x-axis
  const formatXAxisDate = (tickItem) => {
    const date = new Date(tickItem);
    return date.toLocaleDateString('en-US', { month: 'short', year: '2-digit' });
  };

  return (
    <div className="chart-container">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
        <h2 style={{ margin: 0 }}>{currentMetric?.icon} {currentMetric?.label} Chart</h2>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          {onSaveAlpha && data && (
            <button
              onClick={onSaveAlpha}
              style={{
                background: 'linear-gradient(135deg, #4a90e2 0%, #357abd 100%)',
                color: 'white',
                border: 'none',
                padding: '10px 16px',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '14px',
                fontWeight: '600',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                boxShadow: '0 2px 8px rgba(74, 144, 226, 0.3)',
                transition: 'all 0.2s ease'
              }}
              onMouseEnter={(e) => {
                e.target.style.transform = 'translateY(-1px)';
                e.target.style.boxShadow = '0 4px 12px rgba(74, 144, 226, 0.4)';
              }}
              onMouseLeave={(e) => {
                e.target.style.transform = 'translateY(0)';
                e.target.style.boxShadow = '0 2px 8px rgba(74, 144, 226, 0.3)';
              }}
            >
              💾 Save Alpha
            </button>
          )}

          <div style={{
            display: 'flex',
            gap: '8px',
            background: '#f8f9fa',
            padding: '4px',
            borderRadius: '8px',
            border: '1px solid #e0e0e0'
          }}>
          {availableMetrics.map((metric) => (
            <button
              key={metric.key}
              onClick={() => setSelectedMetric(metric.key)}
              style={{
                background: selectedMetric === metric.key ? metric.color : 'transparent',
                color: selectedMetric === metric.key ? 'white' : '#666',
                border: 'none',
                padding: '8px 12px',
                borderRadius: '4px',
                cursor: 'pointer',
                fontSize: '12px',
                fontWeight: '500',
                transition: 'all 0.2s ease',
                display: 'flex',
                alignItems: 'center',
                gap: '4px'
              }}
            >
              <span>{metric.icon}</span>
              <span>{metric.label}</span>
            </button>
          ))}
          </div>
        </div>
      </div>

      <div className="chart-content">
        <ResponsiveContainer width="100%" height={500}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 100 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#4a5568" />
            <XAxis
              dataKey="date"
              stroke="#b0b0b0"
              tickFormatter={formatXAxisDate}
              angle={-45}
              textAnchor="end"
              height={80}
              interval="preserveStartEnd"
            />
            <YAxis
              stroke="#b0b0b0"
              tickFormatter={(value) => value.toFixed(2)}
            />
            <Tooltip content={<CustomTooltip />} />
            {selectedMetric === 'pnl' && (
              <ReferenceLine
                y={1}
                stroke="#666"
                strokeDasharray="2 2"
                label={{ value: "Break Even", position: "insideTopRight", style: { fontSize: '12px', fill: '#666' } }}
              />
            )}
            {selectedMetric === 'returns' && (
              <ReferenceLine
                y={0}
                stroke="#666"
                strokeDasharray="2 2"
                label={{ value: "0% Returns", position: "insideTopRight", style: { fontSize: '12px', fill: '#666' } }}
              />
            )}
            {selectedMetric === 'drawdown' && (
              <ReferenceLine
                y={0}
                stroke="#666"
                strokeDasharray="2 2"
                label={{ value: "No Drawdown", position: "insideTopRight", style: { fontSize: '12px', fill: '#666' } }}
              />
            )}
            {selectedMetric === 'cumulative_returns' && (
              <ReferenceLine
                y={0}
                stroke="#666"
                strokeDasharray="2 2"
                label={{ value: "0% Cumulative", position: "insideTopRight", style: { fontSize: '12px', fill: '#666' } }}
              />
            )}
            <Line
              type="monotone"
              dataKey={selectedMetric}
              stroke={currentMetric?.color || '#4a90e2'}
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 6, fill: currentMetric?.color || '#4a90e2', stroke: '#ffffff', strokeWidth: 2 }}
            />
            <Brush
              dataKey="date"
              height={40}
              stroke="#4a90e2"
              fill="rgba(74, 144, 226, 0.1)"
              tickFormatter={formatXAxisDate}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {metrics && (
        <div className="metrics-section">
          <h3>Performance Metrics</h3>
          <div className="metric-item">
            <span className="metric-label">Total Return</span>
            <span className={`metric-value ${metrics.total_return >= 0 ? 'positive' : 'negative'}`}>
              {metrics.total_return_pct}
            </span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Final PnL</span>
            <span className={`metric-value ${data.values[data.values.length - 1] >= 1 ? 'positive' : 'negative'}`}>
              {data.values[data.values.length - 1].toFixed(4)}
            </span>
          </div>
          <div className="metric-item">
            <span className="metric-label">Data Points</span>
            <span className="metric-value">
              {data.dates.length}
            </span>
          </div>
          {metrics.neutralization && (
            <div className="metric-item">
              <span className="metric-label">Market Neutralization</span>
              <span className={`metric-value ${metrics.neutralization === 'On' ? 'neutral' : 'default'}`}>
                {metrics.neutralization}
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default PnLChart;