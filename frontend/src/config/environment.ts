/**
 * Frontend environment configuration module.
 * 
 * This module provides type-safe access to environment variables
 * exposed by Vite's build process. All variables are validated
 * and provide sensible defaults.
 */

export interface EnvironmentConfig {
  readonly apiUrl: string;
  readonly supabaseProjectId: string;
  readonly supabaseAnonKey: string;
  readonly supabaseUrl: string;
  readonly appEnv: 'development' | 'staging' | 'production';
  readonly isDevelopment: boolean;
  readonly isProduction: boolean;
}

/**
 * Validates and returns the current environment configuration.
 * 
 * @returns {EnvironmentConfig} Validated environment configuration object
 * @throws {Error} If required environment variables are missing
 */
function createEnvironmentConfig(): EnvironmentConfig {
  // Access Vite-defined globals (defined in vite.config.ts)
  const globalVars = globalThis as Record<string, unknown>;
  const apiUrl = (globalVars.__VITE_API_URL__ as string) || 'http://localhost:8000';
  const supabaseProjectId = globalVars.__VITE_SUPABASE_PROJECT_ID__ as string;
  const supabaseAnonKey = globalVars.__VITE_SUPABASE_ANON_KEY__ as string;
  const supabaseUrl = globalVars.__VITE_SUPABASE_URL__ as string;
  const appEnv = (globalVars.__VITE_APP_ENV__ as string) || 'development';

  // Validate required variables
  if (!supabaseProjectId) {
    throw new Error('VITE_SUPABASE_PROJECT_ID is required but not defined');
  }
  
  if (!supabaseAnonKey) {
    throw new Error('VITE_SUPABASE_ANON_KEY is required but not defined');
  }
  
  if (!supabaseUrl) {
    throw new Error('VITE_SUPABASE_URL is required but not defined');
  }

  // Validate app environment
  const validEnvs = ['development', 'staging', 'production'] as const;
  if (!validEnvs.includes(appEnv as 'development' | 'staging' | 'production')) {
    throw new Error(`Invalid APP_ENV: ${appEnv}. Must be one of: ${validEnvs.join(', ')}`);
  }

  return {
    apiUrl,
    supabaseProjectId,
    supabaseAnonKey,
    supabaseUrl,
    appEnv: appEnv as 'development' | 'staging' | 'production',
    isDevelopment: appEnv === 'development',
    isProduction: appEnv === 'production',
  };
}

// Export singleton instance
export const env: EnvironmentConfig = createEnvironmentConfig();

// Export individual values for convenience
export const {
  apiUrl,
  supabaseProjectId,
  supabaseAnonKey,
  supabaseUrl,
  appEnv,
  isDevelopment,
  isProduction,
} = env;