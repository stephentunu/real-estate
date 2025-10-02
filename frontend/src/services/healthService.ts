/**
 * Health monitoring service for backend availability checking.
 * 
 * This service ensures that the frontend only attempts API calls
 * when the backend is healthy and available. It provides proactive
 * health checking and caching to minimize unnecessary requests.
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
  private monitoringInterval: NodeJS.Timeout | null;

  constructor() {
    this.baseURL = 'http://localhost:8000/api/v1';
    this.healthEndpoint = `${this.baseURL}/health/`;
    this.lastHealthCheck = null;
    this.healthCheckInterval = 30000; // 30 seconds
    this.isHealthy = true;
    this.healthCheckPromise = null;
    this.monitoringInterval = null;
  }

  /**
   * Check if the backend is healthy and available.
   * 
   * @returns {Promise<boolean>} True if backend is healthy, false otherwise
   */
  async isBackendHealthy(): Promise<boolean> {
    const now = Date.now();
    
    // Return cached result if recent check was performed
    if (this.lastHealthCheck && (now - this.lastHealthCheck.timestamp) < this.healthCheckInterval) {
      return this.lastHealthCheck.isHealthy;
    }

    // Prevent multiple simultaneous health checks
    if (this.healthCheckPromise) {
      return this.healthCheckPromise;
    }

    this.healthCheckPromise = this._performHealthCheck();
    const result = await this.healthCheckPromise;
    this.healthCheckPromise = null;
    
    return result;
  }

  /**
   * Perform the actual health check against the backend.
   * 
   * @private
   * @returns {Promise<boolean>} Health status
   */
  private async _performHealthCheck(): Promise<boolean> {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout

      const response = await fetch(this.healthEndpoint, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        },
        signal: controller.signal
      });

      clearTimeout(timeoutId);

      // Check if response is JSON
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        console.warn('Health check returned non-JSON response');
        this._updateHealthStatus(false);
        return false;
      }

      if (response.ok) {
        const healthData: SystemStatusResponse = await response.json();
        const isHealthy = healthData.status === 'healthy';
        this._updateHealthStatus(isHealthy);
        return isHealthy;
      } else {
        console.warn(`Health check failed with status: ${response.status}`);
        this._updateHealthStatus(false);
        return false;
      }

    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('Health check failed:', errorMessage);
      this._updateHealthStatus(false);
      return false;
    }
  }

  /**
   * Update the cached health status.
   * 
   * @private
   * @param {boolean} isHealthy - Current health status
   */
  private _updateHealthStatus(isHealthy: boolean): void {
    this.lastHealthCheck = {
      timestamp: Date.now(),
      isHealthy: isHealthy
    };
    this.isHealthy = isHealthy;
  }

  /**
   * Force a fresh health check, bypassing cache.
   * 
   * @returns {Promise<boolean>} Fresh health status
   */
  async forceHealthCheck(): Promise<boolean> {
    this.lastHealthCheck = null;
    this.healthCheckPromise = null;
    return await this.isBackendHealthy();
  }

  /**
   * Get detailed system status information.
   * 
   * @returns {Promise<Record<string, unknown> | null>} System status data or null if unavailable
   */
  async getSystemStatus(): Promise<Record<string, unknown> | null> {
    try {
      const response = await fetch(`${this.baseURL}/status/`, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const contentType = response.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
          return await response.json() as Record<string, unknown>;
        }
      }
      
      return null;
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : 'Unknown error';
      console.error('System status check failed:', errorMessage);
      return null;
    }
  }

  /**
   * Start periodic health monitoring.
   * 
   * @param {number} interval - Check interval in milliseconds (default: 30000)
   */
  startMonitoring(interval: number = 30000): void {
    this.healthCheckInterval = interval;
    
    // Perform initial health check
    this.isBackendHealthy();
    
    // Set up periodic monitoring
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
    }
    
    this.monitoringInterval = setInterval(() => {
      this.forceHealthCheck();
    }, interval);
  }

  /**
   * Stop periodic health monitoring.
   */
  stopMonitoring(): void {
    if (this.monitoringInterval) {
      clearInterval(this.monitoringInterval);
      this.monitoringInterval = null;
    }
  }

  /**
   * Get the current cached health status without performing a check.
   * 
   * @returns {boolean} Last known health status
   */
  getCachedHealthStatus(): boolean {
    return this.isHealthy;
  }
}

// Export singleton instance
export const healthService = new HealthService();
export default healthService;