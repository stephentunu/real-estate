/**
 * @fileoverview Health Check Isolated Tests
 * Tests the health check functionality in isolation
 */

import { describe, it, expect, beforeEach, vi } from 'vitest';
import { healthService } from '../services/healthService.ts';
import apiClient from '../services/apiClient.ts';
import { APIError } from '../services/errors.ts';

// Mock fetch globally
const mockFetch = vi.fn();
global.fetch = mockFetch;

describe('Health Check Isolated Test', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Reset health service cache
    healthService._updateHealthStatus(null);
  });

  it('should throw BACKEND_UNHEALTHY error when backend is down', async () => {
    // Mock unhealthy backend response
    mockFetch.mockRejectedValueOnce(new Error('Connection refused'));

    // Use expect().rejects to properly handle the async error
    await expect(apiClient.get('/api/v1/users/')).rejects.toMatchObject({
      code: 'BACKEND_UNHEALTHY',
      message: expect.stringContaining('Backend is not healthy'),
      status: 503
    });
  });
});