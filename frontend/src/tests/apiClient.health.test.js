/**
 * @fileoverview API Client Health Check Tests
 * Tests the health check functionality of the API client
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { healthService } from '../services/healthService.ts';
import apiClient from '../services/apiClient.ts';
import { APIError } from '../services/errors.ts';

// Mock fetch for this test only
const mockFetch = vi.fn();

describe('API Client Health Check', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Override global fetch for this test
    global.fetch = mockFetch;
    // Reset health service state
    if (healthService._updateHealthStatus) {
      healthService._updateHealthStatus(null);
    }
  });

  it('should throw BACKEND_UNHEALTHY when health check fails', async () => {
    // Mock fetch to simulate unhealthy backend
    mockFetch.mockRejectedValueOnce(new Error('Connection refused'));

    // Test the API call and expect it to throw
    let caughtError = null;
    try {
      await apiClient.get('/api/v1/test/');
    } catch (error) {
      caughtError = error;
    }

    // Verify the error
    expect(caughtError).not.toBeNull();
    expect(caughtError).toBeInstanceOf(APIError);
    expect(caughtError.code).toBe('BACKEND_UNHEALTHY');
    expect(caughtError.status).toBe(503);
    expect(caughtError.message).toContain('Backend is not healthy');
  });
});