/**
 * Error handling utilities for frontend-backend integration
 * Provides consistent error handling across the application
 */

// Import APIError from apiClient instead of defining interface
import { APIError } from '../services/errors.js';

export interface ErrorDetails {
  message: string;
  code?: string;
  field?: string;
  details?: Record<string, unknown>;
}

export interface APIErrorResponse {
  error: string;
  message: string;
  code?: string;
  details?: Record<string, unknown>;
  timestamp: string;
}

export interface NetworkError {
  message: string;
  code?: string;
  status?: number;
  request?: unknown;
  response?: {
    data?: Record<string, unknown>;
    status?: number;
    statusText?: string;
  };
}

export interface ValidationError {
  field: string;
  message: string;
  code?: string;
}

export interface UnknownError {
  message?: string;
  stack?: string;
  name?: string;
}

// Type guards for error data structures
interface ErrorDataWithDetail {
  detail?: string | Record<string, unknown>;
  code?: string;
  message?: string;
  errors?: Array<{ message?: string; code?: string; field?: string }>;
}

interface ErrorDataWithErrors {
  errors?: Array<{ message?: string; code?: string; field?: string }>;
}

interface ErrorDataWithMessage {
  message?: string;
  code?: string;
}

/**
 * Error types for different scenarios
 */
export enum ErrorType {
  NETWORK = 'NETWORK',
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  VALIDATION = 'VALIDATION',
  NOT_FOUND = 'NOT_FOUND',
  SERVER = 'SERVER',
  TIMEOUT = 'TIMEOUT',
  UNKNOWN = 'UNKNOWN',
}

/**
 * Custom error classes for different error scenarios
 */
export class AppError extends Error {
  type: ErrorType;
  code?: string;
  field?: string;
  details?: Record<string, unknown>;
  timestamp: Date;

  constructor(
    message: string,
    type: ErrorType = ErrorType.UNKNOWN,
    code?: string,
    field?: string,
    details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'AppError';
    this.type = type;
    this.code = code;
    this.field = field;
    this.details = details;
    this.timestamp = new Date();
  }
}

/**
 * Map HTTP status codes to error types
 */
function mapStatusToErrorType(status: number): ErrorType {
  switch (status) {
    case 400:
      return ErrorType.VALIDATION;
    case 401:
      return ErrorType.AUTHENTICATION;
    case 403:
      return ErrorType.AUTHORIZATION;
    case 404:
      return ErrorType.NOT_FOUND;
    case 408:
      return ErrorType.TIMEOUT;
    case 500:
    case 502:
    case 503:
    case 504:
      return ErrorType.SERVER;
    default:
      return ErrorType.UNKNOWN;
  }
}

/**
 * Type guards for error data
 */
function hasDetailProperty(data: unknown): data is ErrorDataWithDetail {
  return typeof data === 'object' && data !== null && 'detail' in data;
}

function hasErrorsProperty(data: unknown): data is ErrorDataWithErrors {
  return typeof data === 'object' && data !== null && 'errors' in data;
}

function hasMessageProperty(data: unknown): data is ErrorDataWithMessage {
  return typeof data === 'object' && data !== null && 'message' in data;
}

function isStringOrObject(value: unknown): value is string | Record<string, unknown> {
  return typeof value === 'string' || (typeof value === 'object' && value !== null);
}

/**
 * Parse API error into AppError
 */
export function parseAPIError(apiError: APIError): AppError {
  const { message, status, data } = apiError;
  const errorType = mapStatusToErrorType(status);

  // Handle Django REST Framework error format
  if (data && typeof data === 'object') {
    // Validation errors with detail object
    if (hasDetailProperty(data) && data.detail && typeof data.detail === 'object') {
      const detailObj = data.detail as Record<string, unknown>;
      const firstField = Object.keys(detailObj)[0];
      const fieldErrors = detailObj[firstField];
      const errorMessage = Array.isArray(fieldErrors) ? String(fieldErrors[0]) : String(fieldErrors);
      
      return new AppError(
        errorMessage || 'Validation failed',
        ErrorType.VALIDATION,
        'VALIDATION_ERROR',
        firstField,
        detailObj
      );
    }

    // Single error message in detail
    if (hasDetailProperty(data) && data.detail && typeof data.detail === 'string') {
      return new AppError(
        data.detail,
        errorType,
        data.code || 'API_ERROR'
      );
    }

    // Field-specific errors array
    if (hasErrorsProperty(data) && Array.isArray(data.errors)) {
      const errors = data.errors;
      const firstError = errors[0];
      if (firstError && typeof firstError === 'object') {
        return new AppError(
          firstError.message || 'Validation failed',
          ErrorType.VALIDATION,
          firstError.code || 'VALIDATION_ERROR',
          firstError.field,
          { errors } as Record<string, unknown>
        );
      }
    }

    // Non-field errors with message
    if (hasMessageProperty(data) && data.message) {
      return new AppError(
        data.message,
        errorType,
        data.code || 'API_ERROR',
        undefined,
        data as Record<string, unknown>
      );
    }
  }

  // Fallback to generic error
  return new AppError(
    message || 'An unexpected error occurred',
    errorType,
    'API_ERROR'
  );
}

