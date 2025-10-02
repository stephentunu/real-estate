/**
 * Appointment Service - API calls for appointment management
 * Connects frontend to Django REST API backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

// Types
export interface AppointmentType {
  id: number;
  name: string;
  description?: string;
  duration_minutes: number;
  is_active: boolean;
}

export interface Agent {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
  profile_image?: string;
}

export interface Client {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  phone?: string;
}

export interface Property {
  id: number;
  title: string;
  address: string;
  city: string;
  state: string;
  primary_image?: string;
}

export interface Appointment {
  id: number;
  title: string;
  description?: string;
  appointment_type: AppointmentType;
  client: Client;
  agent?: Agent;
  property?: Property;
  scheduled_date: string;
  scheduled_time: string;
  duration_minutes: number;
  timezone: string;
  status: 'pending' | 'confirmed' | 'cancelled' | 'completed' | 'rescheduled' | 'no_show';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  client_phone?: string;
  client_email?: string;
  meeting_location?: string;
  meeting_link?: string;
  agent_notes?: string;
  client_notes?: string;
  completion_notes?: string;
  cancelled_at?: string;
  cancelled_by?: Client | Agent;
  cancellation_reason?: string;
  original_appointment?: number;
  reschedule_count: number;
  reminder_sent: boolean;
  reminder_sent_at?: string;
  created_at: string;
  updated_at: string;
  created_by?: Client | Agent;
  updated_by?: Client | Agent;
}

export interface CreateAppointmentData {
  title: string;
  description?: string;
  appointment_type_id: number;
  agent_id?: number;
  property_id?: number;
  scheduled_date: string;
  scheduled_time: string;
  duration_minutes?: number;
  timezone?: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  client_phone?: string;
  client_email?: string;
  meeting_location?: string;
  meeting_link?: string;
  client_notes?: string;
}

export interface UpdateAppointmentData {
  title?: string;
  description?: string;
  scheduled_date?: string;
  scheduled_time?: string;
  duration_minutes?: number;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  client_phone?: string;
  client_email?: string;
  meeting_location?: string;
  meeting_link?: string;
  client_notes?: string;
  agent_notes?: string;
}

export interface AppointmentFilters {
  status?: string;
  appointment_type?: number;
  agent?: number;
  property?: number;
  scheduled_date?: string;
  scheduled_date_after?: string;
  scheduled_date_before?: string;
  priority?: string;
  search?: string;
  ordering?: string;
  [key: string]: string | number | undefined;
}

export interface RescheduleData {
  new_date: string;
  new_time: string;
  reason?: string;
}

export interface CancelData {
  reason?: string;
}

// Helper functions
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    throw new Error(`HTTP error! status: ${response.status}`);
  }
  return await response.json();
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

export const appointmentService = {
  /**
   * Get appointments with optional filters
   */
  getAppointments: async (filters?: AppointmentFilters): Promise<{ results: Appointment[]; count: number; next?: string; previous?: string }> => {
    try {
      const queryString = filters ? buildQueryString(filters) : '';
      const url = `${API_BASE_URL}/appointments/${queryString ? `?${queryString}` : ''}`;
      
      const response = await fetch(url, {
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error fetching appointments:', error);
      throw error;
    }
  },

  /**
   * Get a single appointment by ID
   */
  getAppointment: async (id: number): Promise<Appointment> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/${id}/`, {
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error fetching appointment:', error);
      throw error;
    }
  },

  /**
   * Create a new appointment
   */
  createAppointment: async (data: CreateAppointmentData): Promise<Appointment> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error creating appointment:', error);
      throw error;
    }
  },

  /**
   * Update an appointment
   */
  updateAppointment: async (id: number, data: UpdateAppointmentData): Promise<Appointment> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/${id}/`, {
        method: 'PATCH',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error updating appointment:', error);
      throw error;
    }
  },

  /**
   * Delete an appointment
   */
  deleteAppointment: async (id: number): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/${id}/`, {
        method: 'DELETE',
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error deleting appointment:', error);
      throw error;
    }
  },

  /**
   * Confirm an appointment
   */
  confirmAppointment: async (id: number): Promise<Appointment> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/${id}/confirm/`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error confirming appointment:', error);
      throw error;
    }
  },

  /**
   * Cancel an appointment
   */
  cancelAppointment: async (id: number, data?: CancelData): Promise<Appointment> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/${id}/cancel/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data || {}),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error cancelling appointment:', error);
      throw error;
    }
  },

  /**
   * Reschedule an appointment
   */
  rescheduleAppointment: async (id: number, data: RescheduleData): Promise<Appointment> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/${id}/reschedule/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify(data),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error rescheduling appointment:', error);
      throw error;
    }
  },

  /**
   * Complete an appointment
   */
  completeAppointment: async (id: number, notes?: string): Promise<Appointment> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/${id}/complete/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({ completion_notes: notes || '' }),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error completing appointment:', error);
      throw error;
    }
  },

  /**
   * Get appointment types
   */
  getAppointmentTypes: async (): Promise<AppointmentType[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/types/`, {
        headers: getAuthHeaders(),
      });
      
      const data = await handleResponse(response);
      return data.results || data;
    } catch (error) {
      console.error('Error fetching appointment types:', error);
      throw error;
    }
  },

  /**
   * Get user's appointments (client perspective)
   */
  getUserAppointments: async (filters?: AppointmentFilters): Promise<Appointment[]> => {
    try {
      const queryString = filters ? buildQueryString(filters) : '';
      const url = `${API_BASE_URL}/appointments/my-appointments/${queryString ? `?${queryString}` : ''}`;
      
      const response = await fetch(url, {
        headers: getAuthHeaders(),
      });
      
      const data = await handleResponse(response);
      return data.results || data;
    } catch (error) {
      console.error('Error fetching user appointments:', error);
      throw error;
    }
  },

  /**
   * Get appointment statistics
   */
  getAppointmentStats: async (): Promise<{
    total_appointments: number;
    confirmed_appointments: number;
    pending_appointments: number;
    cancelled_appointments: number;
    completed_appointments: number;
    today_appointments: number;
    upcoming_appointments: number;
  }> => {
    try {
      const response = await fetch(`${API_BASE_URL}/appointments/stats/`, {
        headers: getAuthHeaders(),
      });
      
      return await handleResponse(response);
    } catch (error) {
      console.error('Error fetching appointment stats:', error);
      throw error;
    }
  },
};

export default appointmentService;