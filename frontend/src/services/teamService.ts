/**
 * Team Service - API calls for team members and departments
 * Connects frontend to Django REST API backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types
export interface TeamDepartment {
  id: number;
  name: string;
  description?: string;
  color?: string;
  is_visible: boolean;
  created_at: string;
  updated_at: string;
}

export interface TeamMember {
  id: number;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  position: string;
  department?: TeamDepartment;
  bio?: string;
  profile_image?: string;
  linkedin_url?: string;
  twitter_url?: string;
  facebook_url?: string;
  is_active: boolean;
  is_featured: boolean;
  is_visible: boolean;
  display_order: number;
  hire_date?: string;
  created_at: string;
  updated_at: string;
}

export interface TeamMemberListItem {
  id: number;
  first_name: string;
  last_name: string;
  position: string;
  department?: {
    id: number;
    name: string;
    color?: string;
  };
  profile_image?: string;
  linkedin_url?: string;
  twitter_url?: string;
  facebook_url?: string;
  is_featured: boolean;
  display_order: number;
}

export interface TeamAchievement {
  id: number;
  title: string;
  description?: string;
  date_achieved: string;
  category: string;
  is_visible: boolean;
  member: number;
  created_at: string;
  updated_at: string;
}

export interface TeamFilters {
  [key: string]: string | number | boolean | undefined; // Add index signature for compatibility
  department?: number;
  position?: string;
  is_active?: boolean;
  is_featured?: boolean;
  search?: string;
  ordering?: string;
}

export interface PaginatedTeamResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: TeamMemberListItem[];
}

export interface TeamStats {
  total_members: number;
  active_members: number;
  inactive_members: number;
  featured_members: number;
  departments_count: number;
  achievements_count: number;
  positions_breakdown: Record<string, number>;
  departments_breakdown: Record<string, number>;
}

// Helper functions
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` }),
  };
};

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || errorData.message || 'API request failed');
  }
  return response.json();
};

const buildQueryString = (params: Record<string, string | number | boolean | undefined>): string => {
  const searchParams = new URLSearchParams();
  
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value.toString());
    }
  });
  
  return searchParams.toString();
};

// API Functions
export const teamService = {
  /**
   * Get all team members with optional filtering
   */
  getTeamMembers: async (filters?: TeamFilters): Promise<PaginatedTeamResponse> => {
    try {
      const queryString = filters ? buildQueryString(filters) : '';
      const url = `${API_BASE_URL}/team/members/${queryString ? `?${queryString}` : ''}`;
      
      const response = await fetch(url, {
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error fetching team members:', error);
      throw error;
    }
  },

  /**
   * Get a single team member by ID
   */
  getTeamMember: async (id: number): Promise<TeamMember> => {
    try {
      const response = await fetch(`${API_BASE_URL}/team/members/${id}/`, {
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error fetching team member:', error);
      throw error;
    }
  },

  /**
   * Get featured team members
   */
  getFeaturedTeamMembers: async (): Promise<TeamMemberListItem[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/team/members/featured/`, {
        headers: getAuthHeaders(),
      });
      
      const data = await handleResponse(response);
      return data.results || data;
    } catch (error) {
      console.error('Error fetching featured team members:', error);
      throw error;
    }
  },

  /**
   * Get leadership team members
   */
  getLeadershipTeam: async (): Promise<TeamMemberListItem[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/team/members/leadership/`, {
        headers: getAuthHeaders(),
      });
      
      const data = await handleResponse(response);
      return data.results || data;
    } catch (error) {
      console.error('Error fetching leadership team:', error);
      throw error;
    }
  },

  /**
   * Get team members grouped by department
   */
  getTeamByDepartment: async (): Promise<Array<{
    department: TeamDepartment;
    members: TeamMemberListItem[];
  }>> => {
    try {
      const response = await fetch(`${API_BASE_URL}/team/members/by-department/`, {
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error fetching team by department:', error);
      throw error;
    }
  },

  /**
   * Get all departments
   */
  getDepartments: async (): Promise<TeamDepartment[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/team/departments/`, {
        headers: getAuthHeaders(),
      });
      
      const data = await handleResponse(response);
      return data.results || data;
    } catch (error) {
      console.error('Error fetching departments:', error);
      throw error;
    }
  },

  /**
   * Get team statistics
   */
  getTeamStats: async (): Promise<TeamStats> => {
    try {
      const response = await fetch(`${API_BASE_URL}/team/members/stats/`, {
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error fetching team stats:', error);
      throw error;
    }
  },

  /**
   * Get achievements for a team member
   */
  getMemberAchievements: async (memberId: number): Promise<TeamAchievement[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/team/members/${memberId}/achievements/`, {
        headers: getAuthHeaders(),
      });
      
      const data = await handleResponse(response);
      return data.results || data;
    } catch (error) {
      console.error('Error fetching member achievements:', error);
      throw error;
    }
  },
};

export default teamService;