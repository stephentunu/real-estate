/**
 * City Service - Tightly coupled with Django REST API backend
 * Uses unified API client for consistent request handling
 */

import apiClient, { PaginatedResponse } from './apiClient';

// Type definitions matching backend models
export interface City {
  id: number;
  name: string;
  country: string;
  country_code: string;
  region: string;
  latitude: number;
  longitude: number;
  timezone: string;
  population?: number;
  elevation?: number;
  is_capital: boolean;
  is_featured: boolean;
  description?: string;
  images: string[];
  tags: string[];
  nearby_cities: CityListItem[];
  created_at: string;
  updated_at: string;
}

export interface CityListItem {
  id: number;
  name: string;
  country: string;
  country_code: string;
  region: string;
  latitude: number;
  longitude: number;
  timezone: string;
  population?: number;
  elevation?: number;
  is_capital: boolean;
  is_featured: boolean;
  description?: string;
  images: string[];
  tags: string[];
}

export interface CityFilters {
  country?: string;
  region?: string;
  is_capital?: boolean;
  is_featured?: boolean;
  search?: string;
  min_population?: number;
  max_population?: number;
  ordering?: string;
  page?: number;
  limit?: number;
}

export interface NearbyCityQuery {
  latitude: number;
  longitude: number;
  radius?: number; // in kilometers
  limit?: number;
}

export interface CitySearchResult {
  city: CityListItem;
  distance?: number;
}

export interface CreateCityData {
  name: string;
  country: string;
  country_code: string;
  region: string;
  latitude: number;
  longitude: number;
  timezone: string;
  population?: number;
  elevation?: number;
  is_capital?: boolean;
  is_featured?: boolean;
  description?: string;
  images?: string[];
  tags?: string[];
}

export interface UpdateCityData {
  name?: string;
  region?: string;
  latitude?: number;
  longitude?: number;
  timezone?: string;
  population?: number;
  elevation?: number;
  is_capital?: boolean;
  is_featured?: boolean;
  description?: string;
  images?: string[];
  tags?: string[];
}

/**
 * City service methods
 */
export const cityService = {
  /**
   * Get all cities with optional filters
   */
  async getCities(filters?: CityFilters): Promise<PaginatedResponse<CityListItem>> {
    return apiClient.get('/cities/', { params: filters });
  },

  /**
   * Get a specific city by ID
   */
  async getCity(id: number): Promise<City> {
    return apiClient.get(`/cities/${id}/`);
  },

  /**
   * Get featured cities
   */
  async getFeaturedCities(limit?: number): Promise<CityListItem[]> {
    return apiClient.get('/cities/featured/', { params: { limit } });
  },

  /**
   * Get capital cities
   */
  async getCapitalCities(limit?: number): Promise<CityListItem[]> {
    return apiClient.get('/cities/capitals/', { params: { limit } });
  },

  /**
   * Get nearby cities based on coordinates
   */
  async getNearbyCities(query: NearbyCityQuery): Promise<CitySearchResult[]> {
    return apiClient.get('/cities/nearby/', { params: query });
  },

  /**
   * Search cities by coordinates (reverse geocoding)
   */
  async searchCitiesByCoordinates(latitude: number, longitude: number): Promise<CitySearchResult[]> {
    return apiClient.get('/cities/search-by-coordinates/', { params: { latitude, longitude } });
  },

  /**
   * Search cities by name
   */
  async searchCities(query: string, filters?: Omit<CityFilters, 'search'>): Promise<PaginatedResponse<CityListItem>> {
    return this.getCities({ search: query, ...filters });
  },

  /**
   * Get cities by country
   */
  async getCitiesByCountry(countryCode: string, filters?: Omit<CityFilters, 'country'>): Promise<PaginatedResponse<CityListItem>> {
    return this.getCities({ country: countryCode, ...filters });
  },

  /**
   * Get cities by region
   */
  async getCitiesByRegion(region: string, filters?: Omit<CityFilters, 'region'>): Promise<PaginatedResponse<CityListItem>> {
    return this.getCities({ region, ...filters });
  },

  /**
   * Create new city
   */
  async createCity(data: CreateCityData): Promise<City> {
    return apiClient.post('/cities/', data);
  },

  /**
   * Update city
   */
  async updateCity(id: number, data: UpdateCityData): Promise<City> {
    return apiClient.patch(`/cities/${id}/`, data);
  },

  /**
   * Delete city
   */
  async deleteCity(id: number): Promise<void> {
    return apiClient.delete(`/cities/${id}/`);
  },

  /**
   * Get city statistics
   */
  async getCityStats(): Promise<{
    total_cities: number;
    capital_cities: number;
    featured_cities: number;
    countries_count: number;
    total_population: number;
  }> {
    return apiClient.get('/cities/stats/');
  },

  /**
   * Get popular cities
   */
  async getPopularCities(limit?: number): Promise<CityListItem[]> {
    return apiClient.get('/cities/popular/', { params: { limit } });
  },

  /**
   * Get random cities
   */
  async getRandomCities(limit?: number): Promise<CityListItem[]> {
    return apiClient.get('/cities/random/', { params: { limit } });
  },

  /**
   * Get cities by timezone
   */
  async getCitiesByTimezone(timezone: string): Promise<CityListItem[]> {
    return apiClient.get('/cities/timezone/', { params: { timezone } });
  },

  /**
   * Get cities within bounding box
   */
  async getCitiesInBoundingBox(
    minLat: number,
    minLng: number,
    maxLat: number,
    maxLng: number,
    limit?: number
  ): Promise<CityListItem[]> {
    return apiClient.get('/cities/bounding-box/', {
      params: {
        min_lat: minLat,
        min_lng: minLng,
        max_lat: maxLat,
        max_lng: maxLng,
        limit,
      },
    });
  },

  /**
   * Get distance between two cities
   */
  async getDistanceBetweenCities(fromCityId: number, toCityId: number): Promise<{
    distance: number;
    from_city: CityListItem;
    to_city: CityListItem;
  }> {
    return apiClient.get(`/cities/${fromCityId}/distance/${toCityId}/`);
  },

  /**
   * Get city suggestions for autocomplete
   */
  async getCitySuggestions(query: string, limit?: number): Promise<CityListItem[]> {
    return apiClient.get('/cities/suggestions/', { params: { q: query, limit } });
  },

  /**
   * Bulk create cities
   */
  async bulkCreateCities(cities: CreateCityData[]): Promise<CityListItem[]> {
    return apiClient.post('/cities/bulk-create/', { cities });
  },

  /**
   * Export cities data
   */
  async exportCities(format: 'json' | 'csv' | 'xlsx' = 'json'): Promise<Blob> {
    return apiClient.get('/cities/export/', {
      params: { format },
      responseType: 'blob',
    });
  },

  /**
   * Import cities from file
   */
  async importCities(file: File): Promise<{
    imported: number;
    skipped: number;
    errors: string[];
  }> {
    const formData = new FormData();
    formData.append('file', file);
    
    return apiClient.post('/cities/import/', formData, {
      headers: {
        'Content-Type': undefined,
      },
    });
  },
};

export default cityService;