/**
 * Request and Response Interceptors for API Communication
 * 
 * Provides authentication token management, error handling, and request/response transformation
 * to ensure seamless integration between frontend and backend services.
 */

import apiClient from './apiClient.js';
import { APIError } from './errors.js';

// Type definitions for interceptors
interface RequestConfig {
  headers?: Record<string, string>;
  method?: string;
  url?: string;
  data?: unknown;
  _retry?: boolean;
  [key: string]: unknown;
}

interface ResponseData {
  data?: unknown;
  status?: number;
  statusText?: string;
  headers?: Record<string, string>;
  config?: RequestConfig;
  [key: string]: unknown;
}

interface ErrorResponse {
  config?: RequestConfig;
  response?: {
    status: number;
    data?: {
      detail?: string;
      message?: string;
      errors?: Record<string, string[]>;
      [key: string]: unknown;
    };
  };
  message?: string;
  [key: string]: unknown;
}

interface QueueItem {
  resolve: (value: string | null) => void;
  reject: (reason: unknown) => void;
}

// Type guards
function isRequestConfig(obj: unknown): obj is RequestConfig {
  return typeof obj === 'object' && obj !== null;
}

function hasResponseProperty(error: unknown): error is { response: { status: number; data?: Record<string, unknown> } } {
  return typeof error === 'object' && error !== null && 'response' in error &&
         typeof (error as Record<string, unknown>).response === 'object' && (error as Record<string, unknown>).response !== null &&
         typeof ((error as Record<string, unknown>).response as Record<string, unknown>).status === 'number';
}

function hasConfigProperty(error: unknown): error is { config: RequestConfig } {
  return typeof error === 'object' && error !== null && 'config' in error &&
         typeof (error as Record<string, unknown>).config === 'object' && (error as Record<string, unknown>).config !== null;
}

// Authentication interceptor
class AuthInterceptor {
  private static instance: AuthInterceptor;
  private isRefreshing = false;
  private failedQueue: QueueItem[] = [];

  static getInstance(): AuthInterceptor {
    if (!AuthInterceptor.instance) {
      AuthInterceptor.instance = new AuthInterceptor();
    }
    return AuthInterceptor.instance;
  }

  /**
   * Add authentication token to request headers
   */
  addAuthToken = (config: RequestConfig): RequestConfig => {
    const token = localStorage.getItem('access_token');
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  };

  /**
   * Process queued requests after token refresh
   */
  private processQueue = (error: unknown, token: string | null = null): void => {
    this.failedQueue.forEach(({ resolve, reject }) => {
      if (error) {
        reject(error);
      } else {
        resolve(token);
      }
    });
    
    this.failedQueue = [];
  };

  /**
   * Refresh authentication token
   */
  private async refreshToken(): Promise<string> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await fetch('/api/auth/refresh/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!response.ok) {
        throw new Error('Token refresh failed');
      }

      const data = await response.json();
      const newToken = data.access;
      
      localStorage.setItem('access_token', newToken);
      return newToken;
    } catch (error) {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
      throw error;
    } finally {
      this.isRefreshing = false;
    }
  }

  /**
   * Handle authentication errors and token refresh
   */
  handleAuthError = async (error: ErrorResponse): Promise<unknown> => {
    if (!hasConfigProperty(error) || !hasResponseProperty(error)) {
      throw error;
    }

    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (this.isRefreshing) {
        return new Promise((resolve, reject) => {
          this.failedQueue.push({ resolve, reject });
        }).then(() => {
          const token = localStorage.getItem('access_token');
          if (originalRequest.headers && token) {
            originalRequest.headers.Authorization = `Bearer ${token}`;
          }
          
          // Reconstruct the request using public API methods
          const { method, url, data, ...config } = originalRequest;
          if (!method || !url) {
            throw new Error('Invalid request configuration');
          }

          switch (method.toLowerCase()) {
            case 'get':
              return apiClient.get(url, config);
            case 'post':
              return apiClient.post(url, data, config);
            case 'put':
              return apiClient.put(url, data, config);
            case 'patch':
              return apiClient.patch(url, data, config);
            case 'delete':
              return apiClient.delete(url, config);
            default:
              return apiClient.get(url, config);
          }
        });
      }

      originalRequest._retry = true;
      this.isRefreshing = true;

      try {
        const newToken = await this.refreshToken();
        this.processQueue(null, newToken);
        if (originalRequest.headers) {
          originalRequest.headers.Authorization = `Bearer ${newToken}`;
        }
        
        // Reconstruct the request using public API methods
        const { method, url, data, ...config } = originalRequest;
        if (!method || !url) {
          throw new Error('Invalid request configuration');
        }

        switch (method.toLowerCase()) {
          case 'get':
            return apiClient.get(url, config);
          case 'post':
            return apiClient.post(url, data, config);
          case 'put':
            return apiClient.put(url, data, config);
          case 'patch':
            return apiClient.patch(url, data, config);
          case 'delete':
            return apiClient.delete(url, config);
          default:
            return apiClient.get(url, config);
        }
      } catch (refreshError) {
        this.processQueue(refreshError, null);
        throw refreshError;
      }
    }

    throw error;
  };
}

