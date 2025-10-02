/**
 * Feature Service - API calls for feature management
 * Connects frontend to Django REST API backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types
export interface Feature {
  id: number;
  name: string;
  display_name: string;
  description: string;
  is_active: boolean;
  configuration: Record<string, unknown>;
  user_roles: string[];
  created_at: string;
  updated_at: string;
}

export interface UserFeatureAccess {
  id: number;
  user: number;
  feature: Feature;
  is_enabled: boolean;
  configuration: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

// Helper functions
const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Network error' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }
  return response.json();
};

export const featureService = {
  /**
   * Get all active features for current user's role
   */
  getFeatures: async (): Promise<Feature[]> => {
    const response = await fetch(`${API_BASE_URL}/features/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Get user's feature access settings
   */
  getUserFeatures: async (): Promise<UserFeatureAccess[]> => {
    const response = await fetch(`${API_BASE_URL}/user-features/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Update user feature access
   */
  updateUserFeature: async (featureId: number, data: { is_enabled: boolean; configuration?: Record<string, unknown> }): Promise<UserFeatureAccess> => {
    const response = await fetch(`${API_BASE_URL}/user-features/${featureId}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Check if user has access to a specific feature
   */
  hasFeatureAccess: async (featureName: string): Promise<boolean> => {
    try {
      const response = await fetch(`${API_BASE_URL}/features/check-access/?feature=${featureName}`, {
        headers: getAuthHeaders(),
      });
      const result = await handleResponse(response);
      return result.has_access;
    } catch (error) {
      console.error('Error checking feature access:', error);
      return false;
    }
  },
};

export default featureService;