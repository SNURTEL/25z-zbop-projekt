// Authentication Service

import { api } from './api';
import { API_CONFIG, API_ENDPOINTS } from '../config/api';
import { Cookies } from '../utils/cookies';
import { 
  UserLogin, 
  UserRegister, 
  UserResponse, 
  TokenResponse 
} from '../types';

export const authService = {
  /**
   * Login user and store token in cookie
   */
  async login(credentials: UserLogin): Promise<TokenResponse> {
    const response = await api.post<TokenResponse>(
      API_ENDPOINTS.AUTH.LOGIN,
      credentials,
      { skipAuth: true }
    );
    
    // Store token in cookie
    const expiresIn = response.expires_in || 1800; // Default 30 minutes
    Cookies.set(API_CONFIG.TOKEN_COOKIE_NAME, response.access_token, {
      expires: expiresIn,
      path: '/',
      sameSite: 'Lax',
    });
    
    // Store expiry time for reference
    const expiryTime = new Date(Date.now() + expiresIn * 1000);
    Cookies.set(API_CONFIG.TOKEN_EXPIRY_COOKIE_NAME, expiryTime.toISOString(), {
      expires: expiresIn,
      path: '/',
      sameSite: 'Lax',
    });
    
    return response;
  },

  /**
   * Register new user
   */
  async register(userData: UserRegister): Promise<UserResponse> {
    return api.post<UserResponse>(
      API_ENDPOINTS.AUTH.REGISTER,
      userData,
      { skipAuth: true }
    );
  },

  /**
   * Get current logged in user
   */
  async getCurrentUser(): Promise<UserResponse> {
    return api.get<UserResponse>(API_ENDPOINTS.AUTH.ME);
  },

  /**
   * Logout user - remove token from cookie
   */
  logout(): void {
    Cookies.remove(API_CONFIG.TOKEN_COOKIE_NAME);
    Cookies.remove(API_CONFIG.TOKEN_EXPIRY_COOKIE_NAME);
  },

  /**
   * Check if user is authenticated (has valid token)
   */
  isAuthenticated(): boolean {
    const token = Cookies.get(API_CONFIG.TOKEN_COOKIE_NAME);
    if (!token) return false;
    
    // Check if token is expired
    const expiry = Cookies.get(API_CONFIG.TOKEN_EXPIRY_COOKIE_NAME);
    if (expiry) {
      const expiryDate = new Date(expiry);
      if (expiryDate < new Date()) {
        this.logout();
        return false;
      }
    }
    
    return true;
  },

  /**
   * Get stored token
   */
  getToken(): string | null {
    return Cookies.get(API_CONFIG.TOKEN_COOKIE_NAME);
  },
};
