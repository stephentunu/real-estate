/**
 * Authentication Service - Tightly coupled with Django REST API backend
 * Uses unified API client for consistent request handling
 */

import apiClient, { PaginatedResponse } from './apiClient';
export { APIValidationError } from './errors';

// Type definitions matching backend models
export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  date_joined: string;
  last_login?: string;
}

export interface UserProfile {
  id: number;
  user: User;
  phone_number?: string;
  address?: string;
  city?: string;
  state?: string;
  zip_code?: string;
  country?: string;
  date_of_birth?: string;
  bio?: string;
  avatar?: string;
  user_role: 'tenant' | 'landlord' | 'property_manager' | 'admin';
  is_verified: boolean;
  company_name?: string;
  license_number?: string;
  website?: string;
  social_media_links?: Record<string, string>;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  user: User;
  profile: UserProfile;
  token: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  user_role?: 'tenant' | 'landlord' | 'property_manager';
}

export interface PasswordChangeData {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

export interface PasswordResetData {
  email: string;
}

export interface PasswordResetConfirmData {
  uid: string;
  token: string;
  new_password: string;
  new_password_confirm: string;
}

/**
 * Authentication service methods
 */
export const authService = {
  /**
   * Login user with email and password
   */
  // Update login/register endpoints to match Django backend
async login(data: LoginData): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/v1/users/login/', data, {
    requiresAuth: false,
  });
  apiClient.setToken(response.token);
  return response;
},

async register(data: RegisterData): Promise<AuthResponse> {
  const response = await apiClient.post<AuthResponse>('/api/v1/users/register/', data, {
    requiresAuth: false,
  });
  apiClient.setToken(response.token);
  return response;
},


  /**
   * Logout user and clear authentication
   */
  async logout(): Promise<void> {
    try {
      await apiClient.post('/users/logout/', {});
    } finally {
      // Always remove token on logout
      apiClient.removeToken();
    }
  },

  /**
   * Get current authenticated user profile
   */
  async getCurrentUser(): Promise<{ user: User; profile: UserProfile }> {
    return apiClient.get('/users/me/');
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return apiClient.patch('/users/profiles/me/', data);
  },

  /**
   * Change user password
   */
  async changePassword(data: PasswordChangeData): Promise<{ message: string }> {
    return apiClient.post('/users/change-password/', data);
  },

  /**
   * Request password reset
   */
  async requestPasswordReset(data: PasswordResetData): Promise<{ message: string }> {
    return apiClient.post('/users/password-reset/', data, {
      requiresAuth: false,
    });
  },

  /**
   * Confirm password reset
   */
  async confirmPasswordReset(data: PasswordResetConfirmData): Promise<{ message: string }> {
    return apiClient.post('/users/password-reset-confirm/', data, {
      requiresAuth: false,
    });
  },

  /**
   * Refresh authentication token
   */
  async refreshToken(): Promise<{ token: string }> {
    const response = await apiClient.post<{ access: string }>('/users/token/refresh/', {});
    apiClient.setToken(response.access);
    return { token: response.access };
  },

  /**
   * Verify authentication token
   */
  async verifyToken(): Promise<{ valid: boolean }> {
    return apiClient.get('/users/token/verify/');
  },

  /**
   * Get user list (admin only)
   */
  async getUsers(params?: {
    search?: string;
    role?: string;
    is_active?: boolean;
    page?: number;
  }): Promise<PaginatedResponse<User>> {
    return apiClient.get('/users/list/', { params });
  },

  /**
   * Get specific user by ID
   */
  async getUser(id: number): Promise<User> {
    return apiClient.get(`/users/${id}/`);
  },

  /**
   * Update user (admin only)
   */
  async updateUser(id: number, data: Partial<User>): Promise<User> {
    return apiClient.patch(`/users/${id}/`, data);
  },

  /**
   * Delete user (admin only)
   */
  async deleteUser(id: number): Promise<void> {
    return apiClient.delete(`/users/${id}/`);
  },
};

/**
 * User profile service methods
 */
export const userProfileService = {
  /**
   * Get current user profile
   */
  async getCurrentProfile(): Promise<UserProfile> {
    return apiClient.get('/users/profiles/me/');
  },

  /**
   * Update current user profile
   */
  async updateCurrentProfile(data: Partial<UserProfile>): Promise<UserProfile> {
    return apiClient.patch('/users/profiles/me/', data);
  },

  /**
   * Upload profile avatar
   */
  async uploadAvatar(file: File): Promise<{ avatar: string }> {
    const formData = new FormData();
    formData.append('avatar', file);
    
    return apiClient.post('/users/profiles/avatar/', formData, {
      headers: {
        'Content-Type': undefined, // Let browser set content-type
      },
    });
  },

  /**
   * Get user profile by ID
   */
  async getProfile(id: number): Promise<UserProfile> {
    return apiClient.get(`/users/profiles/${id}/`);
  },

  /**
   * Get all user profiles with pagination
   */
  async getProfiles(params?: {
    search?: string;
    role?: string;
    is_verified?: boolean;
    page?: number;
  }): Promise<PaginatedResponse<UserProfile>> {
    return apiClient.get('/users/profiles/', { params });
  },
};

export default authService;