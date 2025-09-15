import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import './Navigation.css';

const Navigation = () => {
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useTheme();

  const isActive = (path) => {
    if (path === '/simulate') {
      return location.pathname === '/' || location.pathname === '/simulate';
    }
    return location.pathname.startsWith(path);
  };

  return (
    <nav className="main-navigation">
      <div className="nav-brand">
        <Link to="/simulate">
          <h1>Trading Signals Alpha Strategy</h1>
        </Link>
      </div>

      <div className="nav-links">
        <Link
          to="/simulate"
          className={`nav-link ${isActive('/simulate') ? 'active' : ''}`}
        >
          📈 Simulate
        </Link>
        <Link
          to="/learn"
          className={`nav-link ${isActive('/learn') ? 'active' : ''}`}
        >
          📚 Learn
        </Link>
        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </button>
      </div>
    </nav>
  );
};

export default Navigation;