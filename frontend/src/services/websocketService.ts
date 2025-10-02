/**
 * WebSocket Service - Real-time communication client
 * Connects frontend to Django Channels WebSocket backend
 */

const WS_BASE_URL = 'ws://localhost:8006/ws';

// Types
export interface WebSocketMessage {
  type: string;
  data: Record<string, unknown>;
  timestamp?: string;
  sender?: string;
}

export interface ChatMessage {
  id: number;
  sender: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  };
  content: string;
  message_type: 'text' | 'image' | 'file' | 'system';
  timestamp: string;
  is_read: boolean;
  thread_id?: string;
}

export interface NotificationMessage {
  id: number;
  type: 'maintenance_request' | 'lease_update' | 'payment_due' | 'message' | 'system';
  title: string;
  message: string;
  data?: Record<string, unknown>;
  timestamp: string;
  is_read: boolean;
}

export interface WebSocketEventHandlers {
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  onMessage?: (message: WebSocketMessage) => void;
  onChatMessage?: (message: ChatMessage) => void;
  onNotification?: (notification: NotificationMessage) => void;
  onUserStatusUpdate?: (data: { user_id: number; status: 'online' | 'offline' }) => void;
  onMaintenanceUpdate?: (data: Record<string, unknown>) => void;
  onLeaseUpdate?: (data: Record<string, unknown>) => void;
  onPropertyUpdate?: (data: Record<string, unknown>) => void;
}

class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectInterval = 1000;
  private handlers: WebSocketEventHandlers = {};
  private isConnecting = false;
  private shouldReconnect = true;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private connectionTimeout: NodeJS.Timeout | null = null;

  /**
   * Connect to WebSocket server
   */
  connect(endpoint: string = '', handlers: WebSocketEventHandlers = {}): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.isConnecting || (this.ws && this.ws.readyState === WebSocket.CONNECTING)) {
        return;
      }

      this.isConnecting = true;
      this.handlers = { ...this.handlers, ...handlers };
      
      const token = localStorage.getItem('authToken');
      const wsUrl = `${WS_BASE_URL}/${endpoint}${token ? `?token=${token}` : ''}`;
      
      try {
        this.ws = new WebSocket(wsUrl);
        
        // Connection timeout
        this.connectionTimeout = setTimeout(() => {
          if (this.ws && this.ws.readyState === WebSocket.CONNECTING) {
            this.ws.close();
            reject(new Error('WebSocket connection timeout'));
          }
        }, 10000);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.isConnecting = false;
          this.reconnectAttempts = 0;
          
          if (this.connectionTimeout) {
            clearTimeout(this.connectionTimeout);
            this.connectionTimeout = null;
          }
          
          this.startHeartbeat();
          
          if (this.handlers.onConnect) {
            this.handlers.onConnect();
          }
          
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        this.ws.onclose = (event) => {
          console.log('WebSocket disconnected:', event.code, event.reason);
          this.isConnecting = false;
          this.stopHeartbeat();
          
          if (this.connectionTimeout) {
            clearTimeout(this.connectionTimeout);
            this.connectionTimeout = null;
          }
          
          if (this.handlers.onDisconnect) {
            this.handlers.onDisconnect();
          }
          
          if (this.shouldReconnect && event.code !== 1000) {
            this.attemptReconnect(endpoint);
          }
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          this.isConnecting = false;
          
          if (this.handlers.onError) {
            this.handlers.onError(error);
          }
          
          reject(error);
        };
        
      } catch (error) {
        this.isConnecting = false;
        reject(error);
      }
    });
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect(): void {
    this.shouldReconnect = false;
    this.stopHeartbeat();
    
    if (this.connectionTimeout) {
      clearTimeout(this.connectionTimeout);
      this.connectionTimeout = null;
    }
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
    }
  }

  /**
   * Send message through WebSocket
   */
  send(message: WebSocketMessage): boolean {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      try {
        this.ws.send(JSON.stringify(message));
        return true;
      } catch (error) {
        console.error('Error sending WebSocket message:', error);
        return false;
      }
    }
    console.warn('WebSocket is not connected');
    return false;
  }

  /**
   * Send chat message
   */
  sendChatMessage(content: string, recipientId?: number, threadId?: string): boolean {
    return this.send({
      type: 'chat_message',
      data: {
        content,
        recipient_id: recipientId,
        thread_id: threadId,
        message_type: 'text'
      }
    });
  }

  /**
   * Send typing indicator
   */
  sendTypingIndicator(isTyping: boolean, recipientId?: number, threadId?: string): boolean {
    return this.send({
      type: 'typing_indicator',
      data: {
        is_typing: isTyping,
        recipient_id: recipientId,
        thread_id: threadId
      }
    });
  }

  /**
   * Mark message as read
   */
  markMessageAsRead(messageId: number): boolean {
    return this.send({
      type: 'mark_read',
      data: {
        message_id: messageId
      }
    });
  }

  /**
   * Join room/channel
   */
  joinRoom(roomName: string): boolean {
    return this.send({
      type: 'join_room',
      data: {
        room: roomName
      }
    });
  }

  /**
   * Leave room/channel
   */
  leaveRoom(roomName: string): boolean {
    return this.send({
      type: 'leave_room',
      data: {
        room: roomName
      }
    });
  }

  /**
   * Subscribe to notifications
   */
  subscribeToNotifications(types: string[] = []): boolean {
    return this.send({
      type: 'subscribe_notifications',
      data: {
        notification_types: types
      }
    });
  }

  /**
   * Get connection status
   */
  getConnectionStatus(): 'connecting' | 'open' | 'closing' | 'closed' {
    if (!this.ws) return 'closed';
    
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return 'connecting';
      case WebSocket.OPEN:
        return 'open';
      case WebSocket.CLOSING:
        return 'closing';
      case WebSocket.CLOSED:
      default:
        return 'closed';
    }
  }

  /**
   * Check if WebSocket is connected
   */
  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  /**
   * Update event handlers
   */
  updateHandlers(handlers: Partial<WebSocketEventHandlers>): void {
    this.handlers = { ...this.handlers, ...handlers };
  }

  /**
   * Handle incoming WebSocket messages
   */
  private handleMessage(message: WebSocketMessage): void {
    // Call general message handler
    if (this.handlers.onMessage) {
      this.handlers.onMessage(message);
    }

    // Handle specific message types
    switch (message.type) {
      case 'chat_message':
        if (this.handlers.onChatMessage) {
          this.handlers.onChatMessage(message.data as unknown as ChatMessage);
        }
        break;
        
      case 'notification':
        if (this.handlers.onNotification) {
          this.handlers.onNotification(message.data as unknown as NotificationMessage);
        }
        break;
        
      case 'user_status_update':
        if (this.handlers.onUserStatusUpdate) {
          this.handlers.onUserStatusUpdate(message.data as { user_id: number; status: 'online' | 'offline' });
        }
        break;
        
      case 'maintenance_update':
        if (this.handlers.onMaintenanceUpdate) {
          this.handlers.onMaintenanceUpdate(message.data);
        }
        break;
        
      case 'lease_update':
        if (this.handlers.onLeaseUpdate) {
          this.handlers.onLeaseUpdate(message.data);
        }
        break;
        
      case 'property_update':
        if (this.handlers.onPropertyUpdate) {
          this.handlers.onPropertyUpdate(message.data);
        }
        break;
        
      case 'pong':
        // Heartbeat response - connection is alive
        break;
        
      default:
        console.log('Unhandled WebSocket message type:', message.type);
    }
  }

  /**
   * Attempt to reconnect to WebSocket
   */
  private attemptReconnect(endpoint: string): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.reconnectInterval * Math.pow(2, this.reconnectAttempts - 1);
    
    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (this.shouldReconnect) {
        this.connect(endpoint, this.handlers).catch((error) => {
          console.error('Reconnection failed:', error);
        });
      }
    }, delay);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.stopHeartbeat();
    
    this.heartbeatInterval = setInterval(() => {
      if (this.isConnected()) {
        this.send({ type: 'ping', data: {} });
      }
    }, 30000); // Send ping every 30 seconds
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }
}

