/**
 * Error Boundaries for Frontend Application
 * 
 * Provides comprehensive error handling and recovery mechanisms
 * for API failures, JavaScript errors, and network issues.
 */

import { APIError } from '../services/errors.js';

// Error boundary configuration
interface ErrorBoundaryConfig {
  fallback?: (error: Error, info: ErrorInfo) => HTMLElement;
  onError?: (error: Error, info: ErrorInfo) => void;
  retryable?: boolean;
  maxRetries?: number;
}

interface ErrorInfo {
  componentStack?: string;
  url?: string;
  timestamp: Date;
  userAgent?: string;
}

// Simple error handler class
class ErrorHandler {
  logError(error: Error, info: ErrorInfo) {
    console.error('Error logged:', error, info);
  }
  
  handleAPIError(error: Error | APIError) {
    console.error('API Error:', error);
  }
}

// Base error boundary class
export class ErrorBoundary {
  private static instance: ErrorBoundary;
  private activeBoundaries = new Map<string, ErrorBoundaryInstance>();
  private globalErrorHandler: ErrorHandler;
  
  constructor() {
    this.globalErrorHandler = new ErrorHandler();
  }

  static getInstance(): ErrorBoundary {
    if (!ErrorBoundary.instance) {
      ErrorBoundary.instance = new ErrorBoundary();
    }
    return ErrorBoundary.instance;
  }

  /**
   * Initializes global error handling
   */
  initializeGlobalHandler() {
    if (this.globalErrorHandler) return;

    this.globalErrorHandler = new ErrorHandler();

    // Global error handlers
    if (typeof window !== 'undefined') {
      window.addEventListener('error', this.handleGlobalError.bind(this));
      window.addEventListener('unhandledrejection', this.handleUnhandledRejection.bind(this));
      
      // Network error handler
      window.addEventListener('offline', this.handleNetworkOffline.bind(this));
      window.addEventListener('online', this.handleNetworkOnline.bind(this));
    }
  }

  /**
   * Creates a new error boundary instance
   */
  createBoundary(
    id: string,
    config: ErrorBoundaryConfig = {}
  ): ErrorBoundaryInstance {
    const boundary = new ErrorBoundaryInstance(id, config);
    this.activeBoundaries.set(id, boundary);
    return boundary;
  }

  /**
   * Removes an error boundary instance
   */
  removeBoundary(id: string) {
    this.activeBoundaries.delete(id);
  }

  /**
   * Handles global JavaScript errors
   */
  private handleGlobalError(event: ErrorEvent) {
    const errorInfo: ErrorInfo = {
      componentStack: event.filename,
      url: window.location.href,
      timestamp: new Date(),
      userAgent: navigator.userAgent,
    };

    console.error('Global error:', event.error, errorInfo);
    
    if (this.globalErrorHandler) {
      this.globalErrorHandler.logError(event.error, errorInfo);
    }

    // Show global error notification
    this.showGlobalErrorNotification(
      'An unexpected error occurred. Please refresh the page.',
      event.error
    );
  }

  /**
   * Handles unhandled promise rejections
   */
  private handleUnhandledRejection(event: PromiseRejectionEvent) {
    const error = event.reason instanceof Error ? event.reason : new Error(String(event.reason));
    const errorInfo: ErrorInfo = {
      url: window.location.href,
      timestamp: new Date(),
      userAgent: navigator.userAgent,
    };

    console.error('Unhandled promise rejection:', error, errorInfo);
    
    if (this.globalErrorHandler) {
      this.globalErrorHandler.logError(error, errorInfo);
    }

    // Show user-friendly error
    if (error instanceof APIError) {
      this.showAPIErrorNotification(error);
    } else {
      this.showGlobalErrorNotification(
        'An unexpected error occurred. Please try again.',
        error
      );
    }
  }

  /**
   * Handles network offline events
   */
  private handleNetworkOffline() {
    this.showGlobalErrorNotification(
      'You appear to be offline. Please check your internet connection.',
      new Error('Network offline')
    );
  }

  /**
   * Handles network online events
   */
  private handleNetworkOnline() {
    this.hideGlobalErrorNotification();
    this.showSuccessNotification('You are back online!');
  }

  /**
   * Shows API error notification
   */
  private showAPIErrorNotification(error: APIError) {
    const message = this.getUserFriendlyMessage(error);
    this.showErrorNotification(message, error);
  }

  /**
   * Shows global error notification
   */
  private showGlobalErrorNotification(message: string, error: Error) {
    this.showErrorNotification(message, error);
  }

