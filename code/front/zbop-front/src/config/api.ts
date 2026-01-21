// API Configuration

const getApiBaseUrl = (): string => {
  // Check for environment variable first
  if (process.env.REACT_APP_API_URL) {
    return process.env.REACT_APP_API_URL;
  }
  
  // Default to localhost for development
  return 'http://localhost:8000';
};

export const API_CONFIG = {
  BASE_URL: getApiBaseUrl(),
  TIMEOUT: 30000, // 30 seconds
  TOKEN_COOKIE_NAME: 'auth_token',
  TOKEN_EXPIRY_COOKIE_NAME: 'auth_token_expiry',
};

export const API_ENDPOINTS = {
  // Auth
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    ME: '/auth/me',
  },
  // Orders
  ORDERS: {
    LIST: '/orders',
    DETAIL: (id: number) => `/orders/${id}`,
    UPDATE_STATUS: (id: number) => `/orders/${id}/status`,
    CORRECTIONS: (id: number) => `/orders/${id}/corrections`,
  },
  // Optimization
  OPTIMIZATION: {
    CREATE: '/optimization/requests',
    DETAIL: (id: number) => `/optimization/requests/${id}`,
  },
  // Offices
  OFFICES: {
    LIST: '/offices',
    DETAIL: (id: number) => `/offices/${id}`,
  },
  // Settings
  SETTINGS: {
    LIST: '/settings',
    UPDATE: (name: string) => `/settings/${name}`,
  },
  // Legacy
  LEGACY: {
    CREATE_PREDICTIONS_V2: '/create_predictions_v2',
  },
};
