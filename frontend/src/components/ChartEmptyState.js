import React from 'react';
import './ChartEmptyState.css';

const ChartEmptyState = ({ step, hasData, hasFormula }) => {
  const getStepContent = () => {
    if (!hasData) {
      return {
        icon: "📁",
        title: "Upload Data First",
        description: "Click the 'Data Upload' button to load market data",
        stepNumber: "1",
        nextAction: "Upload CSV file or load Dow Jones 30 data"
      };
    }

    if (!hasFormula) {
      return {
        icon: "📝",
        title: "Enter Alpha Formula",
        description: "Write your trading strategy formula in the editor",
        stepNumber: "2",
        nextAction: "Try: Rank(Close - Open) for a simple example"
      };
    }

    return {
      icon: "🧮",
      title: "Calculate Alpha",
      description: "Your formula is ready - click Calculate to see results",
      stepNumber: "3",
      nextAction: "Click 'Calculate Alpha' or press Ctrl+Enter"
    };
  };

  const stepContent = getStepContent();

  return (
    <div className="chart-empty-state">
      <div className="empty-state-background">
        {/* Placeholder grid lines */}
        <svg className="placeholder-grid" viewBox="0 0 400 200">
          <defs>
            <pattern id="grid" width="40" height="20" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 20" fill="none" stroke="currentColor" strokeWidth="0.5" opacity="0.3"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />

          {/* Placeholder chart line */}
          <path
            d="M 20 150 Q 100 120 180 90 T 380 60"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            opacity="0.2"
            strokeDasharray="5,5"
          />

          {/* Placeholder data points */}
          <circle cx="20" cy="150" r="3" fill="currentColor" opacity="0.2" />
          <circle cx="100" cy="120" r="3" fill="currentColor" opacity="0.2" />
          <circle cx="180" cy="90" r="3" fill="currentColor" opacity="0.2" />
          <circle cx="260" cy="80" r="3" fill="currentColor" opacity="0.2" />
          <circle cx="340" cy="60" r="3" fill="currentColor" opacity="0.2" />

          {/* Axis lines */}
          <line x1="20" y1="20" x2="20" y2="180" stroke="currentColor" strokeWidth="1" opacity="0.3"/>
          <line x1="20" y1="180" x2="380" y2="180" stroke="currentColor" strokeWidth="1" opacity="0.3"/>
        </svg>
      </div>

      <div className="empty-state-content">
        <div className="step-indicator">
          <div className="step-number">{stepContent.stepNumber}</div>
          <div className="step-icon">{stepContent.icon}</div>
        </div>

        <h3 className="empty-state-title">{stepContent.title}</h3>
        <p className="empty-state-description">{stepContent.description}</p>
        <div className="empty-state-action">{stepContent.nextAction}</div>

        <div className="workflow-steps">
          <div className={`workflow-step ${!hasData ? 'active' : 'completed'}`}>
            <div className="workflow-step-number">1</div>
            <div className="workflow-step-text">Upload Data</div>
          </div>
          <div className="workflow-connector"></div>
          <div className={`workflow-step ${hasData && !hasFormula ? 'active' : hasData ? 'completed' : 'pending'}`}>
            <div className="workflow-step-number">2</div>
            <div className="workflow-step-text">Enter Formula</div>
          </div>
          <div className="workflow-connector"></div>
          <div className={`workflow-step ${hasData && hasFormula ? 'active' : 'pending'}`}>
            <div className="workflow-step-number">3</div>
            <div className="workflow-step-text">Calculate</div>
          </div>
        </div>

        <div className="example-preview">
          <div className="example-title">What you'll see:</div>
          <div className="example-items">
            <div className="example-item">
              <span className="example-icon">📊</span>
              <span>Interactive PnL chart with zoom & hover</span>
            </div>
            <div className="example-item">
              <span className="example-icon">📈</span>
              <span>Performance metrics (returns, Sharpe ratio)</span>
            </div>
            <div className="example-item">
              <span className="example-icon">⚡</span>
              <span>Real-time strategy analysis</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChartEmptyState;