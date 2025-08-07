import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { authApi } from '@/lib/api';
import api from '@/lib/api';
import { UserResponse } from '@/types/api';

interface AuthContextType {
  user: UserResponse | null;
  token: string | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string, firstName: string, lastName?: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserResponse | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user && !!token;

  // Initialize auth state from localStorage
  useEffect(() => {
    console.log('AuthContext: Initializing auth state...');
    
    // Check both token keys for backward compatibility
    const authToken = localStorage.getItem('auth_token');
    const accessToken = localStorage.getItem('access_token');
    const savedToken = authToken || accessToken;
    
    console.log('AuthContext: Found tokens:', { authToken: !!authToken, accessToken: !!accessToken, savedToken: !!savedToken });
    
    if (savedToken) {
      console.log('AuthContext: Setting token and fetching user data...');
      setToken(savedToken);
      // Set the token in axios defaults immediately
      api.defaults.headers.common['Authorization'] = `Bearer ${savedToken}`;
      
      // Standardize to auth_token and remove old access_token if exists
      localStorage.setItem('auth_token', savedToken);
      if (accessToken) {
        localStorage.removeItem('access_token');
      }
      
      // Verify token and fetch user data
      fetchUserData(savedToken);
    } else {
      console.log('AuthContext: No token found, setting loading false');
      setIsLoading(false);
    }
  }, []);

  const fetchUserData = async (authToken: string) => {
    try {
      console.log('AuthContext: Fetching user data with token...');
      setIsLoading(true);
      
      // Add timeout to prevent infinite loading
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('API timeout')), 10000)
      );
      
      const userData = await Promise.race([
        authApi.me(),
        timeoutPromise
      ]);
      
      console.log('AuthContext: User data fetched successfully:', userData);
      setUser(userData as any);
    } catch (error: any) {
      console.error('AuthContext: Failed to fetch user data:', error);
      // Token might be expired or invalid, clear it
      if (error.response?.status === 401 || error.message === 'API timeout') {
        console.log('AuthContext: Token invalid or timeout, logging out...');
        logout();
      }
    } finally {
      console.log('AuthContext: Setting loading to false');
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await authApi.login(email, password);
      
      const { access_token } = response;
      setToken(access_token);
      localStorage.setItem('auth_token', access_token);
      
      // Set the token in axios defaults
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Fetch user data
      await fetchUserData(access_token);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (email: string, password: string, firstName: string, lastName?: string) => {
    try {
      setIsLoading(true);
      await authApi.register(email, password, firstName, lastName);
      
      // Auto-login after registration
      await login(email, password);
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('access_token'); // Remove both token types
    localStorage.removeItem('selectedClientId'); // Clear selected client as well
    
    // Clear the authorization header
    delete api.defaults.headers.common['Authorization'];
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}