import React, { useState, useEffect, useCallback } from 'react';
import { Send, Paperclip, Search, MoreVertical } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import DashboardLayout from '@/components/DashboardLayout';
import { messageService, Conversation, Message, CreateMessageData } from '@/services/messageService';
import { useToast } from '@/hooks/use-toast';
import { handleAPIError } from '@/services/errorHandler';

const MessagesPage = () => {
  const [selectedConversation, setSelectedConversation] = useState<number | null>(null);
  const [newMessage, setNewMessage] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(true);
  const [sendingMessage, setSendingMessage] = useState(false);
  const { toast } = useToast();

  // Load conversations on component mount
  useEffect(() => {
    loadConversations();
  }, [loadConversations]);

  // Load messages when conversation is selected
  useEffect(() => {
    if (selectedConversation) {
      loadMessages(selectedConversation);
    }
  }, [selectedConversation]);

  const loadConversations = useCallback(async () => {
    try {
      setLoading(true);
      const data = await messageService.getConversations();
      setConversations(data);
      
      // Auto-select first conversation if available
      if (data.length > 0 && !selectedConversation) {
        setSelectedConversation(data[0].id);
      }
    } catch (error) {
      handleAPIError(error, 'Loading conversations');
    } finally {
      setLoading(false);
    }
  }, [selectedConversation]);

  const loadMessages = async (conversationId: number) => {
    try {
      const data = await messageService.getMessages(conversationId);
      setMessages(data);
      
      // Mark messages as read
      await messageService.markAsRead(conversationId);
    } catch (error) {
      handleAPIError(error, 'Loading messages');
    }
  };

  const handleSendMessage = async () => {
    if (newMessage.trim() && selectedConversation) {
      try {
        setSendingMessage(true);
        
        const messageData: CreateMessageData = {
          content: newMessage.trim(),
          conversation_id: selectedConversation,
        };
        
        const sentMessage = await messageService.sendMessage(messageData);
        
        // Add the new message to the current messages
        setMessages(prev => [...prev, sentMessage]);
        setNewMessage('');
        
        // Refresh conversations to update last message
        loadConversations();
        
        toast({
          title: "Success",
          description: "Message sent successfully!",
        });
      } catch (error) {
        handleAPIError(error, 'Sending message');
      } finally {
        setSendingMessage(false);
      }
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const filteredConversations = conversations.filter(conv => {
    const participantNames = conv.participants
      .map(p => `${p.first_name} ${p.last_name}`.toLowerCase())
      .join(' ');
    return participantNames.includes(searchTerm.toLowerCase());
  });

  const selectedConversationData = conversations.find(c => c.id === selectedConversation);

  return (
    <DashboardLayout title="Messages">
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 h-[calc(100vh-200px)]">
        {/* Conversations List */}
        <div className="lg:col-span-1 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg overflow-hidden">
          <div className="p-4 border-b border-rental-100 dark:border-rental-800">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-rental-900 dark:text-rental-100">Messages</h2>
              <Button size="sm" variant="outline">
                <MoreVertical className="h-4 w-4" />
              </Button>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-rental-400 h-4 w-4" />
              <Input
                placeholder="Search conversations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
          </div>
          
          <div className="overflow-y-auto h-full">
            <div className="divide-y divide-rental-100 dark:divide-rental-800">
              {loading ? (
                <div className="p-4 text-center text-rental-500 dark:text-rental-400">
                  Loading conversations...
                </div>
              ) : filteredConversations.length === 0 ? (
                <div className="p-4 text-center text-rental-500 dark:text-rental-400">
                  {searchTerm ? 'No conversations found' : 'No conversations yet'}
                </div>
              ) : (
                filteredConversations.map((conversation) => {
                  const otherParticipants = conversation.participants.filter(p => p.id !== 1); // TODO: Get current user ID
                  const displayName = otherParticipants.length > 0 
                    ? `${otherParticipants[0].first_name} ${otherParticipants[0].last_name}`
                    : 'Unknown User';
                  
                  return (
                    <div
                      key={conversation.id}
                      onClick={() => setSelectedConversation(conversation.id)}
                      className={`p-4 border-b border-rental-100 dark:border-rental-800 cursor-pointer hover:bg-rental-50 dark:hover:bg-rental-800/50 transition-colors ${
                        selectedConversation === conversation.id ? 'bg-rental-100 dark:bg-rental-800' : ''
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className="relative">
                          <div className="w-12 h-12 rounded-full bg-rental-200 dark:bg-rental-700 flex items-center justify-center">
                            <span className="text-rental-600 dark:text-rental-300 font-medium">
                              {displayName.charAt(0).toUpperCase()}
                            </span>
                          </div>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center justify-between">
                            <h3 className="text-sm font-medium text-rental-900 dark:text-rental-100 truncate">
                              {displayName}
                            </h3>
                            <span className="text-xs text-rental-500 dark:text-rental-400">
                              {conversation.last_message ? new Date(conversation.last_message.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'}) : ''}
                            </span>
                          </div>
                          <div className="flex items-center justify-between mt-1">
                            <p className="text-sm text-rental-600 dark:text-rental-400 truncate">
                              {conversation.last_message?.content || 'No messages yet'}
                            </p>
                          </div>
                          <p className="text-xs text-rental-500 dark:text-rental-500 mt-1">
                            {new Date(conversation.updated_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </div>

        {/* Chat Area */}
        <div className="lg:col-span-2 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg overflow-hidden flex flex-col">
          {selectedConversationData ? (
            <>
              {/* Chat Header */}
              <div className="p-4 border-b border-rental-100 dark:border-rental-800">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-3">
                    <div className="w-10 h-10 rounded-full bg-rental-200 dark:bg-rental-700 flex items-center justify-center">
                      <span className="text-rental-600 dark:text-rental-300 font-medium">
                        {selectedConversationData.participants
                          .filter(p => p.id !== 1)[0]?.first_name.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-lg font-semibold text-rental-900 dark:text-rental-100">
                        {selectedConversationData.participants
                          .filter(p => p.id !== 1)
                          .map(p => `${p.first_name} ${p.last_name}`)
                          .join(', ') || 'Unknown User'}
                      </h3>
                      <p className="text-sm text-rental-500 dark:text-rental-400">Online</p>
                    </div>
                  </div>
                  <Button size="sm" variant="outline">
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-4 space-y-4">
                {messages.map((message) => {
                  const isCurrentUser = message.sender && typeof message.sender === 'object' && message.sender.id === 1; // TODO: Get current user ID
                  
                  return (
                    <div
                      key={message.id}
                      className={`flex items-start space-x-3 mb-4 ${
                        isCurrentUser ? 'flex-row-reverse space-x-reverse' : ''
                      }`}
                    >
                      {!isCurrentUser && (
                        <div className="w-8 h-8 rounded-full bg-rental-200 dark:bg-rental-700 flex items-center justify-center flex-shrink-0">
                          <span className="text-rental-600 dark:text-rental-300 text-xs font-medium">
                            {message.sender && typeof message.sender === 'object' && message.sender.first_name ? message.sender.first_name.charAt(0).toUpperCase() : '?'}
                          </span>
                        </div>
                      )}
                      <div
                        className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                          isCurrentUser
                            ? 'bg-rental-600 text-white'
                            : 'bg-rental-100 dark:bg-rental-800 text-rental-900 dark:text-rental-100'
                        }`}
                      >
                        <p className="text-sm">{message.content}</p>
                        <p
                          className={`text-xs mt-1 ${
                            isCurrentUser
                              ? 'text-rental-200'
                              : 'text-rental-500 dark:text-rental-400'
                          }`}
                        >
                          {new Date(message.created_at).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                        </p>
                      </div>
                    </div>
                  );
                })}
              </div>

              {/* Message Input */}
              <div className="p-4 border-t border-rental-100 dark:border-rental-800">
                <div className="flex items-end space-x-2">
                  <Button size="sm" variant="outline">
                    <Paperclip className="h-4 w-4" />
                  </Button>
                  <div className="flex-1">
                    <Textarea
                      placeholder="Type your message..."
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={handleKeyPress}
                      className="min-h-[40px] max-h-32 resize-none"
                      rows={1}
                    />
                  </div>
                  <Button 
                    onClick={handleSendMessage} 
                    size="sm"
                    disabled={sendingMessage || !newMessage.trim()}
                  >
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <div className="w-16 h-16 rounded-full bg-rental-100 dark:bg-rental-800 flex items-center justify-center mx-auto mb-4">
                  <Send className="h-8 w-8 text-rental-400" />
                </div>
                <h3 className="text-lg font-semibold text-rental-900 dark:text-rental-100 mb-2">
                  Select a conversation
                </h3>
                <p className="text-rental-500 dark:text-rental-400">
                  Choose a conversation from the list to start messaging
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
};

export default MessagesPage;