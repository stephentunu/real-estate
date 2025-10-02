/**
 * @fileoverview Minimal Health Check Tests
 * Minimal test for health check functionality
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { healthService } from '../services/healthService.ts';
import { apiClient } from '../services/apiClient.ts';
import { APIError } from '../services/errors.ts';

// Create a completely isolated test environment
const createIsolatedTest = async () => {
  // Mock fetch locally
  const mockFetch = vi.fn();
  const originalFetch = global.fetch;
  global.fetch = mockFetch;

  try {
    // Import modules fresh
    const { healthService } = await import('../services/healthService.ts');
    const apiClientModule = await import('../services/apiClient.ts');
    const apiClient = apiClientModule.default;
    const { APIError } = await import('../services/errors.ts');

    // Reset health service state
    if (healthService._updateHealthStatus) {
      healthService._updateHealthStatus(null);
    }

    // Mock unhealthy backend
    mockFetch.mockRejectedValueOnce(new Error('Connection refused'));

    // Test the API call - properly handle the promise
    let caughtError = null;
    try {
      const result = await apiClient.get('/api/v1/test/');
      console.log('Unexpected success:', result);
    } catch (error) {
      caughtError = error;
      console.log('Caught error (expected):', error);
    }

    // Log the caught error for debugging
    console.log('Caught error:', caughtError);
    console.log('Error type:', typeof caughtError);
    console.log('Error constructor:', caughtError?.constructor?.name);
    console.log('Error properties:', Object.keys(caughtError || {}));

    // Verify the error
    const isCorrectError = caughtError && 
                          caughtError.code === 'BACKEND_UNHEALTHY' &&
                          caughtError.status === 503 &&
                          caughtError.message.includes('Backend is not healthy');

    return {
      success: isCorrectError,
      error: caughtError,
      details: {
        hasError: !!caughtError,
        errorCode: caughtError?.code,
        errorStatus: caughtError?.status,
        errorMessage: caughtError?.message,
        errorType: typeof caughtError,
        errorConstructor: caughtError?.constructor?.name
      }
    };
  } finally {
    // Restore original fetch
    global.fetch = originalFetch;
  }
};

// Run the test
describe('Health Check Minimal Test', () => {
  it('should handle backend unhealthy error correctly', async () => {
    const result = await createIsolatedTest();
    
    console.log('Test result:', result);
    
    if (!result.success) {
      console.error('Test failed with details:', result.details);
      throw new Error(`Health check test failed: ${JSON.stringify(result.details)}`);
    }
    
    // If we get here, the test passed
    expect(result.success).toBe(true);
  });
});