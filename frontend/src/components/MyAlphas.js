// frontend/src/components/MyAlphas.js
import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './MyAlphas.css';

const MyAlphas = () => {
  const { user, isGuest, openLoginModal, deleteAlpha } = useAuth();
  const [sortBy, setSortBy] = useState('newest');

  if (isGuest) {
    return (
      <div className="my-alphas-container">
        <div className="alphas-guest-state">
          <div className="guest-icon">🔒</div>
          <h2>My Alpha Strategies</h2>
          <p>Sign in to save and manage your alpha strategies</p>
          <button className="login-prompt-btn" onClick={openLoginModal}>
            Sign In to Access My Alphas
          </button>
          <div className="guest-features">
            <h3>With an account, you can:</h3>
            <ul>
              <li>✅ Save unlimited alpha strategies</li>
              <li>✅ Compare performance across strategies</li>
              <li>✅ Export results and data</li>
              <li>✅ Access your strategies from anywhere</li>
              <li>✅ Track strategy performance over time</li>
            </ul>
          </div>
        </div>
      </div>
    );
  }

  const alphas = user?.alphas || [];

  const sortedAlphas = [...alphas].sort((a, b) => {
    switch (sortBy) {
      case 'newest':
        return new Date(b.createdAt) - new Date(a.createdAt);
      case 'oldest':
        return new Date(a.createdAt) - new Date(b.createdAt);
      case 'name':
        return a.name.localeCompare(b.name);
      case 'performance':
        const aReturn = a.returns?.totalReturn || 0;
        const bReturn = b.returns?.totalReturn || 0;
        return bReturn - aReturn;
      default:
        return 0;
    }
  });

  const handleDeleteAlpha = (alphaId, alphaName) => {
    if (window.confirm(`Are you sure you want to delete "${alphaName}"? This action cannot be undone.`)) {
      deleteAlpha(alphaId);
    }
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const formatReturn = (value) => {
    if (value === null || value === undefined || typeof value !== 'number' || isNaN(value)) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  if (alphas.length === 0) {
    return (
      <div className="my-alphas-container">
        <div className="alphas-empty-state">
          <div className="empty-icon">📊</div>
          <h2>No Alpha Strategies Yet</h2>
          <p>Start creating and testing alpha strategies in the Simulate tab. When you find a promising strategy, you can save it here for future reference.</p>
          <div className="empty-tips">
            <h3>Getting Started:</h3>
            <ol>
              <li>Go to the <strong>Simulate</strong> tab</li>
              <li>Choose your data source and load data</li>
              <li>Enter an alpha formula (e.g., <code>close / Ts_mean(close, 20) - 1</code>)</li>
              <li>Click <strong>Calculate Alpha</strong></li>
              <li>If satisfied with results, click <strong>Save Alpha</strong></li>
            </ol>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="my-alphas-container">
      <div className="alphas-header">
        <div className="header-left">
          <h2>My Alpha Strategies</h2>
          <span className="alpha-count">{alphas.length} saved strategies</span>
        </div>
        <div className="header-right">
          <label className="sort-label">
            Sort by:
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="sort-select"
            >
              <option value="newest">Newest First</option>
              <option value="oldest">Oldest First</option>
              <option value="name">Name A-Z</option>
              <option value="performance">Best Performance</option>
            </select>
          </label>
        </div>
      </div>

      <div className="alphas-list">
        {sortedAlphas.map((alpha) => (
          <div key={alpha.id} className="alpha-list-item">
            <div className="alpha-info">
              <span className="alpha-name">{alpha.name}</span>
              <span className="alpha-formula"><code>{alpha.formula}</code></span>
              <span className={`alpha-return ${
                (alpha.returns?.totalReturn || 0) > 0 ? 'positive' : 'negative'
              }`}>
                {formatReturn(alpha.returns?.totalReturn)}
              </span>
            </div>
            <button
              className="delete-btn"
              onClick={(e) => {
                e.stopPropagation();
                handleDeleteAlpha(alpha.id, alpha.name);
              }}
              title="Delete Alpha"
            >
              🗑️
            </button>
          </div>
        ))}
      </div>
    </div>
  );
};

export default MyAlphas;