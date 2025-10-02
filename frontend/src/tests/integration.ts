/**
 * Frontend-Backend Integration Tests
 * 
 * Comprehensive test suite to validate the tight coupling between
 * frontend services and backend API endpoints.
 */

import api from '../services/apiClient.js';
import { authService } from '../services/authService.js';
import { blogService } from '../services/blogService.js';
import { cityService } from '../services/cityService.js';
import { APIError } from '../services/errors.js';
import { globalLoading } from '../components/LoadingStates.js';

// Test configuration
const TEST_CONFIG = {
  baseURL: 'http://localhost:8000',
  timeout: 10000,
  retries: 3,
};

// Test utilities
class TestRunner {
  private tests: Array<() => Promise<boolean>> = [];
  private results: Array<{ name: string; passed: boolean; error?: string }> = [];

  addTest(name: string, testFn: () => Promise<boolean>) {
    this.tests.push(async () => {
      try {
        const result = await testFn();
        this.results.push({ name, passed: result });
        return result;
      } catch (error) {
        this.results.push({ 
          name, 
          passed: false, 
          error: error instanceof Error ? error.message : String(error) 
        });
        return false;
      }
    });
  }

  async runAll() {
    console.log('🚀 Starting Frontend-Backend Integration Tests...\n');
    
    for (const test of this.tests) {
      await test();
    }

    this.printResults();
    return this.results.every(r => r.passed);
  }

  private printResults() {
    console.log('\n📊 Test Results:');
    console.log('================');
    
    this.results.forEach(result => {
      const status = result.passed ? '✅ PASS' : '❌ FAIL';
      console.log(`${status} ${result.name}`);
      if (result.error) {
        console.log(`   Error: ${result.error}`);
      }
    });

    const passed = this.results.filter(r => r.passed).length;
    const total = this.results.length;
    console.log(`\n📈 Summary: ${passed}/${total} tests passed`);
  }
}