// Error handling interceptor
class ErrorInterceptor {
  private static instance: ErrorInterceptor;

  static getInstance(): ErrorInterceptor {
    if (!ErrorInterceptor.instance) {
      ErrorInterceptor.instance = new ErrorInterceptor();
    }
    return ErrorInterceptor.instance;
  }

  /**
   * Handle API error responses
   */
  handleErrorResponse = (error: ErrorResponse): never => {
    let errorMessage = 'An unexpected error occurred';
    let errorCode = 'UNKNOWN_ERROR';
    let statusCode = 500;
    let errorData: Record<string, unknown> | undefined;

    // Check if this is already an APIError with specific error code
    if (error instanceof APIError) {
      // Preserve the original APIError properties
      throw error;
    }

    if (hasResponseProperty(error)) {
      statusCode = error.response.status;
      errorData = error.response.data;

      // Handle different error response formats
      if (errorData) {
        // Django REST Framework error format
        if (typeof errorData.detail === 'string') {
          errorMessage = errorData.detail;
        } else if (typeof errorData.message === 'string') {
          errorMessage = errorData.message;
        } else if (errorData.errors) {
          const validationMessage = this.formatValidationErrors(errorData);
          if (validationMessage) {
            errorMessage = validationMessage;
          }
        }

        // Extract error code if available
        if (typeof errorData.code === 'string') {
          errorCode = errorData.code;
        }
      }

      // Handle specific HTTP status codes
      switch (statusCode) {
        case 400:
          if (errorData?.errors) {
            errorMessage = this.formatValidationErrors(errorData) || 'Validation failed';
            errorCode = 'VALIDATION_ERROR';
          } else {
            errorMessage = errorData?.detail as string || errorData?.message as string || 'Bad request';
            errorCode = 'BAD_REQUEST';
          }
          break;
        case 401:
          errorMessage = 'Authentication required';
          errorCode = 'UNAUTHORIZED';
          break;
        case 403:
          errorMessage = 'Access forbidden';
          errorCode = 'FORBIDDEN';
          break;
        case 404:
          errorMessage = 'Resource not found';
          errorCode = 'NOT_FOUND';
          break;
        case 422:
          errorMessage = this.formatValidationErrors(errorData) || 'Validation failed';
          errorCode = 'VALIDATION_ERROR';
          break;
        case 429:
          errorMessage = 'Too many requests. Please try again later.';
          errorCode = 'RATE_LIMITED';
          break;
        case 500:
          errorMessage = 'Internal server error';
          errorCode = 'SERVER_ERROR';
          break;
        case 502:
          errorMessage = 'Bad gateway';
          errorCode = 'BAD_GATEWAY';
          break;
        case 503:
          // Preserve existing error code if it's BACKEND_UNHEALTHY
          if (errorCode !== 'BACKEND_UNHEALTHY') {
            errorMessage = 'Service unavailable';
            errorCode = 'SERVICE_UNAVAILABLE';
          }
          break;
        case 504:
          errorMessage = 'Gateway timeout';
          errorCode = 'GATEWAY_TIMEOUT';
          break;
      }
    } else if (error.message) {
      errorMessage = error.message;
      errorCode = 'NETWORK_ERROR';
    }

    // Create and throw APIError
    const apiError = new APIError(errorMessage, statusCode, errorCode, errorData);
    
    // Log error in development
    if (process.env.NODE_ENV === 'development') {
      console.error('API Error:', apiError);
    }

    throw apiError;
  };

