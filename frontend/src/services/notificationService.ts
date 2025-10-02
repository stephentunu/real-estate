/**
 * Notification Service - API calls for notification management
 * Connects frontend to Django REST API backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1';

// Types
export interface NotificationType {
  id: number;
  name: string;
  description?: string;
  is_active: boolean;
  default_title_template: string;
  default_message_template: string;
  created_at: string;
  updated_at: string;
}

export interface Notification {
  id: number;
  recipient: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  notification_type: NotificationType;
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'urgent';
  is_read: boolean;
  read_at?: string;
  email_sent: boolean;
  email_sent_at?: string;
  push_sent: boolean;
  push_sent_at?: string;
  data?: Record<string, unknown>;
  expires_at?: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationPreference {
  id: number;
  user: number;
  notification_type: NotificationType;
  email_enabled: boolean;
  push_enabled: boolean;
  in_app_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  frequency: 'immediate' | 'daily' | 'weekly';
  created_at: string;
  updated_at: string;
}

export interface CreateNotificationData {
  recipient_id?: number;
  notification_type_id: number;
  title: string;
  message: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  data?: Record<string, unknown>;
  expires_at?: string;
}

export interface BulkNotificationData {
  recipient_ids: number[];
  notification_type_id: number;
  title: string;
  message: string;
  priority?: 'low' | 'medium' | 'high' | 'urgent';
  data?: Record<string, unknown>;
  expires_at?: string;
}

export interface NotificationFilters {
  [key: string]: string | number | boolean | undefined; // Add index signature for compatibility
  is_read?: boolean;
  notification_type?: number;
  priority?: string;
  created_after?: string;
  created_before?: string;
  search?: string;
  ordering?: string;
}

export interface NotificationStats {
  total_notifications: number;
  unread_notifications: number;
  notifications_by_type: { type: string; count: number }[];
  notifications_by_priority: { priority: string; count: number }[];
  recent_activity: Notification[];
}

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    ...(token && { 'Authorization': `Token ${token}` })
  };
};

// Helper function to handle API responses
const handleResponse = async (response: Response) => {
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
    throw new Error(errorData.detail || errorData.message || 'API request failed');
  }
  return response.json();
};

// Helper function to build query string
const buildQueryString = (params: Record<string, unknown>): string => {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value.toString());
    }
  });
  return searchParams.toString();
};

export const notificationService = {
  /**
   * Get user notifications with optional filters
   */
  getNotifications: async (filters?: NotificationFilters): Promise<{ results: Notification[]; count: number; next?: string; previous?: string }> => {
    const queryString = filters ? buildQueryString(filters) : '';
    const url = `${API_BASE_URL}/notifications/${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetch(url, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get notification by ID
   */
  getNotification: async (id: number): Promise<Notification> => {
    const response = await fetch(`${API_BASE_URL}/notifications/${id}/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Create new notification
   */
  createNotification: async (data: CreateNotificationData): Promise<Notification> => {
    const response = await fetch(`${API_BASE_URL}/notifications/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse(response);
  },

  /**
   * Create bulk notifications
   */
  createBulkNotifications: async (data: BulkNotificationData): Promise<{ created_count: number; notifications: Notification[] }> => {
    const response = await fetch(`${API_BASE_URL}/notifications/bulk-create/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse(response);
  },

  /**
   * Mark notification as read
   */
  markAsRead: async (id: number): Promise<Notification> => {
    const response = await fetch(`${API_BASE_URL}/notifications/${id}/mark-read/`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Mark notification as unread
   */
  markAsUnread: async (id: number): Promise<Notification> => {
    const response = await fetch(`${API_BASE_URL}/notifications/${id}/mark-unread/`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Mark all notifications as read
   */
  markAllAsRead: async (): Promise<{ updated_count: number }> => {
    const response = await fetch(`${API_BASE_URL}/notifications/mark-all-read/`, {
      method: 'POST',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Delete notification
   */
  deleteNotification: async (id: number): Promise<void> => {
    const response = await fetch(`${API_BASE_URL}/notifications/${id}/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: 'Network error' }));
      throw new Error(errorData.detail || errorData.message || 'Failed to delete notification');
    }
  },

  /**
   * Get unread notifications count
   */
  getUnreadCount: async (): Promise<{ count: number }> => {
    const response = await fetch(`${API_BASE_URL}/notifications/unread-count/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get notification statistics
   */
  getStats: async (): Promise<NotificationStats> => {
    const response = await fetch(`${API_BASE_URL}/notifications/stats/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get notification types
   */
  getNotificationTypes: async (): Promise<NotificationType[]> => {
    const response = await fetch(`${API_BASE_URL}/notifications/types/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Get user notification preferences
   */
  getPreferences: async (): Promise<NotificationPreference[]> => {
    const response = await fetch(`${API_BASE_URL}/notifications/preferences/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Update notification preference
   */
  updatePreference: async (id: number, data: Partial<NotificationPreference>): Promise<NotificationPreference> => {
    const response = await fetch(`${API_BASE_URL}/notifications/preferences/${id}/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify(data),
    });

    return handleResponse(response);
  },

  /**
   * Update multiple notification preferences
   */
  updatePreferences: async (preferences: { id: number; data: Partial<NotificationPreference> }[]): Promise<NotificationPreference[]> => {
    const response = await fetch(`${API_BASE_URL}/notifications/preferences/bulk-update/`, {
      method: 'PATCH',
      headers: getAuthHeaders(),
      body: JSON.stringify({ preferences }),
    });

    return handleResponse(response);
  },

  /**
   * Test notification delivery
   */
  testNotification: async (notificationTypeId: number, channels: string[]): Promise<{ message: string }> => {
    const response = await fetch(`${API_BASE_URL}/notifications/test/`, {
      method: 'POST',
      headers: getAuthHeaders(),
      body: JSON.stringify({
        notification_type_id: notificationTypeId,
        channels
      }),
    });

    return handleResponse(response);
  },

  /**
   * Subscribe to real-time notifications (WebSocket)
   */
  subscribeToNotifications: (onNotification: (notification: Notification) => void): WebSocket | null => {
    const token = localStorage.getItem('auth_token');
    if (!token) {
      console.error('No auth token found for WebSocket connection');
      return null;
    }

    const wsUrl = `ws://localhost:8006/ws/notifications/?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('Connected to notification WebSocket');
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'notification' && data.notification) {
          onNotification(data.notification);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log('Disconnected from notification WebSocket');
    };

    return ws;
  },

  /**
   * Get recent notifications (last 10)
   */
  getRecentNotifications: async (): Promise<Notification[]> => {
    const response = await fetch(`${API_BASE_URL}/notifications/recent/`, {
      method: 'GET',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },

  /**
   * Clear all read notifications
   */
  clearReadNotifications: async (): Promise<{ deleted_count: number }> => {
    const response = await fetch(`${API_BASE_URL}/notifications/clear-read/`, {
      method: 'DELETE',
      headers: getAuthHeaders(),
    });

    return handleResponse(response);
  },
};

export default notificationService;