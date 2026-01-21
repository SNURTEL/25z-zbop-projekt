// useAuth hook

import { useContext } from 'react';
import { AuthContext, AuthContextType } from '../context/AuthContext';
import { UserRole } from '../types';

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  
  return context;
};

// Helper hooks for role checking
export const useIsRole = (role: UserRole): boolean => {
  const { user } = useAuth();
  return user?.role === role;
};

export const useIsUser = (): boolean => {
  return useIsRole('user');
};

export const useIsVendor = (): boolean => {
  return useIsRole('vendor');
};

// Check if user has at least one of the specified roles
export const useHasAnyRole = (roles: UserRole[]): boolean => {
  const { user } = useAuth();
  return user ? roles.includes(user.role) : false;
};