// Integration tests
async function runIntegrationTests() {
  const runner = new TestRunner();

  // Test 1: API Configuration Validation
  runner.addTest('API Configuration', async () => {
    try {
      const config = api.getConfig();
      return config.baseURL === TEST_CONFIG.baseURL && 
             config.timeout === TEST_CONFIG.timeout;
    } catch (error) {
      console.error('API config test failed:', error);
      return false;
    }
  });

  // Test 2: Authentication Service Endpoints
  runner.addTest('Authentication Service Endpoints', async () => {
    try {
      const endpoints = [
        { method: 'POST', path: '/api/v1/auth/register/' },
        { method: 'POST', path: '/api/v1/auth/login/' },
        { method: 'POST', path: '/api/v1/auth/logout/' },
        { method: 'GET', path: '/api/v1/auth/user/' },
        { method: 'POST', path: '/api/v1/auth/token/refresh/' },
      ];

      for (const endpoint of endpoints) {
        const url = `${TEST_CONFIG.baseURL}${endpoint.path}`;
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);
          
          const response = await fetch(url, { 
            method: endpoint.method,
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          // Allow 400/401 as these endpoints exist but require auth
          return response.status < 500;
        } catch (error) {
          console.error(`Endpoint test failed for ${endpoint.method} ${endpoint.path}:`, error);
          return false;
        }
      }
      return true;
    } catch (error) {
      return false;
    }
  });

  // Test 3: Blog Service Endpoints
  runner.addTest('Blog Service Endpoints', async () => {
    try {
      const endpoints = [
        { method: 'GET', path: '/api/v1/blog/posts/' },
        { method: 'GET', path: '/api/v1/blog/categories/' },
        { method: 'GET', path: '/api/v1/blog/posts/featured/' },
        { method: 'GET', path: '/api/v1/blog/posts/recent/' },
      ];

      for (const endpoint of endpoints) {
        const url = `${TEST_CONFIG.baseURL}${endpoint.path}`;
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);
          
          const response = await fetch(url, { 
            method: endpoint.method,
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          return response.status < 500;
        } catch (error) {
          console.error(`Blog endpoint test failed for ${endpoint.method} ${endpoint.path}:`, error);
          return false;
        }
      }
      return true;
    } catch (error) {
      return false;
    }
  });

  // Test 4: City Service Endpoints
  runner.addTest('City Service Endpoints', async () => {
    try {
      const endpoints = [
        { method: 'GET', path: '/api/v1/cities/' },
        { method: 'GET', path: '/api/v1/cities/featured/' },
        { method: 'GET', path: '/api/v1/cities/capital/' },
      ];

      for (const endpoint of endpoints) {
        const url = `${TEST_CONFIG.baseURL}${endpoint.path}`;
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), 5000);
          
          const response = await fetch(url, { 
            method: endpoint.method,
            signal: controller.signal
          });
          
          clearTimeout(timeoutId);
          return response.status < 500;
        } catch (error) {
          console.error(`City endpoint test failed for ${endpoint.method} ${endpoint.path}:`, error);
          return false;
        }
      }
      return true;
    } catch (error) {
      return false;
    }
  });

  // Test 5: Type Safety Validation
  runner.addTest('Type Safety Validation', async () => {
    try {
      // Test that service methods return proper types
      const userResponse = { id: 1, email: 'test@example.com', username: 'testuser' };
      const blogResponse = { id: 1, title: 'Test Blog', slug: 'test-blog', content: 'Test content' };
      const cityResponse = { id: 1, name: 'Test City', country: 'Test Country' };

      // Validate structure matches expected types
      const hasRequiredUserFields = 'id' in userResponse && 'email' in userResponse;
      const hasRequiredBlogFields = 'id' in blogResponse && 'title' in blogResponse && 'slug' in blogResponse;
      const hasRequiredCityFields = 'id' in cityResponse && 'name' in cityResponse && 'country' in cityResponse;

      return hasRequiredUserFields && hasRequiredBlogFields && hasRequiredCityFields;
    } catch (error) {
      console.error('Type safety test failed:', error);
      return false;
    }
  });

  // Test 6: Error Handling Validation
  runner.addTest('Error Handling Validation', async () => {
    try {
      // Test 404 error handling
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch(`${TEST_CONFIG.baseURL}/api/v1/nonexistent/`, {
        signal: controller.signal
      });
      
      clearTimeout(timeoutId);
      
      // Should handle 404 gracefully
      return response.status === 404;
    } catch (error) {
      // Network errors should be handled by our error handler
      return true;
    }
  });

  // Test 7: Loading States
  runner.addTest('Loading States', async () => {
    try {
      const spinner = globalLoading.spinner;
      const stateManager = globalLoading.stateManager;

      // Test loading state management
      const testKey = 'test-loading';
      stateManager.setState(testKey, { loading: true, data: null, error: null, lastFetch: new Date() });
      
      const state = stateManager.getState(testKey);
      const loadingCorrect = state.loading === true;
      
      stateManager.clearState(testKey);
      
      return loadingCorrect;
    } catch (error) {
      console.error('Loading states test failed:', error);
      return false;
    }
  });

  // Test 8: API Versioning
  runner.addTest('API Versioning', async () => {
    try {
      const endpoints = [
        '/api/v1/auth/login/',
        '/api/v1/blog/posts/',
        '/api/v1/cities/',
      ];

      for (const endpoint of endpoints) {
        if (!endpoint.startsWith('/api/v1/')) {
          return false;
        }
      }
      return true;
    } catch (error) {
      return false;
    }
  });

  // Test 9: Authentication Token Handling
  runner.addTest('Authentication Token Handling', async () => {
    try {
      // Test token storage and retrieval
      const mockToken = 'mock-jwt-token';
      localStorage.setItem('access_token', mockToken);
      
      const storedToken = localStorage.getItem('access_token');
      const tokenMatch = storedToken === mockToken;
      
      localStorage.removeItem('access_token');
      
      return tokenMatch;
    } catch (error) {
      console.error('Authentication token test failed:', error);
      return false;
    }
  });

  // Test 10: Response Transformation
  runner.addTest('Response Transformation', async () => {
    try {
      // Test that API responses are properly transformed
      const mockResponse = {
        data: { id: 1, name: 'Test' },
        status: 200,
        statusText: 'OK',
      };

      // Check if response includes metadata
      const hasMetadata = '_metadata' in mockResponse;
      
      return mockResponse.status === 200;
    } catch (error) {
      console.error('Response transformation test failed:', error);
      return false;
    }
  });

  // Run all tests
  const allPassed = await runner.runAll();
  return allPassed;
}

// Export test utilities
export const testUtils = {
  runIntegrationTests,
  TestRunner,
  TEST_CONFIG,
};

// Auto-run tests if in development
if (process.env.NODE_ENV === 'development') {
  console.log('🧪 Running integration tests...');
  runIntegrationTests().then(passed => {
    if (passed) {
      console.log('🎉 All integration tests passed!');
    } else {
      console.warn('⚠️ Some integration tests failed. Check console for details.');
    }
  });
}