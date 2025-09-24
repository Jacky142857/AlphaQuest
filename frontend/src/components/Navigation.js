import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth } from '../contexts/AuthContext';
import './Navigation.css';

const Navigation = () => {
  const location = useLocation();
  const { isDarkMode, toggleTheme } = useTheme();
  const { user, isGuest, openLoginModal, logout } = useAuth();

  const isActive = (path) => {
    if (path === '/simulate') {
      return location.pathname === '/' || location.pathname === '/simulate';
    }
    return location.pathname.startsWith(path);
  };

  const handleAuthAction = () => {
    if (isGuest) {
      openLoginModal();
    } else {
      logout();
    }
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
        <Link
          to="/my-alphas"
          className={`nav-link ${isActive('/my-alphas') ? 'active' : ''}`}
        >
          💼 My Alphas
        </Link>
        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          aria-label={`Switch to ${isDarkMode ? 'light' : 'dark'} mode`}
        >
          {isDarkMode ? '☀️' : '🌙'}
        </button>
        <button
          className="auth-btn"
          onClick={handleAuthAction}
          title={isGuest ? 'Sign In' : `Sign Out (${user?.username})`}
        >
          {isGuest ? '👤 Sign In' : '🚪 Sign Out'}
        </button>
      </div>
    </nav>
  );
};

export default Navigation;