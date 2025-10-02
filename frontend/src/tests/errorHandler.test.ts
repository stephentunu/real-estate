import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'

// Mock the ToastService before any imports
vi.mock('@/services/toastService', () => ({
  toastService: {
    showAPIError: vi.fn(),
    showError: vi.fn(),
    showNetworkOffline: vi.fn(),
    showNetworkOnline: vi.fn(),
    showSuccess: vi.fn()
  }
}))

import { errorHandler, handleAPIError, handleError, handleFormError, handleAsyncOperation } from '@/services/errorHandler'
import { APIError, NetworkError, ValidationError, AuthenticationError } from '@/services/errors'
import { toastService } from '@/services/toastService'

// Mock localStorage
const localStorageMock = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn(),
}
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
})

// Mock window.location
const mockLocation = {
  href: '',
  assign: vi.fn(),
  reload: vi.fn(),
}
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true,
})

describe('ErrorHandler', () => {
  beforeEach(() => {
    // Reset all mocks
    vi.clearAllMocks()
    
    // Reset localStorage mock
    localStorageMock.getItem.mockReturnValue(null)
    localStorageMock.setItem.mockClear()
    localStorageMock.removeItem.mockClear()
    
    // Reset network status
    Object.defineProperty(navigator, 'onLine', {
      writable: true,
      value: true
    })
    
    // Reset console methods
    vi.spyOn(console, 'error').mockImplementation(() => {})
    vi.spyOn(console, 'log').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  describe('Singleton Pattern', () => {
    it('should return the same instance', () => {
      const instance1 = errorHandler
      const instance2 = errorHandler
      expect(instance1).toBe(instance2)
    })
  })

  describe('Network Error Handling', () => {
    it('should handle offline network errors', () => {
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: false,
      })

      const networkError = new NetworkError('Connection failed')
      handleAPIError(networkError, 'Test context')

      expect(toastService.showNetworkOffline).toHaveBeenCalled()
    })

    it('should handle online network errors', () => {
      Object.defineProperty(navigator, 'onLine', {
        writable: true,
        value: true,
      })

      const networkError = new NetworkError('Server unreachable')
      handleAPIError(networkError, 'Test context')

      expect(toastService.showError).toHaveBeenCalledWith(
        'Connection Error',
        'Unable to connect to the server. Please try again. (Test context)'
      )
    })

    it('should detect network errors from error properties', () => {
      const fetchError = { message: 'fetch failed', code: 'NETWORK_ERROR' }
      handleAPIError(fetchError, 'Fetch test')

      expect(toastService.showError).toHaveBeenCalledWith(
        'Network Request Failed',
        'Failed to connect to the server. Please check your internet connection and try again. (Fetch test)'
      )
    })
  })

  describe('Authentication Error Handling', () => {
    it('should handle authentication errors and redirect to login', async () => {
      const authError = new AuthenticationError('Token expired')
      
      // Mock setTimeout to execute immediately
      vi.spyOn(global, 'setTimeout').mockImplementation((fn: () => void) => {
        fn();
        return {} as NodeJS.Timeout;
      })

      handleAPIError(authError, 'Auth test')

      expect(localStorageMock.removeItem).toHaveBeenCalledWith('access_token')
      expect(localStorageMock.removeItem).toHaveBeenCalledWith('refresh_token')
      expect(toastService.showError).toHaveBeenCalledWith(
        'Authentication Error',
        'Token expired'
      )
      expect(mockLocation.href).toBe('/login')
    })
  })

  describe('Validation Error Handling', () => {
    it('should handle validation errors with field-specific messages', () => {
      const validationError = new ValidationError('Validation failed', {
        email: ['This field is required'],
        password: ['Password too short']
      })

      handleAPIError(validationError, 'Form validation')

      expect(toastService.showError).toHaveBeenCalledWith('email: This field is required')
    })

    it('should handle validation errors without specific fields', () => {
      const validationError = new ValidationError('General validation error')

      handleAPIError(validationError, 'General validation')

      expect(toastService.showError).toHaveBeenCalledWith(
        'Validation Error',
        'General validation error'
      )
    })
  })

  describe('General API Error Handling', () => {
    it('should handle generic API errors', () => {
      const apiError = new APIError('Server error', 500)
      handleAPIError(apiError, 'API test')

      expect(toastService.showAPIError).toHaveBeenCalledWith(apiError, 'API test')
    })

    it('should handle unknown error types', () => {
      const unknownError = { message: 'Unknown error' }
      handleAPIError(unknownError, 'Unknown test')

      expect(toastService.showAPIError).toHaveBeenCalledWith(unknownError, 'Unknown test')
    })
  })

  describe('Form Error Handling', () => {
    it('should re-throw validation errors for form handling', () => {
      const validationError = new ValidationError('Form validation failed', {
        name: ['Required field']
      })

      expect(() => {
        handleFormError(validationError, 'User form')
      }).toThrow(validationError)
    })

    it('should handle non-validation form errors with toast', () => {
      const formError = new Error('Form submission failed')
      handleFormError(formError, 'User form')

      expect(toastService.showAPIError).toHaveBeenCalledWith(
        formError,
        'Form submission (User form)'
      )
    })
  })

  describe('Async Operation Handling', () => {
    it('should handle successful async operations with success message', async () => {
      const mockOperation = vi.fn().mockResolvedValue('success result')
      
      const result = await handleAsyncOperation(
        mockOperation,
        {
          successMessage: 'Operation completed successfully'
        }
      )

      expect(result).toBe('success result')
      expect(mockOperation).toHaveBeenCalled()
      // Note: toastSuccess is still dynamically imported in handleAsyncOperation
      // We'll need to mock the dynamic import differently
    })

    it('should handle failed async operations', async () => {
      const mockOperation = vi.fn().mockRejectedValue(new Error('Operation failed'))
      
      try {
        await handleAsyncOperation(
          mockOperation,
          {
            errorContext: 'Test operation'
          }
        )
        // Should not reach here
        expect(true).toBe(false)
      } catch (error) {
        expect(toastService.showAPIError).toHaveBeenCalledWith(
          expect.any(Error),
          'Test operation'
        )
      }
    })

    it('should handle successful async operations without success message', async () => {
      const mockOperation = vi.fn().mockResolvedValue('success result')
      
      const result = await handleAsyncOperation(
        mockOperation,
        {}
      )

      expect(result).toBe('success result')
      // toastSuccess should not be called when no success message is provided
    })
  })

  describe('General Error Handling', () => {
    it('should handle general application errors', () => {
      const error = new Error('Application error')
      handleError(error, 'App context')

      expect(toastService.showError).toHaveBeenCalledWith(
        'Unexpected Error',
        'Application error'
      )
    })

    it('should handle errors without messages', () => {
      const error = new Error()
      handleError(error, 'Empty error')

      expect(toastService.showError).toHaveBeenCalledWith(
        'Unexpected Error',
        'Something went wrong. Please try again.'
      )
    })
  })

  describe('Network Status Listeners', () => {
    it('should handle online event', () => {
      const onlineEvent = new Event('online')
      window.dispatchEvent(onlineEvent)

      expect(toastService.showNetworkOnline).toHaveBeenCalled()
    })

    it('should handle offline event', () => {
      const offlineEvent = new Event('offline')
      window.dispatchEvent(offlineEvent)

      expect(toastService.showNetworkOffline).toHaveBeenCalled()
    })
  })

  describe('Global Error Handlers', () => {
    it('should handle unhandled promise rejections', () => {
      const rejectionEvent = new PromiseRejectionEvent('unhandledrejection', {
        promise: Promise.resolve(), // Use resolved promise to avoid actual rejection
        reason: new Error('Unhandled rejection')
      })

      window.dispatchEvent(rejectionEvent)

      expect(toastService.showError).toHaveBeenCalledWith(
        'Unexpected Error',
        'Unhandled rejection'
      )
    })

    it('should handle uncaught errors', () => {
      const errorEvent = new ErrorEvent('error', {
        error: new Error('Uncaught error'),
        message: 'Uncaught error'
      })

      window.dispatchEvent(errorEvent)

      expect(toastService.showError).toHaveBeenCalledWith(
        'Unexpected Error',
        'Uncaught error'
      )
    })

    it('should handle uncaught errors without error object', () => {
      const errorEvent = new ErrorEvent('error', {
        message: 'Error message only'
      })

      window.dispatchEvent(errorEvent)

      expect(toastService.showError).toHaveBeenCalledWith(
        'Unexpected Error',
        'Error message only'
      )
    })
  })
})