/**
 * Tests for the frontend environment configuration system.
 * 
 * This module tests the type-safe environment configuration
 * and validation functionality for the React frontend.
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';

// Mock environment variables
const mockEnv = {
  __VITE_API_URL__: 'http://localhost:8000',
  __VITE_SUPABASE_PROJECT_ID__: 'test-project-id',
  __VITE_SUPABASE_ANON_KEY__: 'test-anon-key',
  __VITE_SUPABASE_URL__: 'https://test-project-id.supabase.co',
  __VITE_APP_ENV__: 'development',
};

describe('Environment Configuration', () => {
  let originalEnv: Record<string, unknown>;

  beforeEach(() => {
    // Store original environment
    originalEnv = {};
    Object.keys(mockEnv).forEach(key => {
      originalEnv[key] = (globalThis as Record<string, unknown>)[key];
    });
    
    // Mock environment variables
    Object.assign(globalThis, mockEnv);
  });

  afterEach(() => {
    // Restore original environment
    Object.keys(mockEnv).forEach(key => {
      if (originalEnv[key] !== undefined) {
        (globalThis as Record<string, unknown>)[key] = originalEnv[key];
      } else {
        delete (globalThis as Record<string, unknown>)[key];
      }
    });
  });

  describe('environment configuration creation', () => {
    it('should create config with valid environment variables', async () => {
      // Clear module cache and re-import to get fresh config
      vi.resetModules();
      const { env } = await import('../environment');

      expect(env.apiUrl).toBe('http://localhost:8000');
      expect(env.supabaseProjectId).toBe('test-project-id');
      expect(env.supabaseAnonKey).toBe('test-anon-key');
      expect(env.supabaseUrl).toBe('https://test-project-id.supabase.co');
      expect(env.appEnv).toBe('development');
      expect(env.isDevelopment).toBe(true);
      expect(env.isProduction).toBe(false);
    });

    it('should use default API URL when not provided', async () => {
      delete (globalThis as Record<string, unknown>).__VITE_API_URL__;
      
      vi.resetModules();
      const { env } = await import('../environment');

      expect(env.apiUrl).toBe('http://localhost:8000');
    });

    it('should throw error for missing required Supabase project ID', async () => {
      delete (globalThis as Record<string, unknown>).__VITE_SUPABASE_PROJECT_ID__;

      vi.resetModules();
      
      await expect(async () => {
        await import('../environment');
      }).rejects.toThrow('VITE_SUPABASE_PROJECT_ID is required but not defined');
    });

    it('should throw error for missing required Supabase anon key', async () => {
      delete (globalThis as Record<string, unknown>).__VITE_SUPABASE_ANON_KEY__;

      vi.resetModules();
      
      await expect(async () => {
        await import('../environment');
      }).rejects.toThrow('VITE_SUPABASE_ANON_KEY is required but not defined');
    });

    it('should throw error for missing required Supabase URL', async () => {
      delete (globalThis as Record<string, unknown>).__VITE_SUPABASE_URL__;

      vi.resetModules();
      
      await expect(async () => {
        await import('../environment');
      }).rejects.toThrow('VITE_SUPABASE_URL is required but not defined');
    });

    it('should throw error for invalid app environment', async () => {
      (globalThis as Record<string, unknown>).__VITE_APP_ENV__ = 'invalid';

      vi.resetModules();
      
      await expect(async () => {
        await import('../environment');
      }).rejects.toThrow('Invalid APP_ENV: invalid. Must be one of: development, staging, production');
    });
  });

  describe('environment-specific behavior', () => {
    it('should handle development environment', async () => {
      (globalThis as Record<string, unknown>).__VITE_APP_ENV__ = 'development';
      
      vi.resetModules();
      const { env } = await import('../environment');

      expect(env.appEnv).toBe('development');
      expect(env.isDevelopment).toBe(true);
      expect(env.isProduction).toBe(false);
    });

    it('should handle staging environment', async () => {
      (globalThis as Record<string, unknown>).__VITE_APP_ENV__ = 'staging';
      
      vi.resetModules();
      const { env } = await import('../environment');

      expect(env.appEnv).toBe('staging');
      expect(env.isDevelopment).toBe(false);
      expect(env.isProduction).toBe(false);
    });

    it('should handle production environment', async () => {
      (globalThis as Record<string, unknown>).__VITE_APP_ENV__ = 'production';
      
      vi.resetModules();
      const { env } = await import('../environment');

      expect(env.appEnv).toBe('production');
      expect(env.isDevelopment).toBe(false);
      expect(env.isProduction).toBe(true);
    });
  });

  describe('exported values', () => {
    it('should export individual configuration values', async () => {
      vi.resetModules();
      const {
        apiUrl,
        supabaseProjectId,
        supabaseAnonKey,
        supabaseUrl,
        appEnv,
        isDevelopment,
        isProduction,
      } = await import('../environment');

      expect(apiUrl).toBe('http://localhost:8000');
      expect(supabaseProjectId).toBe('test-project-id');
      expect(supabaseAnonKey).toBe('test-anon-key');
      expect(supabaseUrl).toBe('https://test-project-id.supabase.co');
      expect(appEnv).toBe('development');
      expect(isDevelopment).toBe(true);
      expect(isProduction).toBe(false);
    });
  });

  describe('configuration validation', () => {
    it('should validate environment types correctly', async () => {
      const validEnvs = ['development', 'staging', 'production'];
      
      for (const env of validEnvs) {
        (globalThis as Record<string, unknown>).__VITE_APP_ENV__ = env;
        
        vi.resetModules();
        const { env: config } = await import('../environment');
        
        expect(config.appEnv).toBe(env);
        expect(config.isDevelopment).toBe(env === 'development');
        expect(config.isProduction).toBe(env === 'production');
      }
    });

    it('should handle empty string environment variables as missing', async () => {
      (globalThis as Record<string, unknown>).__VITE_SUPABASE_PROJECT_ID__ = '';

      vi.resetModules();
      
      await expect(async () => {
        await import('../environment');
      }).rejects.toThrow('VITE_SUPABASE_PROJECT_ID is required but not defined');
    });
  });
});