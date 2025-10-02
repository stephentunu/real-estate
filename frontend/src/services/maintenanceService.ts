/**
 * Maintenance Service - API calls for maintenance request management
 * Connects frontend to Django REST API backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types
export interface MaintenanceRequest {
  id: number;
  request_number: string;
  property_ref: {
    id: number;
    title: string;
    address: string;
  };
  tenant?: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    email: string;
  };
  landlord: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  title: string;
  description: string;
  category: 'plumbing' | 'electrical' | 'hvac' | 'appliance' | 'structural' | 'cosmetic' | 'security' | 'other';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  status: 'submitted' | 'acknowledged' | 'in_progress' | 'completed' | 'cancelled';
  urgency_level: number;
  location_details?: string;
  access_instructions?: string;
  preferred_contact_method: 'email' | 'phone' | 'sms' | 'app';
  tenant_available_times?: string;
  photos?: string[];
  estimated_cost?: string;
  actual_cost?: string;
  completion_notes?: string;
  tenant_satisfaction_rating?: number;
  tenant_feedback?: string;
  created_at: string;
  updated_at: string;
  scheduled_date?: string;
  completed_date?: string;
}

export interface WorkOrder {
  id: number;
  work_order_number: string;
  maintenance_request: number;
  contractor?: {
    id: number;
    name: string;
    email: string;
    phone: string;
    specialties: string[];
  };
  assigned_to?: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  title: string;
  description: string;
  status: 'created' | 'assigned' | 'in_progress' | 'completed' | 'cancelled';
  priority: 'low' | 'medium' | 'high' | 'urgent';
  estimated_hours?: number;
  actual_hours?: number;
  estimated_cost?: string;
  actual_cost?: string;
  materials_needed?: string;
  materials_cost?: string;
  scheduled_start_date?: string;
  scheduled_end_date?: string;
  actual_start_date?: string;
  actual_completion_date?: string;
  work_performed?: string;
  quality_rating?: number;
  notes?: string;
  photos_before?: string[];
  photos_after?: string[];
  created_at: string;
  updated_at: string;
}

export interface Contractor {
  id: number;
  name: string;
  company_name?: string;
  email: string;
  phone: string;
  address?: string;
  license_number?: string;
  insurance_info?: string;
  specialties: string[];
  hourly_rate?: string;
  availability_schedule?: string;
  rating?: number;
  total_jobs_completed?: number;
  is_active: boolean;
  emergency_contact: boolean;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface MaintenanceListItem {
  id: number;
  request_number: string;
  property_title: string;
  tenant_name?: string;
  title: string;
  category: string;
  priority: string;
  status: string;
  created_at: string;
  scheduled_date?: string;
}

export interface CreateMaintenanceRequestData {
  property_ref: number;
  tenant?: number;
  title: string;
  description: string;
  category: string;
  priority: string;
  location_details?: string;
  access_instructions?: string;
  preferred_contact_method: string;
  tenant_available_times?: string;
  photos?: File[];
}

export interface UpdateMaintenanceRequestData {
  title?: string;
  description?: string;
  category?: string;
  priority?: string;
  status?: string;
  location_details?: string;
  access_instructions?: string;
  preferred_contact_method?: string;
  tenant_available_times?: string;
  estimated_cost?: string;
  actual_cost?: string;
  completion_notes?: string;
  tenant_satisfaction_rating?: number;
  tenant_feedback?: string;
  scheduled_date?: string;
  completed_date?: string;
}

export interface CreateWorkOrderData {
  maintenance_request: number;
  contractor?: number;
  assigned_to?: number;
  title: string;
  description: string;
  priority: string;
  estimated_hours?: number;
  estimated_cost?: string;
  materials_needed?: string;
  materials_cost?: string;
  scheduled_start_date?: string;
  scheduled_end_date?: string;
  notes?: string;
}

export interface UpdateWorkOrderData {
  contractor?: number;
  assigned_to?: number;
  title?: string;
  description?: string;
  status?: string;
  priority?: string;
  estimated_hours?: number;
  actual_hours?: number;
  estimated_cost?: string;
  actual_cost?: string;
  materials_needed?: string;
  materials_cost?: string;
  scheduled_start_date?: string;
  scheduled_end_date?: string;
  actual_start_date?: string;
  actual_completion_date?: string;
  work_performed?: string;
  quality_rating?: number;
  notes?: string;
}

export interface CreateContractorData {
  name: string;
  company_name?: string;
  email: string;
  phone: string;
  address?: string;
  license_number?: string;
  insurance_info?: string;
  specialties: string[];
  hourly_rate?: string;
  availability_schedule?: string;
  emergency_contact?: boolean;
  notes?: string;
}

export interface UpdateContractorData {
  name?: string;
  company_name?: string;
  email?: string;
  phone?: string;
  address?: string;
  license_number?: string;
  insurance_info?: string;
  specialties?: string[];
  hourly_rate?: string;
  availability_schedule?: string;
  is_active?: boolean;
  emergency_contact?: boolean;
  notes?: string;
}

// Helper functions
const getAuthHeaders = () => {
  const token = localStorage.getItem('authToken');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Bearer ${token}` })
  };
};

const getMultipartHeaders = () => {
  const token = localStorage.getItem('authToken');
  return {
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

export const maintenanceService = {
  // Maintenance Request Methods
  /**
   * Get all maintenance requests with optional filtering
   */
  getMaintenanceRequests: async (params?: {
    status?: string;
    category?: string;
    priority?: string;
    property_ref?: number;
    tenant?: number;
    search?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: MaintenanceListItem[]; count: number; next?: string; previous?: string }> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Get maintenance request by ID
   */
  getMaintenanceRequest: async (id: number): Promise<MaintenanceRequest> => {
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/${id}/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Create new maintenance request
   */
  createMaintenanceRequest: async (data: CreateMaintenanceRequestData): Promise<MaintenanceRequest> => {
    const formData = new FormData();
    
    // Add text fields
    Object.entries(data).forEach(([key, value]) => {
      if (key !== 'photos' && value !== undefined && value !== null) {
        formData.append(key, value.toString());
      }
    });
    
    // Add photos if any
    if (data.photos && data.photos.length > 0) {
      data.photos.forEach((photo, index) => {
        formData.append(`photos`, photo);
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/`, {
      method: 'POST',
      headers: getMultipartHeaders(),
      body: formData,
    });
    return handleResponse(response);
  },

  /**
   * Update maintenance request
   */
  updateMaintenanceRequest: async (id: number, data: UpdateMaintenanceRequestData): Promise<MaintenanceRequest> => {
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Delete maintenance request
   */
  deleteMaintenanceRequest: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
  },

  /**
   * Acknowledge maintenance request
   */
  acknowledgeMaintenanceRequest: async (id: number, data?: { notes?: string; estimated_cost?: string }): Promise<MaintenanceRequest> => {
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/${id}/acknowledge/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data || {}),
    });
    return handleResponse(response);
  },

  /**
   * Complete maintenance request
   */
  completeMaintenanceRequest: async (id: number, data: { completion_notes?: string; actual_cost?: string }): Promise<MaintenanceRequest> => {
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/${id}/complete/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Cancel maintenance request
   */
  cancelMaintenanceRequest: async (id: number, data?: { reason?: string }): Promise<MaintenanceRequest> => {
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/${id}/cancel/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data || {}),
    });
    return handleResponse(response);
  },

  /**
   * Upload photos to maintenance request
   */
  uploadMaintenancePhotos: async (id: number, photos: File[]): Promise<MaintenanceRequest> => {
    const formData = new FormData();
    photos.forEach((photo) => {
      formData.append('photos', photo);
    });
    
    const response = await fetch(`${API_BASE_URL}/maintenance-requests/${id}/upload_photos/`, {
      method: 'POST',
      headers: getMultipartHeaders(),
      body: formData,
    });
    return handleResponse(response);
  },

  // Work Order Methods
  /**
   * Get all work orders with optional filtering
   */
  getWorkOrders: async (params?: {
    maintenance_request?: number;
    contractor?: number;
    assigned_to?: number;
    status?: string;
    priority?: string;
    search?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: WorkOrder[]; count: number; next?: string; previous?: string }> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/work-orders/?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Get work order by ID
   */
  getWorkOrder: async (id: number): Promise<WorkOrder> => {
    const response = await fetch(`${API_BASE_URL}/work-orders/${id}/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Create new work order
   */
  createWorkOrder: async (data: CreateWorkOrderData): Promise<WorkOrder> => {
    const response = await fetch(`${API_BASE_URL}/work-orders/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Update work order
   */
  updateWorkOrder: async (id: number, data: UpdateWorkOrderData): Promise<WorkOrder> => {
    const response = await fetch(`${API_BASE_URL}/work-orders/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Delete work order
   */
  deleteWorkOrder: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/work-orders/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
  },

  /**
   * Assign work order to contractor
   */
  assignWorkOrder: async (id: number, data: { contractor?: number; assigned_to?: number }): Promise<WorkOrder> => {
    const response = await fetch(`${API_BASE_URL}/work-orders/${id}/assign/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Start work order
   */
  startWorkOrder: async (id: number): Promise<WorkOrder> => {
    const response = await fetch(`${API_BASE_URL}/work-orders/${id}/start/`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Complete work order
   */
  completeWorkOrder: async (id: number, data: {
    work_performed: string;
    actual_hours?: number;
    actual_cost?: string;
    materials_cost?: string;
    quality_rating?: number;
    notes?: string;
  }): Promise<WorkOrder> => {
    const response = await fetch(`${API_BASE_URL}/work-orders/${id}/complete/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Upload before/after photos to work order
   */
  uploadWorkOrderPhotos: async (id: number, photos: File[], type: 'before' | 'after'): Promise<WorkOrder> => {
    const formData = new FormData();
    photos.forEach((photo) => {
      formData.append(`photos_${type}`, photo);
    });
    
    const response = await fetch(`${API_BASE_URL}/work-orders/${id}/upload_photos/`, {
      method: 'POST',
      headers: getMultipartHeaders(),
      body: formData,
    });
    return handleResponse(response);
  },

  // Contractor Methods
  /**
   * Get all contractors with optional filtering
   */
  getContractors: async (params?: {
    specialties?: string;
    is_active?: boolean;
    emergency_contact?: boolean;
    search?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: Contractor[]; count: number; next?: string; previous?: string }> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/contractors/?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Get contractor by ID
   */
  getContractor: async (id: number): Promise<Contractor> => {
    const response = await fetch(`${API_BASE_URL}/contractors/${id}/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Create new contractor
   */
  createContractor: async (data: CreateContractorData): Promise<Contractor> => {
    const response = await fetch(`${API_BASE_URL}/contractors/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Update contractor
   */
  updateContractor: async (id: number, data: UpdateContractorData): Promise<Contractor> => {
    const response = await fetch(`${API_BASE_URL}/contractors/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Delete contractor
   */
  deleteContractor: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/contractors/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
  },

  /**
   * Get contractor performance analytics
   */
  getContractorAnalytics: async (id: number): Promise<Record<string, unknown>> => {
    const response = await fetch(`${API_BASE_URL}/contractors/${id}/analytics/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Get maintenance analytics
   */
  getMaintenanceAnalytics: async (params?: {
    property_ref?: number;
    date_from?: string;
    date_to?: string;
    category?: string;
  }): Promise<Record<string, unknown>> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/maintenance-analytics/?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },
};

export default maintenanceService;