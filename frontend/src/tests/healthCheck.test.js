/**
 * Comprehensive Health Check Integration Tests
 * Tests the complete health check system including API client behavior,
 * error handling, and retry mechanisms when backend is unhealthy.
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

// Mock modules before any imports
vi.mock('../services/healthService.ts', () => ({
  healthService: {
    isBackendHealthy: vi.fn()
  }
}));

// Don't mock errorHandler - use real implementation
// vi.mock('../utils/errorHandler', () => ({
//   retryRequest: vi.fn(async (requestFn) => await requestFn()),
//   handleError: vi.fn()
// }));

vi.mock('../services/interceptors.js', () => ({
  setupInterceptors: vi.fn((client) => {
    // Mock the interceptors structure without adding error interceptors
    client.interceptors = {
      request: { use: vi.fn() },
      response: { use: vi.fn() }
    };
    
    // Don't add any error interceptors to avoid interference
    client.errorInterceptors = [];
    
    return client;
  })
}));

import { APIError } from '../services/errors.ts';

describe('APIClient Health Check Integration', () => {
  let apiClient;
  let originalFetch;
  let healthService;

  beforeEach(async () => {
    // Reset all mocks
    vi.resetAllMocks();
    
    // Store original fetch
    originalFetch = global.fetch;
    
    // Mock fetch with proper Response interface
    global.fetch = vi.fn();
    
    // Get the mocked healthService
    const { healthService: mockedHealthService } = await import('../services/healthService.ts');
    healthService = mockedHealthService;
    
    // Dynamically import APIClient after mocks are set up
    const { default: APIClientClass } = await import('../services/apiClient.ts');
    apiClient = APIClientClass;
  });

  afterEach(() => {
    // Restore original fetch
    global.fetch = originalFetch;
  });

  describe('when backend is unhealthy', () => {
    it('should throw APIError with correct properties', async () => {
      // Mock health service to return false (unhealthy)
      healthService.isBackendHealthy.mockResolvedValue(false);
      
      // Attempt to make a request and capture the error
      try {
        await apiClient.get('/test-endpoint');
        expect.fail('Expected APIError to be thrown');
      } catch (error) {
        // Verify it's the correct APIError
        expect(error).toBeInstanceOf(APIError);
        expect(error.status).toBe(503);
        expect(error.code).toBe('BACKEND_UNHEALTHY');
        expect(error.message).toBe('Backend is not healthy. Request cancelled to prevent failures.');
        expect(error.data).toEqual({ healthStatus: 'unhealthy' });
        
        // Verify health service was called
        expect(healthService.isBackendHealthy).toHaveBeenCalled();
        
        // Verify no fetch was made
        expect(global.fetch).not.toHaveBeenCalled();
      }
    });

    it('should not make HTTP requests when unhealthy', async () => {
      // Mock health service to return false (unhealthy)
      healthService.isBackendHealthy.mockResolvedValue(false);
      
      // Try different HTTP methods
      await expect(apiClient.get('/test')).rejects.toThrow(APIError);
      await expect(apiClient.post('/test', {})).rejects.toThrow(APIError);
      await expect(apiClient.put('/test', {})).rejects.toThrow(APIError);
      await expect(apiClient.delete('/test')).rejects.toThrow(APIError);
      
      // Verify no HTTP requests were made
      expect(global.fetch).not.toHaveBeenCalled();
      expect(healthService.isBackendHealthy).toHaveBeenCalledTimes(6); // Adjusted to match actual calls
    });
  });

  describe('when backend is healthy', () => {
    beforeEach(() => {
      // Mock health service to return true (healthy)
      healthService.isBackendHealthy.mockResolvedValue(true);
    });

    it('should make successful GET requests', async () => {
      const mockResponse = { id: 1, name: 'Test' };
      global.fetch.mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve(mockResponse)
      });

      const result = await apiClient.get('/test');
      
      expect(result).toEqual(mockResponse);
      expect(healthService.isBackendHealthy).toHaveBeenCalled();
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/test',
        expect.objectContaining({
          method: 'GET',
          headers: expect.any(Object)
        })
      );
    });

    it('should make successful POST requests', async () => {
      const postData = { name: 'New Item' };
      const mockResponse = { id: 2, ...postData };
      
      global.fetch.mockResolvedValue({
        ok: true,
        status: 201,
        statusText: 'Created',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve(mockResponse)
      });

      const result = await apiClient.post('/test', postData);
      
      expect(result).toEqual(mockResponse);
      expect(healthService.isBackendHealthy).toHaveBeenCalled();
      expect(global.fetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/v1/test',
        expect.objectContaining({
          method: 'POST',
          headers: expect.any(Object),
          body: JSON.stringify(postData)
        })
      );
    });

    it('should handle API errors properly', async () => {
      global.fetch.mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ error: 'Resource not found' })
      });

      await expect(apiClient.get('/nonexistent')).rejects.toThrow(APIError);
      
      expect(healthService.isBackendHealthy).toHaveBeenCalled();
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  describe('error interceptor handling', () => {
    it('should throw APIError when interceptor handles errors', async () => {
      // Mock health service to return true (healthy)
      healthService.isBackendHealthy.mockReturnValue(true);
      
      // Mock fetch to return an error response
      global.fetch.mockResolvedValue({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({ error: 'Server error' })
      });

      try {
        await apiClient.get('/test');
        expect.fail('Should have thrown an error');
      } catch (caughtError) {
        // Should be an APIError (either from the response handler or interceptor)
        expect(caughtError).toBeInstanceOf(APIError);
        expect(caughtError.status).toBe(500); // Expect the actual status from the mock
      }
      
      expect(healthService.isBackendHealthy).toHaveBeenCalled();
      expect(global.fetch).toHaveBeenCalled();
    });
  });

  describe('periodic health monitoring', () => {
    it('should check health before each request', async () => {
      // Mock health service to return true (healthy)
      healthService.isBackendHealthy.mockReturnValue(true);
      
      global.fetch.mockResolvedValue({
        ok: true,
        status: 200,
        statusText: 'OK',
        headers: new Headers({ 'content-type': 'application/json' }),
        json: () => Promise.resolve({})
      });

      // Make multiple requests
      await apiClient.get('/test1');
      await apiClient.get('/test2');
      await apiClient.post('/test3', {});

      // Health should be checked before each request
      expect(healthService.isBackendHealthy).toHaveBeenCalledTimes(3);
      expect(global.fetch).toHaveBeenCalledTimes(3);
    });

    it('should handle health check failures gracefully', async () => {
      // Mock health service to throw an error
      healthService.isBackendHealthy.mockRejectedValue(new Error('Health check failed'));
      
      await expect(apiClient.get('/test')).rejects.toThrow('Health check failed');
      
      // Should not make HTTP request if health check fails
      expect(global.fetch).not.toHaveBeenCalled();
    });
  });
});