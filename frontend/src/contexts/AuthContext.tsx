/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useEffect, useState } from 'react';
import { authService, User, AuthResponse, UserProfile } from '@/services/authService';
import { AuthContextType } from './auth-types';

export const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check for existing authentication token
    const initializeAuth = async () => {
      const token = localStorage.getItem('auth_token');
      if (token) {
        try {
          const userProfile = await authService.getCurrentUser();
          setUser(userProfile.user);
          setProfile(userProfile.profile);
        } catch (error) {
          // Token might be expired, clear it
          localStorage.removeItem('auth_token');
          console.error('Error fetching profile:', error);
        }
      }
      setLoading(false);
    };

    initializeAuth();
  }, []);

  const fetchProfile = async () => {
    try {
      const userProfile = await authService.getCurrentUser();
      setUser(userProfile.user);
      setProfile(userProfile.profile);
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const signUp = async (email: string, password: string, firstName?: string, lastName?: string): Promise<AuthResponse> => {
    const response = await authService.register({
      email,
      password,
      password_confirm: password,
      first_name: firstName || '',
      last_name: lastName || ''
    });
    
    if (response.token) {
      localStorage.setItem('auth_token', response.token);
      setUser(response.user);
      setProfile(response.profile);
    }
    
    return response;
  };

  const signIn = async (email: string, password: string): Promise<AuthResponse> => {
    const response = await authService.login({ email, password });
    
    if (response.token) {
      localStorage.setItem('auth_token', response.token);
      setUser(response.user);
      setProfile(response.profile);
    }
    
    return response;
  };

  const signOut = async () => {
    try {
      await authService.logout();
      localStorage.removeItem('auth_token');
      setUser(null);
      setProfile(null);
    } catch (error) {
      console.error('Error signing out:', error);
      // Clear local state even if logout fails
      localStorage.removeItem('auth_token');
      setUser(null);
      setProfile(null);
    }
  };

  const updateProfile = async (updates: Partial<UserProfile>) => {
    if (!user) throw new Error('No user logged in');

    await authService.updateProfile(updates);
    // Refresh profile
    await fetchProfile();
  };

  const value = {
    user,
    profile,
    loading,
    signUp,
    signIn,
    signOut,
    updateProfile,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};