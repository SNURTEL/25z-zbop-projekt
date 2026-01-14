// API Service - HTTP client with authentication support

import { API_CONFIG } from '../config/api';
import { Cookies } from '../utils/cookies';
import { ErrorResponse } from '../types';

export class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public data?: ErrorResponse
  ) {
    super(data?.detail || statusText);
    this.name = 'ApiError';
  }
}

type RequestOptions = {
  headers?: Record<string, string>;
  params?: Record<string, string | number | boolean | undefined>;
  skipAuth?: boolean;
};

const buildUrl = (endpoint: string, params?: Record<string, string | number | boolean | undefined>): string => {
  const url = new URL(endpoint, API_CONFIG.BASE_URL);
  
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }
  
  return url.toString();
};

const getAuthHeaders = (): Record<string, string> => {
  const token = Cookies.get(API_CONFIG.TOKEN_COOKIE_NAME);
  if (token) {
    return { Authorization: `Bearer ${token}` };
  }
  return {};
};

const handleResponse = async <T>(response: Response): Promise<T> => {
  if (!response.ok) {
    let errorData: ErrorResponse | undefined;
    try {
      errorData = await response.json();
    } catch {
      // Response body is not JSON
    }
    
    // Handle 401 - redirect to login
    if (response.status === 401) {
      Cookies.remove(API_CONFIG.TOKEN_COOKIE_NAME);
      Cookies.remove(API_CONFIG.TOKEN_EXPIRY_COOKIE_NAME);
      
      // Only redirect if not already on login page
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    
    throw new ApiError(response.status, response.statusText, errorData);
  }
  
  // Handle empty responses
  if (response.status === 204) {
    return {} as T;
  }
  
  return response.json();
};

const request = async <T>(
  method: string,
  endpoint: string,
  data?: unknown,
  options: RequestOptions = {}
): Promise<T> => {
  const url = buildUrl(endpoint, options.params);
  
  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    ...(!options.skipAuth ? getAuthHeaders() : {}),
    ...options.headers,
  };
  
  const config: RequestInit = {
    method,
    headers,
  };
  
  if (data && method !== 'GET') {
    config.body = JSON.stringify(data);
  }
  
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);
  config.signal = controller.signal;
  
  try {
    const response = await fetch(url, config);
    clearTimeout(timeoutId);
    return handleResponse<T>(response);
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof ApiError) {
      throw error;
    }
    if (error instanceof Error && error.name === 'AbortError') {
      throw new ApiError(408, 'Request Timeout');
    }
    throw new ApiError(0, 'Network Error');
  }
};

export const api = {
  get: <T>(endpoint: string, options?: RequestOptions): Promise<T> => 
    request<T>('GET', endpoint, undefined, options),
    
  post: <T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> => 
    request<T>('POST', endpoint, data, options),
    
  put: <T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> => 
    request<T>('PUT', endpoint, data, options),
    
  patch: <T>(endpoint: string, data?: unknown, options?: RequestOptions): Promise<T> => 
    request<T>('PATCH', endpoint, data, options),
    
  delete: <T>(endpoint: string, options?: RequestOptions): Promise<T> => 
    request<T>('DELETE', endpoint, undefined, options),
};
