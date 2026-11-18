import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '../types';
import { authApi } from '../api';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (data: { email: string; password: string; full_name: string; target_role?: string; language_preference?: string }) => Promise<void>;
  logout: () => void;
  updateUser: (updated: Partial<User>) => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('smarthire_token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const initAuth = async () => {
      const savedToken = localStorage.getItem('smarthire_token');
      if (savedToken) {
        try {
          const res = await authApi.getMe();
          setUser(res.data);
        } catch (e) {
          localStorage.removeItem('smarthire_token');
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };
    initAuth();
  }, []);

  const login = async (email: string, password: string) => {
    const res = await authApi.login({ email, password });
    const { access_token, user } = res.data;
    localStorage.setItem('smarthire_token', access_token);
    setToken(access_token);
    setUser(user);
  };

  const register = async (data: { email: string; password: string; full_name: string; target_role?: string; language_preference?: string }) => {
    const res = await authApi.register(data);
    const { access_token, user } = res.data;
    localStorage.setItem('smarthire_token', access_token);
    setToken(access_token);
    setUser(user);
  };

  const logout = () => {
    localStorage.removeItem('smarthire_token');
    setToken(null);
    setUser(null);
    window.location.href = '/login';
  };

  const updateUser = (updated: Partial<User>) => {
    if (user) {
      setUser({ ...user, ...updated });
    }
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, updateUser, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
