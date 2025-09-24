// API configuration for different environments
const API_CONFIG = {
  development: {
    BASE_URL: 'http://localhost:8000',
  },
  production: {
    BASE_URL: process.env.REACT_APP_API_URL || '',
  }
};

const environment = process.env.NODE_ENV || 'development';
export const API_BASE_URL = API_CONFIG[environment].BASE_URL;

// Helper function to create full API URLs
export const createApiUrl = (endpoint) => {
  if (environment === 'production' && API_BASE_URL) {
    return `${API_BASE_URL}${endpoint}`;
  }
  // In development or when no API_URL is set, use relative URLs (proxy)
  return endpoint;
};

export default {
  BASE_URL: API_BASE_URL,
  createApiUrl,
};