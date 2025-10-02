
import React, { useState } from 'react';
import { Bell, CheckCheck, Trash, Calendar, Heart, MessageCircle, Home, User, Filter } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import DashboardLayout from '@/components/DashboardLayout';
import { useToast } from '@/hooks/use-toast';
import { Link } from 'react-router-dom';

interface Notification {
  id: string;
  title: string;
  message: string;
  date: string;
  read: boolean;
  type: 'appointment' | 'message' | 'property' | 'system' | 'account';
  relatedId?: string;
  action?: string;
}

const NotificationsPage = () => {
  const { toast } = useToast();
  
  // Mock notifications data
  const [notifications, setNotifications] = useState<Notification[]>([
    {
      id: '1',
      title: 'Appointment Confirmed',
      message: 'Your appointment to view Luxury Apartment in Westlands has been confirmed for June 15, 2023 at 10:00 AM.',
      date: '2023-06-10T14:30:00',
      read: false,
      type: 'appointment',
      relatedId: '1',
      action: '/dashboard/appointments'
    },
    {
      id: '2',
      title: 'New Message',
      message: 'You have received a new message from Sarah Omondi regarding your inquiry about Modern Townhouse in Kilimani.',
      date: '2023-06-09T09:15:00',
      read: false,
      type: 'message',
      relatedId: '2',
      action: '/dashboard/messages'
    },
    {
      id: '3',
      title: 'Property Status Update',
      message: 'Your property listing "Office Space in CBD" is now under review. We will notify you once it is approved.',
      date: '2023-06-07T11:45:00',
      read: true,
      type: 'property',
      relatedId: '3',
      action: '/dashboard/properties'
    },
    {
      id: '4',
      title: 'Welcome to Jaston',
      message: 'Thank you for registering with Jaston. Start exploring properties or list your own property today!',
      date: '2023-06-01T08:00:00',
      read: true,
      type: 'system'
    },
    {
      id: '5',
      title: 'Profile Information',
      message: 'Please complete your profile information to get personalized property recommendations.',
      date: '2023-06-01T08:05:00',
      read: true,
      type: 'account',
      action: '/dashboard/profile'
    }
  ]);

  const markAsRead = (id: string) => {
    setNotifications(notifications.map(notification => 
      notification.id === id ? {...notification, read: true} : notification
    ));
  };

  const markAllAsRead = () => {
    setNotifications(notifications.map(notification => ({...notification, read: true})));
    toast({
      title: "All notifications marked as read",
      description: "All your notifications have been marked as read."
    });
  };

  const deleteNotification = (id: string) => {
    setNotifications(notifications.filter(notification => notification.id !== id));
    toast({
      title: "Notification deleted",
      description: "The notification has been deleted."
    });
  };

  const clearAllNotifications = () => {
    setNotifications([]);
    toast({
      title: "All notifications cleared",
      description: "All your notifications have been cleared."
    });
  };

  const getNotificationIcon = (type: string) => {
    switch(type) {
      case 'appointment':
        return <Calendar className="h-6 w-6" />;
      case 'message':
        return <MessageCircle className="h-6 w-6" />;
      case 'property':
        return <Home className="h-6 w-6" />;
      case 'account':
        return <User className="h-6 w-6" />;
      default:
        return <Bell className="h-6 w-6" />;
    }
  };

  const getNotificationColor = (type: string) => {
    switch(type) {
      case 'appointment':
        return "bg-blue-100 text-blue-600";
      case 'message':
        return "bg-green-100 text-green-600";
      case 'property':
        return "bg-purple-100 text-purple-600";
      case 'account':
        return "bg-yellow-100 text-yellow-600";
      default:
        return "bg-gray-100 text-gray-600";
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) {
      return 'Today, ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInDays === 1) {
      return 'Yesterday, ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    } else if (diffInDays < 7) {
      return diffInDays + ' days ago';
    } else {
      return date.toLocaleDateString([], { year: 'numeric', month: 'short', day: 'numeric' });
    }
  };

  const unreadCount = notifications.filter(notification => !notification.read).length;
  
  const filterNotifications = (filter: string) => {
    if (filter === 'all') return notifications;
    if (filter === 'unread') return notifications.filter(notification => !notification.read);
    return notifications.filter(notification => notification.type === filter);
  };

  return (
    <DashboardLayout title="Notifications">
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
        <div>
          {unreadCount > 0 && (
            <Badge variant="outline" className="bg-primary/10 text-primary mr-2">
              {unreadCount} unread
            </Badge>
          )}
        </div>
        <div className="flex gap-2">
          {unreadCount > 0 && (
            <Button variant="outline" size="sm" onClick={markAllAsRead}>
              <CheckCheck className="h-4 w-4 mr-1" />
              Mark all as read
            </Button>
          )}
          {notifications.length > 0 && (
            <Button variant="outline" size="sm" className="text-red-500 hover:text-red-600 hover:bg-red-50" onClick={clearAllNotifications}>
              <Trash className="h-4 w-4 mr-1" />
              Clear all
            </Button>
          )}
        </div>
      </div>

      {notifications.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
          <Bell className="h-12 w-12 mx-auto text-rental-400" />
          <h3 className="mt-4 text-lg font-medium">No notifications</h3>
          <p className="mt-2 text-rental-600 dark:text-rental-400">
            You don't have any notifications at the moment. We'll notify you of important updates.
          </p>
        </div>
      ) : (
        <Tabs defaultValue="all">
          <TabsList className="mb-4">
            <TabsTrigger value="all">All</TabsTrigger>
            <TabsTrigger value="unread">Unread</TabsTrigger>
            <TabsTrigger value="appointment">Appointments</TabsTrigger>
            <TabsTrigger value="property">Properties</TabsTrigger>
            <TabsTrigger value="message">Messages</TabsTrigger>
          </TabsList>
          
          {['all', 'unread', 'appointment', 'property', 'message'].map((filter) => (
            <TabsContent value={filter} key={filter}>
              {filterNotifications(filter).length === 0 ? (
                <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
                  <Bell className="h-12 w-12 mx-auto text-rental-400" />
                  <h3 className="mt-4 text-lg font-medium">No {filter} notifications</h3>
                  <p className="mt-2 text-rental-600 dark:text-rental-400">
                    You don't have any {filter === 'unread' ? 'unread' : filter} notifications.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {filterNotifications(filter).map((notification) => (
                    <Card 
                      key={notification.id} 
                      className={`overflow-hidden transition-colors ${!notification.read ? 'bg-primary/5 border-primary/20' : ''}`}
                    >
                      <CardContent className="p-4">
                        <div className="flex">
                          <div className={`flex-shrink-0 rounded-full p-2 mr-4 ${getNotificationColor(notification.type)}`}>
                            {getNotificationIcon(notification.type)}
                          </div>
                          <div className="flex-grow">
                            <div className="flex justify-between items-start">
                              <div>
                                <h3 className={`font-semibold ${!notification.read ? 'text-primary' : ''}`}>
                                  {notification.title}
                                </h3>
                                <p className="text-rental-600 dark:text-rental-400 mt-1">
                                  {notification.message}
                                </p>
                                <p className="text-sm text-rental-500 mt-2">
                                  {formatDate(notification.date)}
                                </p>
                              </div>
                              <div className="flex items-center space-x-1">
                                {!notification.read && (
                                  <Button 
                                    variant="ghost" 
                                    size="sm" 
                                    className="text-primary hover:text-primary/80"
                                    onClick={() => markAsRead(notification.id)}
                                  >
                                    <CheckCheck className="h-4 w-4" />
                                  </Button>
                                )}
                                <Button 
                                  variant="ghost" 
                                  size="sm"
                                  className="text-red-500 hover:text-red-600"
                                  onClick={() => deleteNotification(notification.id)}
                                >
                                  <Trash className="h-4 w-4" />
                                </Button>
                              </div>
                            </div>
                            {notification.action && (
                              <div className="mt-3">
                                <Button asChild size="sm">
                                  <Link to={notification.action}>
                                    View Details
                                  </Link>
                                </Button>
                              </div>
                            )}
                          </div>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>
          ))}
        </Tabs>
      )}
    </DashboardLayout>
  );
};

export default NotificationsPage;