// Create singleton instance
const websocketService = new WebSocketService();

// Convenience functions for common WebSocket endpoints
export const chatWebSocket = {
  connect: (handlers?: WebSocketEventHandlers) => websocketService.connect('chat/', handlers),
  disconnect: () => websocketService.disconnect(),
  sendMessage: (content: string, recipientId?: number, threadId?: string) => 
    websocketService.sendChatMessage(content, recipientId, threadId),
  sendTyping: (isTyping: boolean, recipientId?: number, threadId?: string) => 
    websocketService.sendTypingIndicator(isTyping, recipientId, threadId),
  markAsRead: (messageId: number) => websocketService.markMessageAsRead(messageId),
  isConnected: () => websocketService.isConnected(),
};

export const notificationWebSocket = {
  connect: (handlers?: WebSocketEventHandlers) => websocketService.connect('notifications/', handlers),
  disconnect: () => websocketService.disconnect(),
  subscribe: (types?: string[]) => websocketService.subscribeToNotifications(types),
  isConnected: () => websocketService.isConnected(),
};

export const maintenanceWebSocket = {
  connect: (handlers?: WebSocketEventHandlers) => websocketService.connect('maintenance/', handlers),
  disconnect: () => websocketService.disconnect(),
  joinProperty: (propertyId: number) => websocketService.joinRoom(`property_${propertyId}`),
  leaveProperty: (propertyId: number) => websocketService.leaveRoom(`property_${propertyId}`),
  isConnected: () => websocketService.isConnected(),
};

export { websocketService };
export default websocketService;