/**
 * Handle network errors
 */
export function handleNetworkError(error: NetworkError): AppError {
  if (error.response?.status) {
    const errorType = mapStatusToErrorType(error.response.status);
    return new AppError(
      error.message || `Network error: ${error.response.status}`,
      errorType,
      error.code || 'NETWORK_ERROR',
      undefined,
      error.response.data
    );
  }

  return new AppError(
    error.message || 'Network connection failed',
    ErrorType.NETWORK,
    error.code || 'NETWORK_ERROR'
  );
}

/**
 * Display user-friendly error messages
 */
export function getDisplayMessage(error: AppError): string {
  switch (error.type) {
    case ErrorType.NETWORK:
      return 'Unable to connect to the server. Please check your internet connection and try again.';
    case ErrorType.AUTHENTICATION:
      return 'Please log in to continue.';
    case ErrorType.AUTHORIZATION:
      return 'You do not have permission to perform this action.';
    case ErrorType.VALIDATION:
      return error.message || 'Please check your input and try again.';
    case ErrorType.NOT_FOUND:
      return 'The requested resource was not found.';
    case ErrorType.SERVER:
      return 'A server error occurred. Please try again later.';
    case ErrorType.TIMEOUT:
      return 'The request timed out. Please try again.';
    default:
      return error.message || 'An unexpected error occurred. Please try again.';
  }
}

/**
 * Log errors for debugging
 */
export function logError(error: AppError, context?: string): void {
  if (process.env.NODE_ENV === 'development') {
    console.group(`🚨 Error ${context ? `(${context})` : ''}`);
    console.error('Type:', error.type);
    console.error('Message:', error.message);
    console.error('Code:', error.code);
    console.error('Field:', error.field);
    console.error('Details:', error.details);
    console.error('Stack:', error.stack);
    console.groupEnd();
  }
}

/**
 * Handle errors globally
 */
export function handleError(error: unknown, context?: string): AppError {
  let appError: AppError;

  if (error instanceof AppError) {
    appError = error;
  } else if (error instanceof APIError) {
    appError = parseAPIError(error);
  } else if (isNetworkError(error)) {
    // Handle axios-like errors - create proper APIError instance
    const apiError = new APIError(
      error.message || 'API request failed',
      error.response?.status || 0,
      error.response?.data?.code as string,
      error.response?.data
    );
    appError = parseAPIError(apiError);
  } else if (hasRequestProperty(error)) {
    // Network error without response
    appError = new AppError(
      'Network request failed',
      ErrorType.NETWORK,
      'NETWORK_ERROR'
    );
  } else {
    // Unknown error
    const errorMessage = error instanceof Error ? error.message : 'An unexpected error occurred';
    appError = new AppError(
      errorMessage,
      ErrorType.UNKNOWN,
      'UNKNOWN_ERROR'
    );
  }

  logError(appError, context);
  return appError;
}

// Type guard functions
function isNetworkError(error: unknown): error is NetworkError & { response: NonNullable<NetworkError['response']> } {
  return typeof error === 'object' && error !== null && 'response' in error && 
         typeof (error as Record<string, unknown>).response === 'object' && (error as Record<string, unknown>).response !== null;
}

function hasRequestProperty(error: unknown): error is { request: unknown } {
  return typeof error === 'object' && error !== null && 'request' in error;
}

/**
 * Retry logic for failed requests with proper typing
 */
export async function retryRequest<T>(
  requestFn: () => Promise<T>,
  options: { retries?: number; delay?: number } = {}
): Promise<T> {
  const { retries = 3, delay = 1000 } = options;
  let lastError: unknown;

  for (let attempt = 1; attempt <= retries; attempt++) {
    try {
      return await requestFn();
    } catch (error) {
      lastError = error;
      
      // Don't retry on client errors (4xx)
      if (error instanceof APIError && error.status >= 400 && error.status < 500) {
        throw error;
      }

      if (attempt === retries) {
        throw error;
      }

      // Exponential backoff
      const backoffDelay = delay * Math.pow(2, attempt - 1);
      await new Promise(resolve => setTimeout(resolve, backoffDelay));
    }
  }

  throw lastError;
}

/**
 * Validation error utilities
 */
export function formatValidationErrors(errors: ValidationError[] | Record<string, string[]> | unknown): string[] {
  if (Array.isArray(errors)) {
    return errors.map(error => {
      if (typeof error === 'object' && error !== null && 'message' in error) {
        return String((error as ValidationError).message);
      }
      return String(error);
    });
  }

  if (typeof errors === 'object' && errors !== null) {
    return Object.entries(errors as Record<string, string[]>).map(([field, messages]) => {
      const fieldMessages = Array.isArray(messages) ? messages : [String(messages)];
      return `${field}: ${fieldMessages.join(', ')}`;
    });
  }

  return [String(errors)];
}

/**
 * Error tracking for analytics
 */
export function trackError(error: AppError, context?: string): void {
  // In production, integrate with error tracking service like Sentry
  if (process.env.NODE_ENV === 'production') {
    // Example: Sentry.captureException(error, { extra: { context } });
    console.warn('Error tracked:', { error: error.toString(), context });
  }
}