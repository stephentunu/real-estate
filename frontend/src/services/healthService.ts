/**
 * Health monitoring service for backend availability checking.
 *
 * Ensures that the frontend only makes API calls when the backend is healthy.
 * Provides proactive health checking, caching, and resilience against transient failures.
 */

interface HealthCheckResult {
  timestamp: number;
  isHealthy: boolean;
}

interface SystemStatusResponse {
  status?: string;
  [key: string]: unknown;
}

class HealthService {
  private baseURL: string;
  private healthEndpoint: string;
  private lastHealthCheck: HealthCheckResult | null;
  private healthCheckInterval: number;
  private isHealthy: boolean;
  private healthCheckPromise: Promise<boolean> | null;
  private monitoringInterval: ReturnType<typeof setInterval> | null;
  private abortController: AbortController | null;

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api/v1';
    this.healthEndpoint = `${this.baseURL}/health/`;
    this.lastHealthCheck = null;
    this.healthCheckInterval = 30000; // 30 seconds
    this.isHealthy = true;
    this.healthCheckPromise = null;
    this.monitoringInterval = null;
    this.abortController = null;
  }

  /**
   * Checks if the backend is healthy.
   * Uses cached results if recent enough.
   */
  async isBackendHealthy(): Promise<boolean> {
    const now = Date.now();

    if (this.lastHealthCheck && (now - this.lastHealthCheck.timestamp) < this.healthCheckInterval) {
      return this.lastHealthCheck.isHealthy;
    }

    if (this.healthCheckPromise) {
      return this.healthCheckPromise;
    }

    this.healthCheckPromise = this._performHealthCheck();
    const result = await this.healthCheckPromise;
    this.healthCheckPromise = null;

    return result;
  }

  /**
   * Performs the actual backend health check.
   * Handles timeouts and aborts gracefully.
   */
  private async _performHealthCheck(): Promise<boolean> {
    this.abortController?.abort(); // cancel any ongoing check
    this.abortController = new AbortController();

    try {
      const timeout = 15000; // 5 seconds max
      const timeoutPromise = new Promise<never>((_, reject) => {
        setTimeout(() => {
          if (!this.abortController?.signal.aborted) {
            this.abortController?.abort();
            reject(new Error('Health check timeout'));
          }
        }, timeout);
      });

      const fetchPromise = fetch(this.healthEndpoint, {
        method: 'GET',
        headers: { Accept: 'application/json' },
        signal: this.abortController.signal,
      });

      const response = await Promise.race([fetchPromise, timeoutPromise]);

      if (!(response instanceof Response)) {
        throw new Error('Invalid response during health check');
      }

      if (!response.ok) {
        console.warn(`[HealthService] Health check failed with status ${response.status}`);
        this._updateHealthStatus(false);
        return false;
      }

      const contentType = response.headers.get('content-type');
      if (!contentType?.includes('application/json')) {
        console.warn('[HealthService] Non-JSON health response received.');
        this._updateHealthStatus(false);
        return false;
      }

      const data: SystemStatusResponse = await response.json();
      const isHealthy = data.status?.toLowerCase() === 'healthy';

      this._updateHealthStatus(isHealthy);
      return isHealthy;
    } catch (error: any) {
      if (error.name === 'AbortError') {
        console.warn('[HealthService] Health check aborted due to timeout.');
      } else {
        console.error('[HealthService] Health check failed:', error.message || error);
      }
      this._updateHealthStatus(false);
      return false;
    }
  }

  /**
   * Updates the cached health status.
   */
  private _updateHealthStatus(isHealthy: boolean): void {
    this.lastHealthCheck = {
      timestamp: Date.now(),
      isHealthy,
    };
    this.isHealthy = isHealthy;
  }

  /**
   * Forces a fresh health check (ignores cache).
   */
  async forceHealthCheck(): Promise<boolean> {
    this.lastHealthCheck = null;
    this.healthCheckPromise = null;
    return this.isBackendHealthy();
  }

  /**
   * Fetches extended system status info.
   */
  async getSystemStatus(): Promise<Record<string, unknown> | null> {
    try {
      const response = await fetch(`${this.baseURL}/status/`, {
        method: 'GET',
        headers: { Accept: 'application/json' },
      });

      if (response.ok && response.headers.get('content-type')?.includes('application/json')) {
        return (await response.json()) as Record<string, unknown>;
      }

      return null;
    } catch (error: any) {
      console.error('[HealthService] System status check failed:', error.message || error);
      return null;
    }
  }

  /**
   * Starts background monitoring of backend health.
   */
  startMonitoring(interval: number = 30000): void {
    this.healthCheckInterval = interval;
    this.isBackendHealthy(); // perform initial check

    if (this.monitoringInterval) clearInterval(this.monitoringInterval);
    this.monitoringInterval = setInterval(() => this.forceHealthCheck(), interval);
  }

  /**
   * Stops background health monitoring.
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  /**
   * Returns cached health status.
   */
  getCachedHealthStatus(): boolean {
    return this.isHealthy;
  }
}
console.log("Loaded API Base URL:", import.meta.env.VITE_API_BASE_URL);


export const healthService = new HealthService();
export default healthService;
