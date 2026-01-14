// Authentication Context

import React, { createContext, useState, useEffect, useCallback, ReactNode } from 'react';
import { authService } from '../services/auth';
import { UserResponse, UserLogin, UserRegister } from '../types';

export interface AuthContextType {
  user: UserResponse | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: UserLogin) => Promise<void>;
  register: (userData: UserRegister) => Promise<void>;
  logout: () => void;
  refreshUser: () => Promise<void>;
}

export const AuthContext = createContext<AuthContextType | null>(null);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = useCallback(async () => {
    if (!authService.isAuthenticated()) {
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      const userData = await authService.getCurrentUser();
      setUser(userData);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      setUser(null);
      authService.logout();
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshUser();
  }, [refreshUser]);

  const login = async (credentials: UserLogin): Promise<void> => {
    setIsLoading(true);
    try {
      await authService.login(credentials);
      await refreshUser();
    } catch (error) {
      setIsLoading(false);
      throw error;
    }
  };

  const register = async (userData: UserRegister): Promise<void> => {
    await authService.register(userData);
    // After registration, user needs to login
  };

  const logout = useCallback(() => {
    authService.logout();
    setUser(null);
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    register,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};
