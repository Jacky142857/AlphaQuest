// frontend/src/components/LoginModal.js
import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import './LoginModal.css';

const LoginModal = () => {
  const { isLoginModalOpen, closeLoginModal, login, register, continueAsGuest } = useAuth();
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  // Handle escape key to close modal
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === 'Escape' && isLoginModalOpen) {
        closeLoginModal();
      }
    };

    if (isLoginModalOpen) {
      document.addEventListener('keydown', handleEscape);
      document.body.style.overflow = 'hidden';
    }

    return () => {
      document.removeEventListener('keydown', handleEscape);
      document.body.style.overflow = 'unset';
    };
  }, [isLoginModalOpen, closeLoginModal]);

  // Reset form when modal opens/closes or mode changes
  useEffect(() => {
    setFormData({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
    });
    setErrors({});
  }, [isLoginModalOpen, isLogin]);

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value,
    }));
    // Clear error when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: '',
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setErrors({});

    let result;
    if (isLogin) {
      result = login(formData.username, formData.password);
    } else {
      result = register(formData.username, formData.email, formData.password, formData.confirmPassword);
    }

    if (!result.success) {
      setErrors({ general: result.error });
    }

    setIsLoading(false);
  };

  const toggleMode = () => {
    setIsLogin(!isLogin);
  };

  if (!isLoginModalOpen) {
    return null;
  }

  return (
    <div className="login-overlay" onClick={closeLoginModal}>
      <div className="login-modal" onClick={(e) => e.stopPropagation()}>
        <div className="login-header">
          <h3>{isLogin ? 'Sign In' : 'Create Account'}</h3>
          <button className="login-close-btn" onClick={closeLoginModal}>
            ×
          </button>
        </div>

        <div className="login-content">
          <div className="login-description">
            <p>
              {isLogin
                ? 'Sign in to save your alpha strategies and access them later.'
                : 'Create an account to save and manage your alpha strategies.'
              }
            </p>
          </div>

          <form onSubmit={handleSubmit} className="login-form">
            {errors.general && (
              <div className="error-message">
                {errors.general}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="username">Username</label>
              <input
                type="text"
                id="username"
                name="username"
                value={formData.username}
                onChange={handleInputChange}
                placeholder="Enter your username"
                required
                className={errors.username ? 'error' : ''}
              />
              {errors.username && <span className="field-error">{errors.username}</span>}
            </div>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="email">Email</label>
                <input
                  type="email"
                  id="email"
                  name="email"
                  value={formData.email}
                  onChange={handleInputChange}
                  placeholder="Enter your email"
                  required
                  className={errors.email ? 'error' : ''}
                />
                {errors.email && <span className="field-error">{errors.email}</span>}
              </div>
            )}

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleInputChange}
                placeholder="Enter your password"
                required
                className={errors.password ? 'error' : ''}
              />
              {errors.password && <span className="field-error">{errors.password}</span>}
            </div>

            {!isLogin && (
              <div className="form-group">
                <label htmlFor="confirmPassword">Confirm Password</label>
                <input
                  type="password"
                  id="confirmPassword"
                  name="confirmPassword"
                  value={formData.confirmPassword}
                  onChange={handleInputChange}
                  placeholder="Confirm your password"
                  required
                  className={errors.confirmPassword ? 'error' : ''}
                />
                {errors.confirmPassword && <span className="field-error">{errors.confirmPassword}</span>}
              </div>
            )}

            <button
              type="submit"
              className="login-submit-btn"
              disabled={isLoading}
            >
              {isLoading
                ? (isLogin ? 'Signing In...' : 'Creating Account...')
                : (isLogin ? 'Sign In' : 'Create Account')
              }
            </button>
          </form>

          <div className="login-divider">
            <span>or</span>
          </div>

          <button
            className="guest-btn"
            onClick={continueAsGuest}
            disabled={isLoading}
          >
            Continue as Guest
          </button>

          <div className="login-toggle">
            {isLogin ? (
              <p>
                Don't have an account?{' '}
                <button type="button" className="toggle-btn" onClick={toggleMode}>
                  Sign up
                </button>
              </p>
            ) : (
              <p>
                Already have an account?{' '}
                <button type="button" className="toggle-btn" onClick={toggleMode}>
                  Sign in
                </button>
              </p>
            )}
          </div>

          <div className="login-info">
            <h4>Features with Account:</h4>
            <ul>
              <li>✅ Save alpha strategies</li>
              <li>✅ Access saved strategies anytime</li>
              <li>✅ Compare strategy performance</li>
              <li>✅ Export results</li>
            </ul>

            <h4>Guest Mode:</h4>
            <ul>
              <li>✅ Test and simulate alpha strategies</li>
              <li>❌ Cannot save strategies</li>
              <li>❌ No history or comparison features</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginModal;