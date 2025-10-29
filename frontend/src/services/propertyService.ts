/**
 * Property Service - API calls for property management
 * Connects frontend to Django REST API backend
 */

import { 
  APIError, 
  NetworkError, 
  ValidationError, 
  AuthenticationError 
} from './errors'
import { handleAPIError } from './errorHandler'
import { retryFetch } from '../utils/retryUtils'

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types
export interface PropertyType {
  id: number;
  name: string;
  description?: string;
}

export interface PropertyStatus {
  id: number;
  name: string;
  description?: string;
}

export interface PropertyImage {
  id: number;
  image: string;
  caption?: string;
  is_primary: boolean;
  order: number;
}

export interface PropertyFeature {
  id: number;
  name: string;
  description?: string;
  icon?: string;
}

export interface Property {
  id: number;
  title: string;
  description: string;
  property_type: PropertyType;
  status: PropertyStatus;
  price: string;
  bedrooms?: number;
  bathrooms?: number;
  square_feet?: number;
  lot_size?: number;
  year_built?: number;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  latitude?: number;
  longitude?: number;
  owner: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  agent?: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  images: PropertyImage[];
  features: PropertyFeature[];
  is_featured: boolean;
  views_count: number;
  created_at: string;
  updated_at: string;
}

export interface PropertyListItem {
  id: number;
  title: string;
  property_type: PropertyType;
  status: PropertyStatus;
  price: string;
  bedrooms?: number;
  bathrooms?: number;
  square_feet?: number;
  address: string;
  city: string;
  state: string;
  primary_image?: string;
  is_featured: boolean;
  views_count: number;
  created_at: string;
}

export interface CreatePropertyData {
  title: string;
  description: string;
  property_type_id: number;
  price: string;
  bedrooms?: number;
  bathrooms?: number;
  square_feet?: number;
  lot_size?: number;
  year_built?: number;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  country: string;
  latitude?: number;
  longitude?: number;
  agent_id?: number;
  feature_ids?: number[];
}

export interface PropertyFilters {
  [key: string]: string | number | boolean | undefined; // Add index signature for compatibility
  property_type?: number;
  status?: number;
  min_price?: number;
  max_price?: number;
  min_bedrooms?: number;
  max_bedrooms?: number;
  min_bathrooms?: number;
  max_bathrooms?: number;
  min_square_feet?: number;
  max_square_feet?: number;
  city?: string;
  state?: string;
  is_featured?: boolean;
  search?: string;
  ordering?: string;
}

export interface SavedProperty {
  id: number;
  property: PropertyListItem;
  created_at: string;
}

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Token ${token}` })
  };
};

// Helper function to get multipart headers
const getMultipartHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    ...(token && { 'Authorization': `Token ${token}` })
  };
};

// Helper function to handle API responses
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    
    // Create appropriate error type based on status code
    switch (response.status) {
      case 400:
        throw new ValidationError(errorData.detail || 'Invalid request', errorData);
      case 401:
        throw new AuthenticationError(errorData.detail || 'Authentication required');
      case 403:
        throw new APIError(errorData.detail || 'Access denied', response.status);
      case 404:
        throw new APIError(errorData.detail || 'Resource not found', response.status);
      case 429:
        throw new APIError(errorData.detail || 'Too many requests', response.status);
      case 500:
      case 502:
      case 503:
      case 504:
        throw new APIError(errorData.detail || 'Server error', response.status);
      default:
        throw new APIError(errorData.detail || errorData.message || 'API request failed', response.status);
    }
  }
  return response.json();
};

// Helper function to build query string
const buildQueryString = (params: Record<string, unknown>): string => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value.toString());
    }
  });
  return searchParams.toString();
};

export const propertyService = {
  /**
   * Get all properties with optional filters
   */
  getProperties: async (filters?: PropertyFilters): Promise<{ results: PropertyListItem[]; count: number; next?: string; previous?: string }> => {
    const queryString = filters ? buildQueryString(filters) : '';
    const url = `${API_BASE_URL}/properties/${queryString ? `?${queryString}` : ''}`;
    
    const response = await retryFetch(url, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get property by ID
   */
  getProperty: async (id: number): Promise<Property> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/${id}/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Create new property
   */
  createProperty: async (data: CreatePropertyData): Promise<Property> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse(response);
  },

  /**
   * Update property
   */
  updateProperty: async (id: number, data: Partial<CreatePropertyData>): Promise<Property> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse(response);
  },

  /**
   * Delete property
   */
  deleteProperty: async (id: number): Promise<void> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(errorData.detail || errorData.message || 'Failed to delete property');
    }
  },

  /**
   * Upload property images
   */
  uploadPropertyImages: async (propertyId: number, images: File[]): Promise<PropertyImage[]> => {
    const formData = new FormData();
    images.forEach((image, index) => {
      formData.append('images', image);
      formData.append(`captions[${index}]`, '');
      formData.append(`orders[${index}]`, (index + 1).toString());
    });

    const response = await retryFetch(`${API_BASE_URL}/properties/${propertyId}/upload-images/`, {
      method: 'POST',
      headers: getMultipartHeaders(),
      body: formData,
    });

    return handleResponse(response);
  },

  /**
   * Delete property image
   */
  deletePropertyImage: async (propertyId: number, imageId: number): Promise<void> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/${propertyId}/images/${imageId}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(errorData.detail || errorData.message || 'Failed to delete image');
    }
  },

  /**
   * Get property types
   */
  getPropertyTypes: async (): Promise<PropertyType[]> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/types/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get property statuses
   */
  getPropertyStatuses: async (): Promise<PropertyStatus[]> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/statuses/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get property features
   */
  getPropertyFeatures: async (): Promise<PropertyFeature[]> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/features/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Save property to user's saved list
   */
  saveProperty: async (propertyId: number): Promise<SavedProperty> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/${propertyId}/save/`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Remove property from user's saved list
   */
  unsaveProperty: async (propertyId: number): Promise<void> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/${propertyId}/unsave/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(errorData.detail || errorData.message || 'Failed to unsave property');
    }
  },

  /**
   * Get user's saved properties
   */
  getSavedProperties: async (): Promise<SavedProperty[]> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/saved/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get user's properties (for property owners/agents)
   */
  getUserProperties: async (): Promise<PropertyListItem[]> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/my-properties/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get featured properties
   */
  getFeaturedProperties: async (limit?: number): Promise<PropertyListItem[]> => {
    const queryString = limit ? `?limit=${limit}` : '';
    const response = await retryFetch(`${API_BASE_URL}/properties/featured/${queryString}`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Search properties
   */
  searchProperties: async (query: string, filters?: PropertyFilters): Promise<{ results: PropertyListItem[]; count: number }> => {
    const searchFilters = { ...filters, search: query };
    return propertyService.getProperties(searchFilters);
  },

  /**
   * Get property statistics
   */
  getPropertyStats: async (): Promise<{
    total_properties: number;
    available_properties: number;
    sold_properties: number;
    average_price: number;
    properties_by_type: { type: string; count: number }[];
  }> => {
    const response = await retryFetch(`${API_BASE_URL}/properties/stats/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },
};

export default propertyService;