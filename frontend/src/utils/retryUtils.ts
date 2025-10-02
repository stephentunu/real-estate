/**
 * Retry utility with exponential backoff for handling failed API requests
 */

export interface RetryOptions {
  maxAttempts?: number;
  baseDelay?: number;
  maxDelay?: number;
  backoffFactor?: number;
  retryCondition?: (error: unknown) => boolean;
  onRetry?: (attempt: number, error: unknown) => void;
}

export interface RetryResult<T> {
  success: boolean;
  data?: T;
  error?: unknown;
  attempts: number;
}

/**
 * Default retry condition - retries on network errors and 5xx server errors
 */
const defaultRetryCondition = (error: unknown): boolean => {
  // Type guard for error with response property
  const hasResponse = (err: unknown): err is { response?: { status?: number } } => {
    return typeof err === 'object' && err !== null && 'response' in err;
  };

  // Type guard for error with code property
  const hasCode = (err: unknown): err is { code?: string } => {
    return typeof err === 'object' && err !== null && 'code' in err;
  };

  // Retry on network errors (no response)
  if (!hasResponse(error) || !error.response) {
    return true;
  }
  
  // Retry on server errors (5xx)
  if (error.response?.status && error.response.status >= 500) {
    return true;
  }
  
  // Retry on specific network error codes
  const networkErrorCodes = [
    'ERR_NETWORK',
    'ERR_CONNECTION_REFUSED',
    'ECONNREFUSED',
    'ERR_CONNECTION_RESET',
    'ERR_CONNECTION_TIMEOUT',
    'ETIMEDOUT',
    'ENOTFOUND'
  ];
  
  if (hasCode(error) && error.code && networkErrorCodes.includes(error.code)) {
    return true;
  }
  
  // Don't retry on client errors (4xx) except 408 (timeout) and 429 (rate limit)
  if (error.response?.status === 408 || error.response?.status === 429) {
    return true;
  }
  
  return false;
};

/**
 * Sleep utility for delays
 */
const sleep = (ms: number): Promise<void> => {
  return new Promise(resolve => setTimeout(resolve, ms));
};

/**
 * Calculate delay with exponential backoff and jitter
 */
const calculateDelay = (
  attempt: number, 
  baseDelay: number, 
  maxDelay: number, 
  backoffFactor: number
): number => {
  const exponentialDelay = baseDelay * Math.pow(backoffFactor, attempt - 1);
  const jitter = Math.random() * 0.1 * exponentialDelay; // Add 10% jitter
  return Math.min(exponentialDelay + jitter, maxDelay);
};

/**
 * Retry a function with exponential backoff
 */
export async function retryWithBackoff<T>(
  fn: () => Promise<T>,
  options: RetryOptions = {}
): Promise<RetryResult<T>> {
  const {
    maxAttempts = 3,
    baseDelay = 1000,
    maxDelay = 10000,
    backoffFactor = 2,
    retryCondition = defaultRetryCondition,
    onRetry
  } = options;

  let lastError: unknown;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      const result = await fn();
      return {
        success: true,
        data: result,
        attempts: attempt
      };
    } catch (error) {
      lastError = error;
      
      // Don't retry if this is the last attempt
      if (attempt === maxAttempts) {
        break;
      }
      
      // Check if we should retry this error
      if (!retryCondition(error)) {
        break;
      }
      
      // Call onRetry callback if provided
      if (onRetry) {
        onRetry(attempt, error);
      }
      
      // Calculate delay and wait
      const delay = calculateDelay(attempt, baseDelay, maxDelay, backoffFactor);
      await sleep(delay);
    }
  }
  
  return {
    success: false,
    error: lastError,
    attempts: maxAttempts
  };
}

/**
 * Retry wrapper for fetch requests
 */
export async function retryFetch(
  url: string,
  options: RequestInit = {},
  retryOptions: RetryOptions = {}
): Promise<Response> {
  const result = await retryWithBackoff(
    () => fetch(url, options),
    {
      ...retryOptions,
      retryCondition: (error) => {
        // Custom retry condition for fetch
        if (error instanceof TypeError && error.message.includes('fetch')) {
          return true;
        }
        return retryOptions.retryCondition ? retryOptions.retryCondition(error) : defaultRetryCondition(error);
      }
    }
  );
  
  if (result.success && result.data) {
    return result.data;
  }
  
  throw result.error;
}

/**
 * Create a retry-enabled version of an async function
 */
export function withRetry<T extends unknown[], R>(
  fn: (...args: T) => Promise<R>,
  retryOptions: RetryOptions = {}
) {
  return async (...args: T): Promise<R> => {
    const result = await retryWithBackoff(
      () => fn(...args),
      retryOptions
    );
    
    if (result.success && result.data !== undefined) {
      return result.data;
    }
    
    throw result.error;
  };
}

export default {
  retryWithBackoff,
  retryFetch,
  withRetry,
  defaultRetryCondition
};