/**
 * Direct test of APIError throwing mechanism
 */
import { vi } from 'vitest';

describe('Direct APIError Test', () => {
  it('should throw and catch APIError correctly', async () => {
    // Import APIError directly
    const { APIError } = await import('../services/errors.ts');
    
    // Test direct error throwing and catching
    let caughtError = null;
    
    try {
      throw new APIError(
        'Backend is not healthy. Request cancelled to prevent failures.',
        503,
        'BACKEND_UNHEALTHY',
        { healthStatus: 'unhealthy' }
      );
    } catch (error) {
      caughtError = error;
    }
    
    console.log('Caught error:', caughtError);
    console.log('Error type:', typeof caughtError);
    console.log('Error constructor:', caughtError?.constructor?.name);
    console.log('Error code:', caughtError?.code);
    console.log('Error status:', caughtError?.status);
    console.log('Error message:', caughtError?.message);
    
    // Verify the error
    expect(caughtError).toBeInstanceOf(APIError);
    expect(caughtError.code).toBe('BACKEND_UNHEALTHY');
    expect(caughtError.status).toBe(503);
    expect(caughtError.message).toContain('Backend is not healthy');
  });
  
  it('should handle async APIError throwing', async () => {
    const { APIError } = await import('../services/errors.ts');
    
    const asyncFunction = async () => {
      throw new APIError(
        'Backend is not healthy. Request cancelled to prevent failures.',
        503,
        'BACKEND_UNHEALTHY',
        { healthStatus: 'unhealthy' }
      );
    };
    
    let caughtError = null;
    
    try {
      await asyncFunction();
    } catch (error) {
      caughtError = error;
    }
    
    console.log('Async caught error:', caughtError);
    console.log('Async error type:', typeof caughtError);
    console.log('Async error constructor:', caughtError?.constructor?.name);
    
    expect(caughtError).toBeInstanceOf(APIError);
    expect(caughtError.code).toBe('BACKEND_UNHEALTHY');
  });
});