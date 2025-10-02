/**
 * Unified API Client for Django REST API backend
 * Provides consistent request handling with proper authentication and error handling
 */

import { handleError, retryRequest } from '../utils/errorHandler';
import { APIValidationError, APIError, NetworkError, AuthenticationError } from './errors';
import { healthService } from './healthService';

// API Configuration
const API_CONFIG = {
  baseURL: 'http://localhost:8000/api/v1',
  timeout: 30000,
  retries: 3,
  retryDelay: 1000,
};

export interface APIResponse<T = unknown> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}

export interface RequestConfig {
  [key: string]: unknown; // Add index signature for compatibility
  headers?: Record<string, string>;
  params?: Record<string, unknown>;
  timeout?: number;
  responseType?: 'json' | 'blob' | 'text';
  retry?: boolean;
  retryCount?: number;
  retryDelay?: number;
  requiresAuth?: boolean;
}

/**
 * Interceptor types
 */
interface RequestInterceptor {
  (config: RequestConfig): RequestConfig | Promise<RequestConfig>;
}

interface ResponseInterceptor {
  (response: APIResponse<unknown>): APIResponse<unknown> | Promise<APIResponse<unknown>>;
}

interface ErrorInterceptor {
  (error: unknown): unknown | Promise<unknown>;
}

/**
 * API Client class with proper type safety
 */
class APIClient {
  private baseURL: string;
  private timeout: number;
  private retries: number;
  private retryDelay: number;
  private requestInterceptors: RequestInterceptor[] = [];
  private responseInterceptors: ResponseInterceptor[] = [];
  private errorInterceptors: ErrorInterceptor[] = [];

  constructor(config: typeof API_CONFIG) {
    this.baseURL = config.baseURL;
    this.timeout = config.timeout;
    this.retries = config.retries;
    this.retryDelay = config.retryDelay;
  }

  /**
   * Interceptor management
   */
  public interceptors = {
    request: {
      use: (interceptor: RequestInterceptor) => {
        this.requestInterceptors.push(interceptor);
      },
    },
    response: {
      use: (onFulfilled?: ResponseInterceptor, onRejected?: ErrorInterceptor) => {
        if (onFulfilled) this.responseInterceptors.push(onFulfilled);
        if (onRejected) this.errorInterceptors.push(onRejected);
      },
    },
  };

  /**
   * Build full URL from endpoint
   */
  private buildURL(endpoint: string): string {
    return `${this.baseURL}${endpoint.startsWith('/') ? endpoint : `/${endpoint}`}`;
  }

