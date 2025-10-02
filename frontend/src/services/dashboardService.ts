/**
 * Dashboard Service - API calls for dashboard data
 * Connects frontend to Django REST API backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

// Types
export interface DashboardStats {
  totalProperties: number;
  totalViews: number;
  savedProperties: number;
  upcomingAppointments: number;
}

export interface RecentProperty {
  id: string;
  title: string;
  location: string;
  price: string;
  views: number;
  status: string;
}

export interface DashboardData {
  user: {
    name: string;
    email: string;
  };
  stats: DashboardStats;
  recentProperties: RecentProperty[];
}

// API response interfaces
interface PropertyAPIResponse {
  id: number | string;
  title?: string;
  city?: string;
  state?: string;
  price?: string | number;
  views_count?: number;
  status?: {
    name?: string;
  };
}

interface UserAPIResponse {
  first_name?: string;
  last_name?: string;
  email?: string;
}

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Token ${token}` })
  };
};

// Helper function to handle API responses
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || errorData.message || 'API request failed');
  }
  return response.json();
};

// Type guards
function isPropertyAPIResponse(obj: unknown): obj is PropertyAPIResponse {
  return typeof obj === 'object' && obj !== null && 'id' in obj;
}

function isUserAPIResponse(obj: unknown): obj is UserAPIResponse {
  return typeof obj === 'object' && obj !== null;
}

export const dashboardService = {
  /**
   * Get dashboard statistics for current user
   */
  getDashboardStats: async (): Promise<DashboardStats> => {
    try {
      // Get user properties count
      const propertiesResponse = await fetch(`${API_BASE_URL}/properties/my-properties/`, {
        headers: getAuthHeaders(),
      });
      const propertiesData = await handleResponse(propertiesResponse);
      const totalProperties = Array.isArray(propertiesData) ? propertiesData.length : 0;

      // Get total views (sum of all property views)
      let totalViews = 0;
      if (Array.isArray(propertiesData)) {
        totalViews = propertiesData.reduce((sum: number, property: unknown) => {
          if (isPropertyAPIResponse(property) && typeof property.views_count === 'number') {
            return sum + property.views_count;
          }
          return sum;
        }, 0);
      }

      // Get saved properties count
      const savedResponse = await fetch(`${API_BASE_URL}/properties/saved/`, {
        headers: getAuthHeaders(),
      });
      const savedData = await handleResponse(savedResponse);
      const savedProperties = Array.isArray(savedData) ? savedData.length : 0;

      // Get upcoming appointments count
      const appointmentsResponse = await fetch(`${API_BASE_URL}/appointments/upcoming/`, {
        headers: getAuthHeaders(),
      });
      const appointmentsData = await handleResponse(appointmentsResponse);
      const upcomingAppointments = Array.isArray(appointmentsData) ? appointmentsData.length : 0;

      return {
        totalProperties,
        totalViews,
        savedProperties,
        upcomingAppointments
      };
    } catch (error) {
      console.error('Error fetching dashboard stats:', error);
      return {
        totalProperties: 0,
        totalViews: 0,
        savedProperties: 0,
        upcomingAppointments: 0
      };
    }
  },

  /**
   * Get recent properties for current user
   */
  getRecentProperties: async (limit: number = 3): Promise<RecentProperty[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/properties/my-properties/?limit=${limit}`, {
        headers: getAuthHeaders(),
      });
      const properties = await handleResponse(response);
      
      if (!Array.isArray(properties)) {
        return [];
      }

      return properties
        .filter((property: unknown): property is PropertyAPIResponse => isPropertyAPIResponse(property))
        .map((property: PropertyAPIResponse) => ({
          id: String(property.id),
          title: String(property.title || 'Untitled Property'),
          location: `${property.city || 'Unknown'}, ${property.state || 'Unknown'}`,
          price: `KSh ${parseFloat(String(property.price || 0)).toLocaleString()}`,
          views: Number(property.views_count || 0),
          status: property.status?.name || 'Active'
        }));
    } catch (error) {
      console.error('Error fetching recent properties:', error);
      return [];
    }
  },

  /**
   * Get complete dashboard data
   */
  getDashboardData: async (): Promise<DashboardData> => {
    try {
      // Get user info
      const userResponse = await fetch(`${API_BASE_URL}/auth/user/`, {
        headers: getAuthHeaders(),
      });
      const userData = await handleResponse(userResponse);
      
      const user = isUserAPIResponse(userData) ? {
        name: `${userData.first_name || ''} ${userData.last_name || ''}`.trim() || 'User',
        email: userData.email || 'No email'
      } : {
        name: 'User',
        email: 'No email'
      };

      // Get stats and recent properties
      const [stats, recentProperties] = await Promise.all([
        dashboardService.getDashboardStats(),
        dashboardService.getRecentProperties()
      ]);

      return {
        user,
        stats,
        recentProperties
      };
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      throw error;
    }
  }
};

export default dashboardService;