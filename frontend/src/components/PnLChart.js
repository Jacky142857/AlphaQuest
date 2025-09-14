// frontend/src/components/PnLChart.js
import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const PnLChart = ({ data, metrics, loading }) => {
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
        <div className="chart-placeholder">
          Upload data and submit an alpha formula to see the PnL chart
        </div>
      </div>
    );
  }

  // Prepare data for chart
  const chartData = data.dates.map((date, index) => ({
    date: date,
    pnl: data.values[index],
    formatted_date: new Date(date).toLocaleDateString()
  }));

  // Custom tooltip
  const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
      return (
        <div style={{
          backgroundColor: '#2a3b5c',
          border: '1px solid #4a5568',
          borderRadius: '6px',
          padding: '12px',
          color: 'white'
        }}>
          <p style={{ margin: '0 0 8px 0', color: '#b0b0b0' }}>
            {new Date(label).toLocaleDateString()}
          </p>
          <p style={{ margin: 0, color: '#4a90e2' }}>
            PnL: {payload[0].value.toFixed(4)}
          </p>
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
      <h2>PnL Chart</h2>
      
      <div className="chart-content">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 60 }}>
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
            <Line 
              type="monotone" 
              dataKey="pnl" 
              stroke="#4a90e2" 
              strokeWidth={2}
              dot={false}
              activeDot={{ r: 4, fill: '#4a90e2' }}
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
        </div>
      )}
    </div>
  );
};

export default PnLChart;