  /**
   * Get authentication headers
   */
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };

    const token = this.getAuthToken();
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const csrfToken = this.getCSRFToken();
    if (csrfToken) {
      headers['X-CSRFToken'] = csrfToken;
    }

    return headers;
  }

  /**
   * Get CSRF token from cookies
   */
  private getCSRFToken(): string | null {
    const cookies = document.cookie.split(';');
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split('=');
      if (name === 'csrftoken') {
        return decodeURIComponent(value);
      }
    }
    return null;
  }

  /**
   * Build query string from parameters
   */
  private buildQueryString(params?: Record<string, unknown>): string {
    if (!params || Object.keys(params).length === 0) {
      return '';
    }

    const searchParams = new URLSearchParams();
    Object.entries(params).forEach(([key, value]) => {
      if (value !== null && value !== undefined) {
        searchParams.append(key, String(value));
      }
    });

    return searchParams.toString();
  }

  /**
   * Handle response parsing with proper type safety
   */
  private async handleResponse(response: Response): Promise<unknown> {
    const contentType = response.headers.get('content-type') || '';
    
    if (!response.ok) {
      let errorData: unknown;
      
      try {
        if (contentType.includes('application/json')) {
          errorData = await response.json();
        } else {
          errorData = { message: await response.text() };
        }
      } catch {
        errorData = { message: `HTTP ${response.status}: ${response.statusText}` };
      }

      // Handle different error types
      if (response.status === 401) {
        throw new AuthenticationError(
          'Authentication required',
          response.status,
          errorData as Record<string, unknown>
        );
      } else if (response.status === 400) {
        throw new APIValidationError(
          'Validation failed',
          {},
          response.status
        );
      } else {
        throw new APIError(
          `Request failed with status ${response.status}`,
          response.status,
          'API_ERROR',
          errorData as Record<string, unknown>
        );
      }
    }

    // Parse successful response
    if (contentType.includes('application/json')) {
      return await response.json();
    } else if (contentType.includes('text/')) {
      return await response.text();
    } else {
      return await response.blob();
    }
  }

  /**
   * Apply request interceptors
   */
  private async applyRequestInterceptors(config: RequestConfig): Promise<RequestConfig> {
    let processedConfig = config;
    
    for (const interceptor of this.requestInterceptors) {
      processedConfig = await interceptor(processedConfig);
    }
    
    return processedConfig;
  }

  /**
   * Apply response interceptors
   */
  private async applyResponseInterceptors(response: APIResponse<unknown>): Promise<APIResponse<unknown>> {
    let modifiedResponse = response;
    
    for (const interceptor of this.responseInterceptors) {
      modifiedResponse = await interceptor(modifiedResponse);
    }
    
    return modifiedResponse;
  }

  /**
   * Make HTTP request with interceptors
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: unknown,
    config?: RequestConfig
  ): Promise<T> {
    try {
      // Check backend health before making any API calls
      const isHealthy = await healthService.isBackendHealthy();
      if (!isHealthy) {
        throw new APIError(
          'Backend is not healthy. Request cancelled to prevent failures.',
          503,
          'BACKEND_UNHEALTHY',
          { healthStatus: 'unhealthy' }
        );
      }

      // Apply request interceptors
      const processedConfig = await this.applyRequestInterceptors(config || {});
      
      const url = this.buildURL(endpoint);
      const headers = { ...this.getAuthHeaders(), ...processedConfig.headers };
      
      // Handle FormData and other body types
      let body: BodyInit | null = null;
      if (data instanceof FormData) {
        // Remove Content-Type header for FormData to let browser set boundary
        delete headers['Content-Type'];
        body = data;
      } else if (data && typeof data === 'object') {
        body = JSON.stringify(data);
      } else if (typeof data === 'string') {
        body = data;
      }

      // Build query string for GET requests
      let finalUrl = url;
      if (method === 'GET' && processedConfig.params) {
        const queryString = this.buildQueryString(processedConfig.params);
        finalUrl += (queryString ? `?${queryString}` : '');
      }

      const fetchOptions: RequestInit = {
        method,
        headers,
        body: method !== 'GET' ? body : undefined,
      };

      // Add timeout using AbortController
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), processedConfig.timeout || this.timeout);
      
      fetchOptions.signal = controller.signal;

      const response = await fetch(finalUrl, fetchOptions);
      clearTimeout(timeoutId);

      const responseData = await this.handleResponse(response);
      const apiResponse: APIResponse<unknown> = {
        data: responseData,
        status: response.status,
        statusText: response.statusText,
        headers: Object.fromEntries(response.headers.entries()),
      };

      // Apply response interceptors
      const processedResponse = await this.applyResponseInterceptors(apiResponse);
      
      return processedResponse.data as T;
    } catch (error) {
      // Apply error interceptors
      let processedError = error;
      for (const interceptor of this.errorInterceptors) {
        const result = interceptor(processedError);
        // Handle both sync and async interceptors
        if (result && typeof result === 'object' && 'then' in result && typeof result.then === 'function') {
          const awaitedResult = await result;
          if (awaitedResult !== undefined) {
            processedError = awaitedResult;
          }
        } else if (result !== undefined) {
          processedError = result;
        }
        // If result is undefined, keep the original processedError
      }
      throw processedError;
    }
  }

  /**
   * GET request
   */
  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    const requestFn = () => this.request<T>('GET', endpoint, undefined, config);
    
    if (config?.retry !== false) {
      return retryRequest(requestFn, {
        retries: config?.retryCount || this.retries,
        delay: config?.retryDelay || this.retryDelay,
      });
    }
    
    return requestFn();
  }

  /**
   * POST request
   */
  async post<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>('POST', endpoint, data, config);
  }

  /**
   * PUT request
   */
  async put<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>('PUT', endpoint, data, config);
  }

  /**
   * PATCH request
   */
  async patch<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>('PATCH', endpoint, data, config);
  }

  /**
   * DELETE request
   */
  async delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>('DELETE', endpoint, undefined, config);
  }

  /**
   * Upload file
   */
  async upload<T>(endpoint: string, file: File, fieldName: string = 'file', additionalData?: Record<string, unknown>): Promise<T> {
    const formData = new FormData();
    formData.append(fieldName, file);
    
    if (additionalData) {
      Object.entries(additionalData).forEach(([key, value]) => {
        if (value instanceof Blob) {
          formData.append(key, value);
        } else {
          formData.append(key, String(value));
        }
      });
    }

    return this.post<T>(endpoint, formData);
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string | null): void {
    if (token) {
      localStorage.setItem('auth_token', token);
    } else {
      localStorage.removeItem('auth_token');
    }
  }

  /**
   * Set authentication token (alias for setAuthToken)
   */
  setToken(token: string): void {
    this.setAuthToken(token);
  }

  /**
   * Get authentication token
   */
  getAuthToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }

  /**
   * Clear authentication
   */
  clearAuth(): void {
    localStorage.removeItem('auth_token');
  }

  /**
   * Remove authentication token (alias for clearAuth)
   */
  removeToken(): void {
    this.clearAuth();
  }

  /**
   * Get API configuration
   */
  getConfig(): {
    baseURL: string;
    timeout: number;
    retries: number;
    retryDelay: number;
  } {
    return {
      baseURL: this.baseURL,
      timeout: this.timeout,
      retries: this.retries,
      retryDelay: this.retryDelay,
    };
  }
}

// Create singleton instance
const apiClient = new APIClient(API_CONFIG);

// Initialize interceptors when the module is imported
// Use dynamic import to avoid circular dependency
import('./interceptors.ts').then(({ setupInterceptors }) => {
  setupInterceptors(apiClient);
}).catch(error => {
  console.warn('Failed to setup interceptors:', error);
});

export default apiClient;