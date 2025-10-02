// Dynamic imports for toast functions to support mocking in tests
import { 
  APIError, 
  NetworkError, 
  ValidationError, 
  AuthenticationError,
  APIValidationError
} from './errors'
import { toastService } from './toastService'
import { authService } from './authService'

/**
 * Union type for all possible error types that can be handled
 */
type HandlableError = 
  | APIError 
  | APIValidationError
  | NetworkError 
  | AuthenticationError 
  | ValidationError 
  | Error 
  | { message: string; code?: string; status?: number; name?: string }
  | unknown;

/**
 * Centralized error handler for the application
 * Provides consistent error handling and user feedback
 */
export class ErrorHandler {
  private static instance: ErrorHandler
  private isOnline: boolean = navigator.onLine

  private constructor() {
    this.setupNetworkListeners()
  }

  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler()
    }
    return ErrorHandler.instance
  }

  /**
   * Setup network status listeners
   */
  private setupNetworkListeners(): void {
    window.addEventListener('online', () => {
      this.isOnline = true
      toastService.showNetworkOnline()
    })

    window.addEventListener('offline', () => {
      this.isOnline = false
      toastService.showNetworkOffline()
    })
  }

  /**
   * Handle API errors with appropriate user feedback
   */
  public handleAPIError(error: HandlableError, context?: string): void {
    console.error('API Error:', error, { context })

    // Handle backend health check failures
    if (this.isErrorWithCode(error) && error.code === 'BACKEND_UNHEALTHY') {
      toastService.showError(
        'Backend Unavailable',
        'The backend service is currently unavailable. Please try again later.'
      )
      return
    }

    // Handle non-JSON response errors
    if (this.isErrorWithCode(error) && error.code === 'INVALID_CONTENT_TYPE') {
      toastService.showError(
        'Invalid Response Format',
        'The server returned an unexpected response format. Please contact support if this persists.'
      )
      return
    }

    // Handle JSON parsing errors
    if (this.isErrorWithCode(error) && error.code === 'JSON_PARSE_ERROR') {
      toastService.showError(
        'Response Parse Error',
        'Unable to process server response. The server may be experiencing issues.'
      )
      return
    }

    // Check if it's a network error
    if (!navigator.onLine || this.isNetworkError(error)) {
      this.handleNetworkError(error, context)
      return
    }

    // Handle specific error types
    if (error instanceof AuthenticationError) {
      this.handleAuthError(error, context)
      return
    }

    if (error instanceof ValidationError) {
      this.handleValidationError(error, context)
      return
    }

    // Handle APIError instances
    if (error instanceof APIError) {
      toastService.showAPIError(error, context)
      return
    }

    // Handle generic errors
    if (error instanceof Error) {
      toastService.showAPIError(error, context)
      return
    }

    // Handle unknown error types
    toastService.showAPIError(error, context)
  }

  /**
   * Handle network-related errors
   */
  private handleNetworkError(error: HandlableError, context?: string): void {
    console.error('Network Error:', error, { context })
    
    if (!navigator.onLine) {
      toastService.showNetworkOffline()
      return
    }

    // Provide more specific error messages based on error type
    let title = 'Connection Error'
    let description = 'Unable to connect to the server. Please try again.'

    const errorMessage = this.isErrorWithMessage(error) ? error.message.toLowerCase() : ''
    
    if (errorMessage.includes('connection refused') || 
        errorMessage.includes('net::err_connection_refused') ||
        (this.isErrorWithCode(error) && error.code === 'ERR_CONNECTION_REFUSED') ||
        (this.isErrorWithCode(error) && error.code === 'ECONNREFUSED')) {
      title = 'Server Unavailable'
      description = 'The server is currently unavailable. Please check if the backend service is running or try again later.'
    } else if (errorMessage.includes('connection timed out') || 
               errorMessage.includes('etimedout') ||
               (this.isErrorWithCode(error) && error.code === 'ETIMEDOUT')) {
      title = 'Connection Timeout'
      description = 'The request took too long to complete. Please check your internet connection and try again.'
    } else if (errorMessage.includes('name not resolved') || 
               errorMessage.includes('enotfound') ||
               (this.isErrorWithCode(error) && error.code === 'ENOTFOUND')) {
      title = 'Server Not Found'
      description = 'Unable to find the server. Please check the server address and your internet connection.'
    } else if (errorMessage.includes('failed to fetch') || 
               errorMessage.includes('fetch')) {
      title = 'Network Request Failed'
      description = 'Failed to connect to the server. Please check your internet connection and try again.'
    }

    // Add context if provided
    if (context) {
      description = `${description} (${context})`
    }

    toastService.showError(title, description)
  }

  /**
   * Handle authentication errors
   */
  private handleAuthError(error: AuthenticationError, context?: string): void {
    console.error('Authentication Error:', error, { context })
    
    // Clear any stored auth tokens
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    
    toastService.showError(
      'Authentication Error',
      error.message || 'Please log in again'
    )
    
    // Redirect to login page after a short delay
    setTimeout(() => {
      window.location.href = '/login'
    }, 2000)
  }

  /**
   * Handle validation errors
   */
  private handleValidationError(error: ValidationError, context?: string): void {
    console.error('Validation Error:', error, { context })
    
    if (error.validationErrors && typeof error.validationErrors === 'object') {
      // Show specific field errors
      for (const [field, messages] of Object.entries(error.validationErrors)) {
        if (Array.isArray(messages) && messages.length > 0) {
          toastService.showError(`${field}: ${messages[0]}`)
        }
      }
    } else {
      // Show general validation error
      toastService.showError(
        'Validation Error',
        error.message || 'Please check your input and try again'
      )
    }
  }

  /**
   * Handle general application errors
   */
  public handleError(error: Error, context?: string): void {
    console.error('Application Error:', error, { context })
    
    toastService.showError(
      'Unexpected Error',
      error.message || 'Something went wrong. Please try again.'
    )
  }

  /**
   * Type guard to check if error has a code property
   */
  private isErrorWithCode(error: HandlableError): error is { code: string } & HandlableError {
    return typeof error === 'object' && error !== null && 'code' in error && typeof (error as Record<string, unknown>).code === 'string'
  }

  /**
   * Type guard to check if error has a message property
   */
  private isErrorWithMessage(error: HandlableError): error is { message: string } & HandlableError {
    return typeof error === 'object' && error !== null && 'message' in error && typeof (error as Record<string, unknown>).message === 'string'
  }

  /**
   * Check if error is network-related
   */
  private isNetworkError(error: HandlableError): boolean {
    // Check for NetworkError instance
    if (error instanceof NetworkError) {
      return true
    }

    // Check for common network error codes
    const networkErrorCodes = [
      'NETWORK_ERROR',
      'ERR_NETWORK',
      'ERR_CONNECTION_REFUSED', 
      'ERR_CONNECTION_RESET',
      'ERR_CONNECTION_TIMED_OUT',
      'ERR_INTERNET_DISCONNECTED',
      'ERR_NAME_NOT_RESOLVED',
      'ECONNREFUSED',
      'ENOTFOUND',
      'ETIMEDOUT'
    ]

    if (this.isErrorWithCode(error) && networkErrorCodes.includes(error.code)) {
      return true
    }

    // Check error message patterns
    const errorMessage = this.isErrorWithMessage(error) ? error.message.toLowerCase() : ''
    const networkErrorPatterns = [
      'network error',
      'fetch',
      'connection refused',
      'connection reset',
      'connection timed out',
      'internet disconnected',
      'name not resolved',
      'failed to fetch',
      'net::err_connection_refused',
      'net::err_network_changed',
      'net::err_internet_disconnected',
      'net::err_name_not_resolved',
      'net::err_connection_timed_out',
      'net::err_connection_reset',
      'unable to connect',
      'server unreachable'
    ]

    if (networkErrorPatterns.some(pattern => errorMessage.includes(pattern))) {
      return true
    }

    // Check for TypeError with fetch-related messages
    if (typeof error === 'object' && error !== null && 'name' in error && 
        (error as { name: unknown }).name === 'TypeError' && errorMessage.includes('fetch')) {
      return true
    }

    // Check for cases where response is undefined but there's a network-related message
    if (typeof error === 'object' && error !== null && 'response' in error &&
        (error as { response: unknown }).response === undefined && 
        (errorMessage.includes('network') || 
         errorMessage.includes('connection') ||
         errorMessage.includes('fetch'))) {
      return true
    }

    // Check for Axios-specific network error patterns
    if (typeof error === 'object' && error !== null && 
        'request' in error && 'response' in error &&
        (error as { request: unknown; response: unknown }).request && 
        !(error as { request: unknown; response: unknown }).response) {
      return true
    }

    return false
  }

  /**
   * Handle form submission errors
   */
  public handleFormError(error: HandlableError, formContext: string): void {
    if (error instanceof ValidationError && error.validationErrors) {
      // Return validation errors for form handling
      throw error
    } else {
      // Show toast for other errors
      this.handleAPIError(error, `Form submission (${formContext})`)
    }
  }

  /**
   * Handle async operations with loading states and error handling
   */
  public async handleAsyncOperation<T>(
    operation: () => Promise<T>,
    options: {
      loadingMessage?: string
      successMessage?: string
      errorContext?: string
    } = {}
  ): Promise<T> {
    const { loadingMessage, successMessage, errorContext } = options
    
    try {
      if (loadingMessage) {
        // Show loading toast if message provided
        console.log('Loading:', loadingMessage)
      }
      
      const result = await operation()
      
      if (successMessage) {
        toastService.showSuccess(successMessage)
      }
      
      return result
    } catch (error) {
      this.handleAPIError(error, errorContext)
      throw error
    }
  }
}

// Export singleton instance
export const errorHandler = ErrorHandler.getInstance()

// Convenience functions for common error handling patterns
export const handleAPIError = (error: HandlableError, context?: string) => {
  errorHandler.handleAPIError(error, context)
}

export const handleError = (error: Error, context?: string) => {
  errorHandler.handleError(error, context)
}

export const handleFormError = (error: HandlableError, formContext: string) => {
  errorHandler.handleFormError(error, formContext)
}

export const handleAsyncOperation = <T>(
  operation: () => Promise<T>,
  options: {
    loadingMessage?: string
    successMessage?: string
    errorContext?: string
  } = {}
) => {
  return errorHandler.handleAsyncOperation(operation, options)
}

// Global error handlers
window.addEventListener('unhandledrejection', (event) => {
  console.error('Unhandled Promise Rejection:', event.reason)
  errorHandler.handleError(
    event.reason instanceof Error ? event.reason : new Error(String(event.reason)),
    'Unhandled Promise Rejection'
  )
  event.preventDefault()
})

window.addEventListener('error', (event) => {
  console.error('Global Error:', event.error)
  errorHandler.handleError(
    event.error || new Error(event.message),
    'Global Error'
  )
})