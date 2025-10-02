/**
 * Message Service - API calls for messaging functionality
 * Connects frontend to Django REST API backend
 */

const API_BASE_URL = 'http://localhost:8006/api';

// Types
export interface Message {
  id: number;
  content: string;
  sender: number;
  conversation: number;
  created_at: string;
  sender_name?: string;
  sender_avatar?: string;
  is_own_message?: boolean;
}

export interface Conversation {
  id: number;
  conversation_type: string;
  participants: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  }[];
  last_message?: Message;
  created_at: string;
  updated_at: string;
  unread_count?: number;
}

export interface CreateMessageData {
  content: string;
  conversation_id: number;
}

export interface CreateConversationData {
  participant_ids: number[];
  initial_message?: string;
}

// Helper function to get auth headers
const getAuthHeaders = () => {
  const token = localStorage.getItem('auth_token');
  return {
    'Content-Type': 'application/json',
    'Authorization': token ? `Bearer ${token}` : '',
  };
};

// API Functions
export const messageService = {
  // Get all conversations for current user
  getConversations: async (): Promise<Conversation[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/messaging/conversations/`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching conversations:', error);
      throw error;
    }
  },

  // Get messages for a specific conversation
  getMessages: async (conversationId: number): Promise<Message[]> => {
    try {
      const response = await fetch(`${API_BASE_URL}/messaging/conversations/${conversationId}/messages/`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching messages:', error);
      throw error;
    }
  },

  // Send a new message
  sendMessage: async (data: CreateMessageData): Promise<Message> => {
    try {
      const response = await fetch(`${API_BASE_URL}/messaging/messages/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          content: data.content,
          conversation: data.conversation_id
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  },

  // Create a new conversation
  createConversation: async (data: CreateConversationData): Promise<Conversation> => {
    try {
      const response = await fetch(`${API_BASE_URL}/messaging/conversations/`, {
        method: 'POST',
        headers: getAuthHeaders(),
        body: JSON.stringify({
          participant_ids: data.participant_ids,
          initial_message: data.initial_message,
        }),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error creating conversation:', error);
      throw error;
    }
  },

  // Mark messages as read
  markAsRead: async (conversationId: number): Promise<void> => {
    try {
      const response = await fetch(`${API_BASE_URL}/messaging/conversations/${conversationId}/mark_read/`, {
        method: 'POST',
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      console.error('Error marking messages as read:', error);
      throw error;
    }
  },

  // Get conversation details
  getConversation: async (conversationId: number): Promise<Conversation> => {
    try {
      const response = await fetch(`${API_BASE_URL}/messaging/conversations/${conversationId}/`, {
        method: 'GET',
        headers: getAuthHeaders(),
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('Error fetching conversation:', error);
      throw error;
    }
  },
};

export default messageService;