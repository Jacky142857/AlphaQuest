// frontend/src/contexts/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useNotification } from './NotificationContext';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isGuest, setIsGuest] = useState(true);
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const { showNotification } = useNotification();

  // Load authentication state from localStorage on mount
  useEffect(() => {
    const savedAuth = localStorage.getItem('alpha_quest_auth');
    if (savedAuth) {
      try {
        const authData = JSON.parse(savedAuth);
        if (authData.user) {
          setUser(authData.user);
          setIsGuest(false);
        }
      } catch (error) {
        console.error('Error loading auth data:', error);
        localStorage.removeItem('alpha_quest_auth');
      }
    }
  }, []);

  // Save authentication state to localStorage
  const saveAuthState = (userData) => {
    const authData = {
      user: userData,
      timestamp: Date.now(),
    };
    localStorage.setItem('alpha_quest_auth', JSON.stringify(authData));
  };

  const login = (username, password) => {
    // Simple authentication (later replace with real backend)
    if (username && password.length >= 6) {
      const userData = {
        id: `user_${Date.now()}`,
        username: username,
        email: `${username}@example.com`,
        createdAt: new Date().toISOString(),
        alphas: [],
      };

      setUser(userData);
      setIsGuest(false);
      saveAuthState(userData);
      setIsLoginModalOpen(false);

      showNotification(`Welcome back, ${username}! You can now save your alpha strategies.`, 'success', 5000);
      return { success: true };
    } else {
      return { success: false, error: 'Username is required and password must be at least 6 characters' };
    }
  };

  const register = (username, email, password, confirmPassword) => {
    // Simple registration validation
    if (!username || !email || !password) {
      return { success: false, error: 'All fields are required' };
    }

    if (password !== confirmPassword) {
      return { success: false, error: 'Passwords do not match' };
    }

    if (password.length < 6) {
      return { success: false, error: 'Password must be at least 6 characters' };
    }

    if (!email.includes('@')) {
      return { success: false, error: 'Please enter a valid email address' };
    }

    // Check if user already exists (simple localStorage check)
    const existingUsers = JSON.parse(localStorage.getItem('alpha_quest_users') || '[]');
    if (existingUsers.some(u => u.username === username || u.email === email)) {
      return { success: false, error: 'Username or email already exists' };
    }

    const userData = {
      id: `user_${Date.now()}`,
      username: username,
      email: email,
      createdAt: new Date().toISOString(),
      alphas: [],
    };

    // Save to users list
    existingUsers.push(userData);
    localStorage.setItem('alpha_quest_users', JSON.stringify(existingUsers));

    // Set as current user
    setUser(userData);
    setIsGuest(false);
    saveAuthState(userData);
    setIsLoginModalOpen(false);

    showNotification(`Account created successfully! Welcome, ${username}!`, 'success', 5000);
    return { success: true };
  };

  const logout = () => {
    setUser(null);
    setIsGuest(true);
    localStorage.removeItem('alpha_quest_auth');
    showNotification('Logged out successfully. You are now in guest mode.', 'info', 4000);
  };

  const continueAsGuest = () => {
    setIsGuest(true);
    setIsLoginModalOpen(false);
    showNotification('Continuing as guest. You can view and test alphas but cannot save them.', 'info', 4000);
  };

  const openLoginModal = () => {
    setIsLoginModalOpen(true);
  };

  const closeLoginModal = () => {
    setIsLoginModalOpen(false);
  };

  const saveAlpha = (alphaData) => {
    if (isGuest || !user) {
      showNotification('Please login to save your alpha strategies.', 'warning', 5000);
      return false;
    }

    const newAlpha = {
      id: `alpha_${Date.now()}`,
      name: alphaData.name || `Alpha ${user.alphas.length + 1}`,
      formula: alphaData.formula,
      settings: alphaData.settings,
      dataSource: alphaData.dataSource,
      dateRange: alphaData.dateRange,
      returns: alphaData.returns,
      metrics: alphaData.metrics,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
    };

    const updatedUser = {
      ...user,
      alphas: [...user.alphas, newAlpha],
    };

    setUser(updatedUser);
    saveAuthState(updatedUser);

    showNotification(`Alpha "${newAlpha.name}" saved successfully!`, 'success', 4000);
    return true;
  };

  const deleteAlpha = (alphaId) => {
    if (isGuest || !user) {
      return false;
    }

    const updatedUser = {
      ...user,
      alphas: user.alphas.filter(alpha => alpha.id !== alphaId),
    };

    setUser(updatedUser);
    saveAuthState(updatedUser);

    showNotification('Alpha deleted successfully.', 'success', 3000);
    return true;
  };

  const updateAlpha = (alphaId, updatedData) => {
    if (isGuest || !user) {
      return false;
    }

    const updatedUser = {
      ...user,
      alphas: user.alphas.map(alpha =>
        alpha.id === alphaId
          ? { ...alpha, ...updatedData, updatedAt: new Date().toISOString() }
          : alpha
      ),
    };

    setUser(updatedUser);
    saveAuthState(updatedUser);

    showNotification('Alpha updated successfully.', 'success', 3000);
    return true;
  };

  const value = {
    user,
    isGuest,
    isLoginModalOpen,
    login,
    register,
    logout,
    continueAsGuest,
    openLoginModal,
    closeLoginModal,
    saveAlpha,
    deleteAlpha,
    updateAlpha,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};