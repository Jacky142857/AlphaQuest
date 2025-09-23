import React from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import Documentation from './learn/Documentation';
import Operators from './learn/Operators';
import Keywords from './learn/Keywords';
import './Learn.css';

const Learn = () => {
  const location = useLocation();
  const { theme } = useTheme();

  const isActive = (path) => {
    return location.pathname === path;
  };

  return (
    <div className={`learn-container ${theme === 'dark' ? 'dark-theme' : 'light-theme'}`}>
      <div className="learn-header">
        <h1>Learning Center</h1>
        <p>Comprehensive guide to alpha formula development</p>
      </div>

      <div className="learn-navigation">
        <Link
          to="/learn/documentation"
          className={`learn-nav-item ${isActive('/learn/documentation') ? 'active' : ''}`}
        >
          📖 Documentation
        </Link>
        <Link
          to="/learn/operators"
          className={`learn-nav-item ${isActive('/learn/operators') ? 'active' : ''}`}
        >
          ⚙️ Operators
        </Link>
        <Link
          to="/learn/keywords"
          className={`learn-nav-item ${isActive('/learn/keywords') ? 'active' : ''}`}
        >
          🔑 Keywords
        </Link>
      </div>

      <div className="learn-content">
        <Routes>
          <Route path="/" element={<Documentation theme={theme} />} />
          <Route path="/documentation" element={<Documentation theme={theme} />} />
          <Route path="/operators" element={<Operators theme={theme} />} />
          <Route path="/keywords" element={<Keywords theme={theme} />} />
        </Routes>
      </div>
    </div>
  );
};

export default Learn;