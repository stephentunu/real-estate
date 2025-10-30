/**
 * Unified API Client for Django REST API backend
 * Provides consistent request handling with proper authentication and error handling
 */

import { handleError, retryRequest } from "../utils/errorHandler";
import {
  APIValidationError,
  APIError,
  NetworkError,
  AuthenticationError,
} from "./errors";
import { healthService } from "./healthService";

// -------------------------
// API CONFIGURATION
// -------------------------
const API_CONFIG = {
  baseURL: "http://127.0.0.1:8000/api/v1/", // ✅ Ensure only one /api/v1 here
  timeout: 20000,
  retries: 3,
  retryDelay: 1000,
};

export interface APIResponse<T = unknown> {
  data: T;
  status: number;
  statusText: string;
  headers: Record<string, string>;
}

export interface RequestConfig {
  [key: string]: unknown;
  headers?: Record<string, string>;
  params?: Record<string, unknown>;
  timeout?: number;
  responseType?: "json" | "blob" | "text";
  retry?: boolean;
  retryCount?: number;
  retryDelay?: number;
  requiresAuth?: boolean;
}

/**
 * API Client
 */
class APIClient {
  private baseURL: string;
  private timeout: number;
  private retries: number;
  private retryDelay: number;

  constructor(config: typeof API_CONFIG) {
    this.baseURL = config.baseURL.replace(/\/+$/, ""); // Remove trailing slashes
    this.timeout = config.timeout;
    this.retries = config.retries;
    this.retryDelay = config.retryDelay;
  }

  /**
   * Build URL safely
   * Avoids double /api/v1/api/v1
   */
  private buildURL(endpoint: string): string {
    let cleanEndpoint = endpoint.trim();

    // Remove any leading /api or /api/v1 duplication from frontend calls
    cleanEndpoint = cleanEndpoint.replace(/^\/?api(\/v1)?\//, "");

    // Ensure leading slash for consistent joining
    if (!cleanEndpoint.startsWith("/")) {
      cleanEndpoint = "/" + cleanEndpoint;
    }

    return `${this.baseURL}${cleanEndpoint}`;
  }

  /**
   * Get auth headers
   */
  private getAuthHeaders(): Record<string, string> {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
    };

    const token = this.getAuthToken();
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const csrf = this.getCSRFToken();
    if (csrf) headers["X-CSRFToken"] = csrf;

    return headers;
  }

  private getCSRFToken(): string | null {
    const cookies = document.cookie.split(";");
    for (const cookie of cookies) {
      const [name, value] = cookie.trim().split("=");
      if (name === "csrftoken") return decodeURIComponent(value);
    }
    return null;
  }

  /**
   * Main request handler
   */
  private async request<T>(
    method: string,
    endpoint: string,
    data?: unknown,
    config?: RequestConfig
  ): Promise<T> {
    const url = this.buildURL(endpoint);

    // ✅ Health check with graceful handling
    let isHealthy = false;
    try {
      isHealthy = await healthService.isBackendHealthy();
    } catch (err) {
      console.warn("Health check skipped (timeout or network issue):", err);
    }

    if (!isHealthy) {
      throw new APIError(
        "Backend is not healthy. Request cancelled to prevent failures.",
        503,
        "BACKEND_UNHEALTHY"
      );
    }

    const headers = { ...this.getAuthHeaders(), ...(config?.headers || {}) };

    let body: BodyInit | null = null;
    if (data instanceof FormData) {
      delete headers["Content-Type"];
      body = data;
    } else if (data && typeof data === "object") {
      body = JSON.stringify(data);
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(
      () => controller.abort(),
      config?.timeout || this.timeout
    );

    try {
      const response = await fetch(url, {
        method,
        headers,
        body: method !== "GET" ? body : undefined,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);

      const contentType = response.headers.get("content-type") || "";

      if (!response.ok) {
        let errorData: any = {};
        try {
          errorData = contentType.includes("json")
            ? await response.json()
            : { message: await response.text() };
        } catch {
          errorData = { message: response.statusText };
        }

        if (response.status === 401)
          throw new AuthenticationError("Unauthorized", 401, errorData);
        if (response.status === 400)
          throw new APIValidationError("Bad Request", {}, 400);
        throw new APIError(
          `HTTP ${response.status}: ${response.statusText}`,
          response.status,
          "API_ERROR",
          errorData
        );
      }

      if (contentType.includes("application/json")) {
        return (await response.json()) as T;
      }
      if (contentType.includes("text/")) {
        return (await response.text()) as T;
      }

      return (await response.blob()) as T;
    } catch (error: any) {
      if (error.name === "AbortError") {
        throw new NetworkError("Request timed out", 408);
      }
      throw handleError(error);
    }
  }

  async get<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    const fn = () => this.request<T>("GET", endpoint, undefined, config);
    return config?.retry === false
      ? fn()
      : retryRequest(fn, {
          retries: config?.retryCount || this.retries,
          delay: config?.retryDelay || this.retryDelay,
        });
  }

  async post<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>("POST", endpoint, data, config);
  }

  async put<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>("PUT", endpoint, data, config);
  }

  async patch<T>(endpoint: string, data?: unknown, config?: RequestConfig): Promise<T> {
    return this.request<T>("PATCH", endpoint, data, config);
  }

  async delete<T>(endpoint: string, config?: RequestConfig): Promise<T> {
    return this.request<T>("DELETE", endpoint, undefined, config);
  }

  setAuthToken(token: string | null): void {
    if (token) localStorage.setItem("auth_token", token);
    else localStorage.removeItem("auth_token");
  }

  getAuthToken(): string | null {
    return localStorage.getItem("auth_token");
  }

  clearAuth(): void {
    localStorage.removeItem("auth_token");
  }

  isAuthenticated(): boolean {
    return !!this.getAuthToken();
  }
}

// Singleton instance
const apiClient = new APIClient(API_CONFIG);

export default apiClient;
