import { 
  toastAPIError, 
  toastError, 
  toastNetworkOffline, 
  toastNetworkOnline,
  toastSuccess 
} from '@/hooks/use-toast'

/**
 * Service class for handling toast notifications
 * Provides a clean abstraction layer that can be easily mocked in tests
 */
export class ToastService {
  /**
   * Show API error toast
   */
  public showAPIError(error: unknown, context?: string): void {
    toastAPIError(error, context)
  }

  /**
   * Show general error toast
   */
  public showError(title: string, message?: string): void {
    toastError(title, message)
  }

  /**
   * Show network offline toast
   */
  public showNetworkOffline(): void {
    toastNetworkOffline()
  }

  /**
   * Show network online toast
   */
  public showNetworkOnline(): void {
    toastNetworkOnline()
  }

  /**
   * Show success toast
   */
  public showSuccess(title: string, message?: string): void {
    toastSuccess(title, message)
  }
}

// Export singleton instance
export const toastService = new ToastService()