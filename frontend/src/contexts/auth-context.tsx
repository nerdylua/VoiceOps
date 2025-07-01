'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: string;
  name: string;
  type: string;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  login: (userData: User, token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const router = useRouter();

  useEffect(() => {
    // Check for existing authentication on mount
    const token = localStorage.getItem('voiceops_token');
    const userData = localStorage.getItem('voiceops_user');
    const userId = localStorage.getItem('voiceops_user_id');
    const userType = localStorage.getItem('voiceops_user_type');

    if (token && userData && userId && userType) {
      setUser({
        id: userId,
        name: userData,
        type: userType
      });
      setIsAuthenticated(true);
    }
  }, []);

  const login = (userData: User, token: string) => {
    // Store in localStorage
    localStorage.setItem('voiceops_token', token);
    localStorage.setItem('voiceops_user', userData.name);
    localStorage.setItem('voiceops_user_id', userData.id);
    localStorage.setItem('voiceops_user_type', userData.type);
    
    // Set authentication cookies for compatibility
    document.cookie = `voiceops_auth=true; path=/; max-age=${60 * 60 * 24 * 7}`;
    document.cookie = `voiceops_user=${encodeURIComponent(userData.name)}; path=/; max-age=${60 * 60 * 24 * 7}`;
    document.cookie = `voiceops_user_type=${userData.type}; path=/; max-age=${60 * 60 * 24 * 7}`;
    
    setUser(userData);
    setIsAuthenticated(true);
  };

  const logout = () => {
    // Clear localStorage
    localStorage.removeItem('voiceops_token');
    localStorage.removeItem('voiceops_user');
    localStorage.removeItem('voiceops_user_id');
    localStorage.removeItem('voiceops_user_type');
    
    // Clear cookies
    document.cookie = 'voiceops_auth=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
    document.cookie = 'voiceops_user=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
    document.cookie = 'voiceops_user_type=; path=/; expires=Thu, 01 Jan 1970 00:00:01 GMT';
    
    setUser(null);
    setIsAuthenticated(false);
    
    // Redirect to home
    router.push('/');
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, login, logout }}>
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