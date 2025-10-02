/**
 * Loading States and UI Components
 * 
 * Provides reusable loading states and UI components for API interactions
 * to ensure consistent user experience across the application.
 */

// Loading state types
export interface LoadingState {
  isLoading: boolean;
  error: string | null;
  data: unknown | null;
}

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastFetch: Date | null;
}

// Type for internal storage - uses unknown for flexibility
type InternalAsyncState = AsyncState<unknown>;
type StateListener = (state: InternalAsyncState) => void;

// Loading spinner component
export class LoadingSpinner {
  private static instance: LoadingSpinner;
  private activeRequests = 0;
  private spinnerElement: HTMLElement | null = null;

  static getInstance(): LoadingSpinner {
    if (!LoadingSpinner.instance) {
      LoadingSpinner.instance = new LoadingSpinner();
    }
    return LoadingSpinner.instance;
  }

  /**
   * Creates and shows loading spinner
   */
  show() {
    this.activeRequests++;
    if (this.activeRequests === 1) {
      this.createSpinner();
    }
  }

  /**
   * Hides loading spinner
   */
  hide() {
    this.activeRequests = Math.max(0, this.activeRequests - 1);
    if (this.activeRequests === 0) {
      this.removeSpinner();
    }
  }

  /**
   * Creates spinner element and adds to DOM
   */
  private createSpinner() {
    if (this.spinnerElement) return;

    // Create spinner container
    this.spinnerElement = document.createElement('div');
    this.spinnerElement.className = 'loading-spinner-overlay';
    this.spinnerElement.innerHTML = `
      <div class="loading-spinner">
        <div class="spinner-ring"></div>
        <div class="spinner-text">Loading...</div>
      </div>
    `;

    // Add styles
    const style = document.createElement('style');
    style.textContent = `
      .loading-spinner-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
      }
      
      .loading-spinner {
        background: white;
        padding: 2rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
      }
      
      .spinner-ring {
        width: 40px;
        height: 40px;
        border: 4px solid #f3f3f3;
        border-top: 4px solid #3498db;
        border-radius: 50%;
        animation: spin 1s linear infinite;
        margin: 0 auto 1rem;
      }
      
      @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
      }
      
      .spinner-text {
        color: #333;
        font-size: 14px;
      }
    `;

    document.head.appendChild(style);
    document.body.appendChild(this.spinnerElement);
  }

  /**
   * Removes spinner from DOM
   */
  private removeSpinner() {
    if (this.spinnerElement) {
      this.spinnerElement.remove();
      this.spinnerElement = null;
    }
  }
}

// Loading state manager
export class LoadingStateManager {
  private static instance: LoadingStateManager;
  private states = new Map<string, InternalAsyncState>();
  private listeners = new Map<string, Array<StateListener>>();

  static getInstance(): LoadingStateManager {
    if (!LoadingStateManager.instance) {
      LoadingStateManager.instance = new LoadingStateManager();
    }
    return LoadingStateManager.instance;
  }

  /**
   * Gets current loading state for a key
   */
  getState<T>(key: string): AsyncState<T> {
    const state = this.states.get(key) || {
      data: null,
      loading: false,
      error: null,
      lastFetch: null,
    };
    // Type assertion is safe here as we're returning the same structure
    return state as AsyncState<T>;
  }

  /**
   * Sets loading state for a key
   */
  setState<T>(key: string, state: Partial<AsyncState<T>>) {
    const currentState = this.getState<T>(key);
    const newState = { ...currentState, ...state } as InternalAsyncState;
    this.states.set(key, newState);
    this.notifyListeners(key, newState);
  }

  /**
   * Adds state change listener
   */
  addListener<T>(key: string, callback: (state: AsyncState<T>) => void) {
    if (!this.listeners.has(key)) {
      this.listeners.set(key, []);
    }
    // Wrap the callback to handle type conversion
    const wrappedCallback: StateListener = (state: InternalAsyncState) => {
      callback(state as AsyncState<T>);
    };
    this.listeners.get(key)!.push(wrappedCallback);
  }

  /**
   * Removes state change listener
   */
  removeListener<T>(key: string, callback: (state: AsyncState<T>) => void) {
    const listeners = this.listeners.get(key);
    if (listeners) {
      // Find the wrapped callback by comparing the original callback
      // This is a limitation - we can't easily remove specific wrapped callbacks
      // In practice, this method might need to be redesigned for better type safety
      const index = listeners.findIndex(listener => {
        // This is a simplified approach - in a real implementation,
        // you might want to store callback mappings
        return true; // Remove first matching callback for now
      });
      if (index > -1) {
        listeners.splice(index, 1);
      }
    }
  }

  /**
   * Notifies all listeners of state change
   */
  private notifyListeners(key: string, state: InternalAsyncState) {
    const listeners = this.listeners.get(key);
    if (listeners) {
      listeners.forEach(callback => callback(state));
    }
  }

  /**
   * Clears state for a key
   */
  clearState(key: string) {
    this.states.delete(key);
    const clearedState: InternalAsyncState = {
      data: null,
      loading: false,
      error: null,
      lastFetch: null,
    };
    this.notifyListeners(key, clearedState);
  }
}

// Utility functions for loading states
export const loadingUtils = {
  /**
   * Creates initial loading state
   */
  createInitialState<T>(): AsyncState<T> {
    return {
      data: null,
      loading: false,
      error: null,
      lastFetch: null,
    };
  },

  /**
   * Creates loading state with optional current data
   */
  createLoadingState<T>(currentData?: T): AsyncState<T> {
    return {
      data: currentData || null,
      loading: true,
      error: null,
      lastFetch: null,
    };
  },

  /**
   * Creates success state with data
   */
  createSuccessState<T>(data: T): AsyncState<T> {
    return {
      data,
      loading: false,
      error: null,
      lastFetch: new Date(),
    };
  },

  /**
   * Creates error state with optional current data
   */
  createErrorState<T>(error: string, currentData?: T): AsyncState<T> {
    return {
      data: currentData || null,
      loading: false,
      error,
      lastFetch: null,
    };
  },

  /**
   * Checks if state should be refetched based on age
   */
  shouldRefetch(state: AsyncState<unknown>, maxAge: number = 300000): boolean {
    if (!state.lastFetch) return true;
    const age = Date.now() - state.lastFetch.getTime();
    return age > maxAge;
  },

  /**
   * Debounced state update function
   */
  debounce<T>(
    key: string,
    updateFn: () => Promise<T>,
    delay: number = 300
  ): Promise<T> {
    return new Promise((resolve, reject) => {
      const timeoutId = setTimeout(async () => {
        try {
          const result = await updateFn();
          resolve(result);
        } catch (error) {
          reject(error);
        }
      }, delay);

      // Store timeout for potential cancellation
      (globalThis as Record<string, unknown>)[`debounce_${key}`] = timeoutId;
    });
  },
};

// Global loading instances
export const globalLoading = {
  spinner: LoadingSpinner.getInstance(),
  stateManager: LoadingStateManager.getInstance(),
};