  /**
   * Shows error notification
   */
  private showErrorNotification(message: string, error: Error) {
    const notification = this.createNotification('error', message, error);
    document.body.appendChild(notification);
    
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 5000);
  }

  /**
   * Shows success notification
   */
  private showSuccessNotification(message: string) {
    const notification = this.createNotification('success', message);
    document.body.appendChild(notification);
    
    setTimeout(() => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    }, 3000);
  }

  /**
   * Hides global error notification
   */
  private hideGlobalErrorNotification() {
    const notifications = document.querySelectorAll('.error-notification');
    notifications.forEach(notification => {
      if (notification.parentNode) {
        notification.parentNode.removeChild(notification);
      }
    });
  }

  /**
   * Creates notification element
   */
  private createNotification(type: 'error' | 'success', message: string, error?: Error): HTMLElement {
    const notification = document.createElement('div');
    notification.className = `error-notification error-notification-${type}`;
    
    const icon = type === 'error' ? '⚠️' : '✅';
    
    notification.innerHTML = `
      <div class="notification-content">
        <span class="notification-icon">${icon}</span>
        <span class="notification-message">${message}</span>
        ${error ? `<button class="notification-details" onclick="console.error('Error:', ${JSON.stringify(error.message)})">Details</button>` : ''}
      </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      .error-notification {
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        z-index: 10000;
        max-width: 400px;
        animation: slideIn 0.3s ease-out;
      }

      .error-notification-error {
        background: #fee;
        border: 1px solid #fcc;
        color: #c33;
      }

      .error-notification-success {
        background: #efe;
        border: 1px solid #cfc;
        color: #3c3;
      }

      .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
      }

      .notification-message {
        flex: 1;
        font-size: 0.9rem;
      }

      .notification-details {
        background: none;
        border: none;
        color: inherit;
        text-decoration: underline;
        cursor: pointer;
        font-size: 0.8rem;
      }

      @keyframes slideIn {
        from {
          transform: translateX(100%);
          opacity: 0;
        }
        to {
          transform: translateX(0);
          opacity: 1;
        }
      }
    `;

    document.head.appendChild(style);
    return notification;
  }

  /**
   * Gets user-friendly error message
   */
  private getUserFriendlyMessage(error: APIError): string {
    switch (error.code) {
      case 'VALIDATION_ERROR':
        return 'Please check your input and try again.';
      case 'AUTH_REQUIRED':
        return 'Please log in to continue.';
      case 'PERMISSION_DENIED':
        return 'You don\'t have permission to perform this action.';
      case 'NOT_FOUND':
        return 'The requested resource was not found.';
      case 'RATE_LIMITED':
        return 'Too many requests. Please try again later.';
      case 'NETWORK_ERROR':
        return 'Network error. Please check your connection.';
      case 'SERVER_ERROR':
        return 'Server error. Please try again later.';
      default:
        return error.message || 'An unexpected error occurred.';
    }
  }
}

// Individual error boundary instance
export class ErrorBoundaryInstance {
  private hasError = false;
  private error: Error | null = null;
  private errorInfo: ErrorInfo | null = null;
  private retryCount = 0;

  constructor(
    private id: string,
    private config: ErrorBoundaryConfig
  ) {}

  /**
   * Handles error within the boundary
   */
  handleError(error: Error, errorInfo?: ErrorInfo) {
    this.hasError = true;
    this.error = error;
    this.errorInfo = errorInfo || {
      url: window.location.href,
      timestamp: new Date(),
    };

    console.error(`Error in boundary ${this.id}:`, error, this.errorInfo);

    if (this.config.onError) {
      this.config.onError(error, this.errorInfo);
    }

    return this.renderError();
  }

  /**
   * Resets the error boundary
   */
  reset() {
    this.hasError = false;
    this.error = null;
    this.errorInfo = null;
    this.retryCount = 0;
  }

  /**
   * Attempts to retry the failed operation
   */
  async retry(operation: () => Promise<void>): Promise<void> {
    if (this.retryCount >= (this.config.maxRetries || 3)) {
      throw new Error('Maximum retry attempts reached');
    }

    this.retryCount++;
    this.reset();

    try {
      await operation();
    } catch (error) {
      this.handleError(error instanceof Error ? error : new Error(String(error)));
      throw error;
    }
  }

  /**
   * Renders error fallback UI
   */
  private renderError(): HTMLElement {
    if (this.config.fallback && this.error && this.errorInfo) {
      return this.config.fallback(this.error, this.errorInfo);
    }

    return this.createDefaultErrorUI();
  }

  /**
   * Creates default error UI
   */
  private createDefaultErrorUI(): HTMLElement {
    const container = document.createElement('div');
    container.className = 'error-boundary-fallback';
    
    container.innerHTML = `
      <div class="error-content">
        <h3>Something went wrong</h3>
        <p>We encountered an unexpected error. Please try again.</p>
        ${this.config.retryable !== false ? '<button class="retry-button">Retry</button>' : ''}
        <button class="reset-button">Reset</button>
      </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      .error-boundary-fallback {
        padding: 2rem;
        text-align: center;
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        margin: 1rem 0;
      }

      .error-content h3 {
        color: #dc3545;
        margin-bottom: 0.5rem;
      }

      .error-content p {
        color: #6c757d;
        margin-bottom: 1rem;
      }

      .retry-button, .reset-button {
        padding: 0.5rem 1rem;
        margin: 0 0.5rem;
        border: none;
        border-radius: 4px;
        cursor: pointer;
      }

      .retry-button {
        background: #007bff;
        color: white;
      }

      .reset-button {
        background: #6c757d;
        color: white;
      }
    `;

    document.head.appendChild(style);

    // Add event listeners
    const retryBtn = container.querySelector('.retry-button');
    const resetBtn = container.querySelector('.reset-button');

    if (retryBtn) {
      retryBtn.addEventListener('click', () => {
        // Retry logic would be handled by the component using this boundary
        this.reset();
      });
    }

    if (resetBtn) {
      resetBtn.addEventListener('click', () => {
        this.reset();
        window.location.reload();
      });
    }

    return container;
  }
}

// Initialize global error handling
export const errorBoundary = ErrorBoundary.getInstance();
if (typeof window !== 'undefined') {
  errorBoundary.initializeGlobalHandler();
}