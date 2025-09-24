// frontend/src/contexts/AuthContext.js
import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
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
  const [loading, setLoading] = useState(true);
  const { showNotification } = useNotification();

  // Check authentication status on mount
  useEffect(() => {
    const checkAuthStatus = async () => {
      try {
        const response = await axios.get('/api/auth/user/', {
          withCredentials: true
        });

        if (response.data.user) {
          setUser(response.data.user);
          setIsGuest(false);
        }
      } catch (error) {
        // User is not authenticated or session expired
        setUser(null);
        setIsGuest(true);
      } finally {
        setLoading(false);
      }
    };

    checkAuthStatus();
  }, []);

  const login = async (username, password) => {
    try {
      const response = await axios.post('/api/auth/login/', {
        username,
        password
      }, {
        withCredentials: true
      });

      if (response.data.user) {
        setUser(response.data.user);
        setIsGuest(false);
        setIsLoginModalOpen(false);
        showNotification(`Welcome back, ${username}! You can now save your alpha strategies.`, 'success', 5000);
        return { success: true };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Login failed';
      return { success: false, error: errorMessage };
    }
  };

  const register = async (username, email, password, confirmPassword) => {
    try {
      const response = await axios.post('/api/auth/register/', {
        username,
        email,
        password,
        confirm_password: confirmPassword
      }, {
        withCredentials: true
      });

      if (response.data.user) {
        setUser(response.data.user);
        setIsGuest(false);
        setIsLoginModalOpen(false);
        showNotification(`Account created successfully! Welcome, ${username}!`, 'success', 5000);
        return { success: true };
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error ||
                           Object.values(error.response?.data || {}).flat().join(', ') ||
                           'Registration failed';
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/auth/logout/', {}, {
        withCredentials: true
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsGuest(true);
      showNotification('Logged out successfully. You are now in guest mode.', 'info', 4000);
    }
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

  const saveAlpha = async (alphaData) => {
    if (isGuest || !user) {
      showNotification('Please login to save your alpha strategies.', 'warning', 5000);
      return false;
    }

    try {
      const response = await axios.post('/api/alphas/save/', {
        name: alphaData.name || `Alpha ${user.alphas?.length + 1 || 1}`,
        formula: alphaData.formula,
        settings: alphaData.settings,
        dataSource: alphaData.dataSource,
        dateRange: alphaData.dateRange,
        returns: alphaData.returns,
        metrics: alphaData.metrics
      }, {
        withCredentials: true
      });

      if (response.data.alpha) {
        // Update user state with new alpha
        const updatedUser = {
          ...user,
          alphas: [...(user.alphas || []), response.data.alpha]
        };
        setUser(updatedUser);

        showNotification(`Alpha "${response.data.alpha.name}" saved successfully!`, 'success', 4000);
        return true;
      }
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to save alpha';
      showNotification(errorMessage, 'error', 5000);
      return false;
    }
  };

  const deleteAlpha = async (alphaId) => {
    if (isGuest || !user) {
      return false;
    }

    try {
      await axios.delete(`/api/alphas/${alphaId}/delete/`, {
        withCredentials: true
      });

      // Update user state by removing the alpha
      const updatedUser = {
        ...user,
        alphas: user.alphas.filter(alpha => alpha.id !== alphaId)
      };
      setUser(updatedUser);

      showNotification('Alpha deleted successfully.', 'success', 3000);
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to delete alpha';
      showNotification(errorMessage, 'error', 5000);
      return false;
    }
  };

  const updateAlpha = async (alphaId, updatedData) => {
    if (isGuest || !user) {
      return false;
    }

    try {
      await axios.put(`/api/alphas/${alphaId}/update/`, updatedData, {
        withCredentials: true
      });

      // Update user state
      const updatedUser = {
        ...user,
        alphas: user.alphas.map(alpha =>
          alpha.id === alphaId
            ? { ...alpha, ...updatedData, updated_at: new Date().toISOString() }
            : alpha
        )
      };
      setUser(updatedUser);

      showNotification('Alpha updated successfully.', 'success', 3000);
      return true;
    } catch (error) {
      const errorMessage = error.response?.data?.error || 'Failed to update alpha';
      showNotification(errorMessage, 'error', 5000);
      return false;
    }
  };

  const value = {
    user,
    isGuest,
    loading,
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