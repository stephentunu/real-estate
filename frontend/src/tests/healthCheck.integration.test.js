/**
 * @fileoverview Health Check Integration Tests
 * Tests the integration between health service and API client
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';

describe('Health Service Integration Test', () => {
  let originalFetch;
  
  beforeEach(() => {
    originalFetch = global.fetch;
    vi.clearAllMocks();
  });
  
  afterEach(() => {
    global.fetch = originalFetch;
  });
  
  it('should properly handle health check failure in API client', async () => {
    // Mock fetch to simulate unhealthy backend
    const mockFetch = vi.fn();
    global.fetch = mockFetch;
    
    // First call for health check - simulate failure
    mockFetch.mockRejectedValueOnce(new Error('Connection refused'));
    
    // Import modules after mocking
    const { healthService } = await import('../services/healthService.ts');
    const apiClientModule = await import('../services/apiClient.ts');
    const apiClient = apiClientModule.default;
    const { APIError } = await import('../services/errors.ts');
    
    // Reset health service state properly
    if (healthService._updateHealthStatus) {
      healthService._updateHealthStatus(false); // Set to false instead of null
    }
    
    // Clear any cached health check
    healthService.lastHealthCheck = null;
    healthService.healthCheckPromise = null;
    
    console.log('Starting health check test...');
    
    // Test the health service directly first
    const isHealthy = await healthService.isBackendHealthy();
    console.log('Health service result:', isHealthy);
    expect(isHealthy).toBe(false);
    
    // Now test the API client
    console.log('Testing API client...');
    
    let caughtError = null;
    try {
      const result = await apiClient.get('/api/v1/test/');
      console.log('Unexpected success:', result);
      throw new Error('Expected API call to fail');
    } catch (error) {
      caughtError = error;
      console.log('Caught error from API client:', error);
      console.log('Error type:', typeof error);
      console.log('Error constructor:', error?.constructor?.name);
      console.log('Error code:', error?.code);
      console.log('Error status:', error?.status);
      console.log('Error message:', error?.message);
    }
    
    // Verify the error
    expect(caughtError).toBeInstanceOf(APIError);
    expect(caughtError.code).toBe('BACKEND_UNHEALTHY');
    expect(caughtError.status).toBe(503);
    expect(caughtError.message).toContain('Backend is not healthy');
  });
});