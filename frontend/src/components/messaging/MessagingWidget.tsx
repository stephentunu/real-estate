import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { MiniLoader } from '@/components/ui/mini-loader';
import { Badge } from '@/components/ui/badge';
import { MessageCircle, Send, X, Minimize2, ArrowLeft, Phone, Video, MoreVertical } from 'lucide-react';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';
import { format } from 'date-fns';
import messageService from '@/services/messageService';
import { handleAPIError } from '@/services/errorHandler';

interface Message {
  id: number;
  content: string;
  sender: number;
  conversation: number;
  created_at: string;
  sender_name?: string;
  sender_avatar?: string;
  is_own_message?: boolean;
}

interface Conversation {
  id: number;
  conversation_type: string;
  participants: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
  }[];
  last_message?: {
    id: number;
    content: string;
    sender_name?: string;
    created_at: string;
  };
  created_at: string;
  updated_at: string;
  unread_count?: number;
}

export const MessagingWidget: React.FC = () => {
  // All hooks must be at the top level
  const { user, profile } = useAuth();
  const [isOpen, setIsOpen] = useState(false);
  const [isMinimized, setIsMinimized] = useState(false);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeConversation, setActiveConversation] = useState<number | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { toast } = useToast();

  const fetchConversations = useCallback(async () => {
    if (!user) return;

    setIsLoading(true);
    try {
      const conversations = await messageService.getConversations();
      setConversations(conversations || []);
    } catch (error) {
      console.error('Error fetching conversations:', error);
      toast({
        title: "Error",
        description: "Failed to load conversations",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  }, [user, toast]);

  const setupRealtimeSubscription = useCallback(() => {
    if (!user) return;

    // TODO: Implement real-time messaging with Django Channels
    // For now, we'll rely on manual refresh when sending messages
    console.log('Real-time subscription setup - TODO: Implement with Django Channels');

    return () => {
      // Cleanup function for future real-time implementation
    };
  }, [user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (user) {
      fetchConversations();
      setupRealtimeSubscription();
    }
  }, [user, fetchConversations, setupRealtimeSubscription]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Early return after all hooks are called
  if (!user) {
    return null;
  }

  const fetchMessages = async (conversationId: number) => {
      setIsLoading(true);
      try {
        const messages = await messageService.getMessages(conversationId);
        setMessages(messages || []);
      } catch (error) {
        console.error('Error fetching messages:', error);
        toast({
          title: "Error",
          description: "Failed to load messages",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    const createSupportConversation = async () => {
      if (!user) return;

      setIsLoading(true);
      try {
        // Create support conversation using Django backend
        // For now, create conversation with just the current user
        // In a real implementation, you'd add support team member IDs
        const conversation = await messageService.createConversation({
          participant_ids: [user.id], // Add support team member IDs here
          initial_message: "Hello! I need support with my account."
        });

        setActiveConversation(conversation.id);
        setMessages([]);
        await fetchConversations();

        toast({
          title: "Support chat started",
          description: "You can now chat with our support team.",
        });
      } catch (error) {
        console.error('Error creating support conversation:', error);
        toast({
          title: "Error",
          description: "Failed to start support chat",
          variant: "destructive",
        });
      } finally {
        setIsLoading(false);
      }
    };

    const sendMessage = async (e: React.FormEvent) => {
      e.preventDefault();
      if (!newMessage.trim() || !activeConversation || !user) return;

      setIsSending(true);
      try {
        await messageService.sendMessage({
          conversation_id: activeConversation,
          content: newMessage.trim()
        });

        setNewMessage('');
        // Refresh messages to show the new message
        await fetchMessages(activeConversation);
      } catch (error) {
        console.error('Error sending message:', error);
        toast({
          title: "Error",
          description: "Failed to send message",
          variant: "destructive",
        });
      } finally {
        setIsSending(false);
      }
    };

    const handleConversationClick = (conversationId: number) => {
      setActiveConversation(conversationId);
      fetchMessages(conversationId);
      setUnreadCount(0);
    };

    const getCurrentConversation = () => {
      return conversations.find(conv => conv.id === activeConversation);
    };

    if (!user) return null;

    return (
      <>
        {/* Floating Button */}
        {!isOpen && (
          <Button
            onClick={() => setIsOpen(true)}
            className="fixed bottom-6 right-6 rounded-full w-14 h-14 shadow-lg hover:shadow-xl transition-all z-50 bg-primary"
            size="sm"
          >
            <MessageCircle className="h-6 w-6" />
            {unreadCount > 0 && (
              <Badge className="absolute -top-1 -right-1 h-5 w-5 rounded-full flex items-center justify-center text-xs">
                {unreadCount}
              </Badge>
            )}
          </Button>
        )}

        {/* Chat Window */}
        {isOpen && (
          <div className="fixed bottom-6 right-6 w-80 md:w-96 h-96 md:h-[500px] bg-white dark:bg-gray-900 rounded-lg shadow-xl border border-gray-200 dark:border-gray-700 flex flex-col z-50 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
              <h3 className="font-semibold text-gray-900 dark:text-white">
                {activeConversation ? getCurrentConversation()?.participants.map(p => p.first_name).join(', ') : 'Messages'}
              </h3>
              <div className="flex items-center space-x-2">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsMinimized(!isMinimized)}
                  className="h-8 w-8 p-0"
                >
                  <Minimize2 className="h-4 w-4" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setIsOpen(false)}
                  className="h-8 w-8 p-0"
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-hidden">
              {!activeConversation ? (
                <div className="p-4 space-y-4">
                  <div className="text-center">
                    <h4 className="font-medium text-gray-900 dark:text-white mb-2">Welcome to Messaging</h4>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                      Start a conversation with our support team
                    </p>
                  </div>
                  <Button
                    onClick={createSupportConversation}
                    disabled={isLoading}
                    className="w-full"
                  >
                    {isLoading ? (
                      <>
                        <MiniLoader size="sm" className="mr-2" />
                        Starting...
                      </>
                    ) : (
                      'Start Support Chat'
                    )}
                  </Button>
                </div>
              ) : (
                <div className="h-full flex flex-col">
                  {/* Messages */}
                  <div className="flex-1 overflow-y-auto p-4 space-y-3">
                    {messages.map((message) => (
                      <div
                        key={message.id}
                        className={cn(
                          'flex',
                          message.sender === user.id ? 'justify-end' : 'justify-start'
                        )}
                      >
                        <div
                          className={cn(
                            'max-w-[70%] rounded-lg px-3 py-2',
                            message.sender === user.id
                              ? 'bg-green-600 text-white'
                              : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-white'
                          )}
                        >
                          <p className="text-sm">{message.content}</p>
                          <p className={cn(
                            'text-xs mt-1',
                            message.sender === user.id ? 'text-green-100' : 'text-gray-500 dark:text-gray-400'
                          )}>
                            {format(new Date(message.created_at), 'p')}
                          </p>
                        </div>
                      </div>
                    ))}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Message Input */}
                  <form onSubmit={sendMessage} className="p-4 border-t border-gray-200 dark:border-gray-700">
                    <div className="flex space-x-2">
                      <Input
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        placeholder="Type a message..."
                        className="flex-1"
                        disabled={isSending}
                      />
                      <Button type="submit" disabled={isSending || !newMessage.trim()}>
                        {isSending ? (
                          <MiniLoader size="sm" />
                        ) : (
                          <Send className="h-4 w-4" />
                        )}
                      </Button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          </div>
        )}
      </>
    );
};