  /**
   * Format validation errors into readable message
   */
  private formatValidationErrors(data: Record<string, unknown> | undefined): string | null {
    if (!data?.errors || typeof data.errors !== 'object') {
      return null;
    }

    const errors = data.errors as Record<string, string[]>;
    const errorMessages: string[] = [];

    Object.entries(errors).forEach(([field, messages]) => {
      if (Array.isArray(messages)) {
        messages.forEach(message => {
          errorMessages.push(`${field}: ${message}`);
        });
      }
    });

    return errorMessages.length > 0 ? errorMessages.join(', ') : null;
  }
}

// Request interceptor for common headers and logging
class RequestInterceptor {
  private static instance: RequestInterceptor;

  static getInstance(): RequestInterceptor {
    if (!RequestInterceptor.instance) {
      RequestInterceptor.instance = new RequestInterceptor();
    }
    return RequestInterceptor.instance;
  }

  /**
   * Add common headers to all requests
   */
  addCommonHeaders = (config: RequestConfig): RequestConfig => {
    if (!config.headers) {
      config.headers = {};
    }

    // Add common headers
    config.headers['X-Requested-With'] = 'XMLHttpRequest';
    config.headers['Accept'] = 'application/json';

    return config;
  };

  /**
   * Log requests in development mode
   */
  logRequest = (config: RequestConfig): RequestConfig => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`🚀 ${String(config.method || 'GET').toUpperCase()} ${config.url || 'unknown'}`);
    }
    return config;
  };
}

// Response interceptor for data transformation and logging
class ResponseInterceptor {
  private static instance: ResponseInterceptor;

  static getInstance(): ResponseInterceptor {
    if (!ResponseInterceptor.instance) {
      ResponseInterceptor.instance = new ResponseInterceptor();
    }
    return ResponseInterceptor.instance;
  }

  /**
   * Handle successful responses
   */
  handleSuccessResponse = (response: ResponseData): ResponseData => {
    if (process.env.NODE_ENV === 'development') {
      console.log(`✅ ${response.status || 'unknown'} ${String(response.config?.url || 'unknown')}`);
    }
    return response;
  };

  /**
   * Transform response data if needed
   */
  transformResponseData = (response: ResponseData): ResponseData => {
    // Add metadata to response if not present
    if (response.data && typeof response.data === 'object' && response.data !== null) {
      const responseObj = response.data as Record<string, unknown>;
      if (!responseObj._metadata) {
        responseObj._metadata = {
          timestamp: new Date().toISOString(),
          status: response.status
        };
      }
    }

    return response;
  };
}

/**
 * Setup all interceptors for the API client
 */
export function setupInterceptors(client: { 
  interceptors: { 
    request: { 
      use: (fn: (config: RequestConfig) => RequestConfig) => void 
    }; 
    response: { 
      use: (
        success: (response: ResponseData) => ResponseData, 
        error: (error: ErrorResponse) => Promise<void>
      ) => void 
    } 
  } 
}): void {
  const authInterceptor = AuthInterceptor.getInstance();
  const errorInterceptor = ErrorInterceptor.getInstance();
  const requestInterceptor = RequestInterceptor.getInstance();
  const responseInterceptor = ResponseInterceptor.getInstance();

  // Setup request interceptors
  client.interceptors.request.use(requestInterceptor.addCommonHeaders);
  client.interceptors.request.use(authInterceptor.addAuthToken);
  client.interceptors.request.use(requestInterceptor.logRequest);

  // Setup response interceptors
  client.interceptors.response.use(
    responseInterceptor.handleSuccessResponse,
    async (error: ErrorResponse) => {
      try {
        return await authInterceptor.handleAuthError(error);
      } catch (authError) {
        return errorInterceptor.handleErrorResponse(authError as ErrorResponse);
      }
    }
  );
}

export {
  AuthInterceptor,
  ErrorInterceptor,
  RequestInterceptor,
  ResponseInterceptor
};