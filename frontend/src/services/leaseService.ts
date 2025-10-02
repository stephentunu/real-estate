/**
 * Lease Service - API calls for lease management
 * Connects frontend to Django REST API backend
 */

const API_BASE_URL = 'http://localhost:8000/api';

// Types
export interface LeaseTerms {
  id: number;
  lease_duration_months: number;
  rent_amount: string;
  security_deposit: string;
  late_fee_amount?: string;
  grace_period_days?: number;
  rent_due_day: number;
  lease_start_date: string;
  lease_end_date: string;
  auto_renewal: boolean;
  renewal_notice_days?: number;
  pet_policy?: string;
  smoking_policy?: string;
  maintenance_responsibility?: string;
  utilities_included?: string;
  parking_included: boolean;
  additional_terms?: string;
  created_at: string;
  updated_at: string;
}

export interface PaymentSchedule {
  id: number;
  lease: number;
  payment_type: 'rent' | 'deposit' | 'fee' | 'utility' | 'other';
  amount: string;
  due_date: string;
  is_paid: boolean;
  paid_date?: string;
  payment_method?: string;
  reference_number?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface Lease {
  id: number;
  lease_number: string;
  property_ref: {
    id: number;
    title: string;
    address: string;
  };
  tenant: {
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
  terms: LeaseTerms;
  status: 'draft' | 'active' | 'expired' | 'terminated' | 'renewed';
  signed_date?: string;
  move_in_date?: string;
  move_out_date?: string;
  termination_date?: string;
  termination_reason?: string;
  renewal_lease?: number;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaseListItem {
  id: number;
  lease_number: string;
  property_title: string;
  tenant_name: string;
  status: string;
  rent_amount: string;
  lease_start_date: string;
  lease_end_date: string;
  created_at: string;
}

export interface CreateLeaseData {
  property_ref: number;
  tenant: number;
  terms: Omit<LeaseTerms, 'id' | 'created_at' | 'updated_at'>;
  signed_date?: string;
  move_in_date?: string;
  notes?: string;
}

export interface UpdateLeaseData {
  status?: string;
  signed_date?: string;
  move_in_date?: string;
  move_out_date?: string;
  termination_date?: string;
  termination_reason?: string;
  notes?: string;
}

export interface CreatePaymentScheduleData {
  lease: number;
  payment_type: string;
  amount: string;
  due_date: string;
  notes?: string;
}

export interface UpdatePaymentScheduleData {
  is_paid?: boolean;
  paid_date?: string;
  payment_method?: string;
  reference_number?: string;
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

const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: 'Network error' }));
    throw new Error(error.message || `HTTP ${response.status}`);
  }
  return response.json();
};

export const leaseService = {
  /**
   * Get all leases with optional filtering
   */
  getLeases: async (params?: {
    status?: string;
    property_ref?: number;
    tenant?: number;
    search?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: LeaseListItem[]; count: number; next?: string; previous?: string }> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/leases/?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Get lease by ID
   */
  getLease: async (id: number): Promise<Lease> => {
    const response = await fetch(`${API_BASE_URL}/leases/${id}/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Create new lease
   */
  createLease: async (data: CreateLeaseData): Promise<Lease> => {
    const response = await fetch(`${API_BASE_URL}/leases/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Update lease
   */
  updateLease: async (id: number, data: UpdateLeaseData): Promise<Lease> => {
    const response = await fetch(`${API_BASE_URL}/leases/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Delete lease
   */
  deleteLease: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/leases/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
  },

  /**
   * Generate lease document
   */
  generateLeaseDocument: async (id: number): Promise<Blob> => {
    const response = await fetch(`${API_BASE_URL}/leases/${id}/generate_document/`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
    return response.blob();
  },

  /**
   * Renew lease
   */
  renewLease: async (id: number, data: { new_terms?: Partial<LeaseTerms>; notes?: string }): Promise<Lease> => {
    const response = await fetch(`${API_BASE_URL}/leases/${id}/renew/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Terminate lease
   */
  terminateLease: async (id: number, data: { termination_date: string; reason?: string }): Promise<Lease> => {
    const response = await fetch(`${API_BASE_URL}/leases/${id}/terminate/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Get lease analytics
   */
  getLeaseAnalytics: async (id: number): Promise<Record<string, unknown>> => {
    const response = await fetch(`${API_BASE_URL}/leases/${id}/analytics/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  // Payment Schedule Methods
  /**
   * Get payment schedules for a lease
   */
  getPaymentSchedules: async (params?: {
    lease?: number;
    payment_type?: string;
    is_paid?: boolean;
    due_date_after?: string;
    due_date_before?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: PaymentSchedule[]; count: number; next?: string; previous?: string }> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/payment-schedules/?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Get payment schedule by ID
   */
  getPaymentSchedule: async (id: number): Promise<PaymentSchedule> => {
    const response = await fetch(`${API_BASE_URL}/payment-schedules/${id}/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Create payment schedule
   */
  createPaymentSchedule: async (data: CreatePaymentScheduleData): Promise<PaymentSchedule> => {
    const response = await fetch(`${API_BASE_URL}/payment-schedules/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Update payment schedule
   */
  updatePaymentSchedule: async (id: number, data: UpdatePaymentScheduleData): Promise<PaymentSchedule> => {
    const response = await fetch(`${API_BASE_URL}/payment-schedules/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Delete payment schedule
   */
  deletePaymentSchedule: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/payment-schedules/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
  },

  /**
   * Mark payment as paid
   */
  markPaymentAsPaid: async (id: number, data: { payment_method?: string; reference_number?: string }): Promise<PaymentSchedule> => {
    const response = await fetch(`${API_BASE_URL}/payment-schedules/${id}/mark_paid/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Generate payment receipt
   */
  generatePaymentReceipt: async (id: number): Promise<Blob> => {
    const response = await fetch(`${API_BASE_URL}/payment-schedules/${id}/generate_receipt/`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
    return response.blob();
  },

  // Lease Terms Methods
  /**
   * Get lease terms
   */
  getLeaseTerms: async (params?: {
    lease_duration_months?: number;
    rent_amount_min?: string;
    rent_amount_max?: string;
    ordering?: string;
    page?: number;
  }): Promise<{ results: LeaseTerms[]; count: number; next?: string; previous?: string }> => {
    const queryParams = new URLSearchParams();
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== null) {
          queryParams.append(key, value.toString());
        }
      });
    }
    
    const response = await fetch(`${API_BASE_URL}/lease-terms/?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Get lease terms by ID
   */
  getLeaseTermsById: async (id: number): Promise<LeaseTerms> => {
    const response = await fetch(`${API_BASE_URL}/lease-terms/${id}/`, {
      headers: getAuthHeaders(),
    });
    return handleResponse(response);
  },

  /**
   * Create lease terms
   */
  createLeaseTerms: async (data: Omit<LeaseTerms, 'id' | 'created_at' | 'updated_at'>): Promise<LeaseTerms> => {
    const response = await fetch(`${API_BASE_URL}/lease-terms/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Update lease terms
   */
  updateLeaseTerms: async (id: number, data: Partial<LeaseTerms>): Promise<LeaseTerms> => {
    const response = await fetch(`${API_BASE_URL}/lease-terms/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });
    return handleResponse(response);
  },

  /**
   * Delete lease terms
   */
  deleteLeaseTerms: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/lease-terms/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'Network error' }));
      throw new Error(error.message || `HTTP ${response.status}`);
    }
  },
};

export default leaseService;