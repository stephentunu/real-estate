
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { User, Home, Heart, Calendar, Bell, CreditCard, Settings, TrendingUp, Building, MapPin, Eye } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import DashboardLayout from '@/components/DashboardLayout';
import { dashboardService, DashboardData } from '@/services/dashboardService';
import { handleAPIError } from '@/services/errorHandler';

const DashboardPage = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        setIsLoading(true);
        const data = await dashboardService.getDashboardData();
        setDashboardData(data);
        setError(null);
      } catch (err) {
        handleAPIError(err, 'Loading dashboard data');
        setError('Failed to load dashboard data');
      } finally {
        setIsLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  const quickActions = [
    { icon: User, label: 'Edit Profile', path: '/dashboard/profile', color: 'bg-blue-500' },
    { icon: Home, label: 'My Properties', path: '/dashboard/properties', color: 'bg-green-500' },
    { icon: Heart, label: 'Saved Properties', path: '/dashboard/saved', color: 'bg-red-500' },
    { icon: Calendar, label: 'Appointments', path: '/dashboard/appointments', color: 'bg-purple-500' },
    { icon: Bell, label: 'Notifications', path: '/dashboard/notifications', color: 'bg-yellow-500' },
    { icon: CreditCard, label: 'Payments', path: '/dashboard/payments', color: 'bg-indigo-500' },
    { icon: Settings, label: 'Settings', path: '/dashboard/settings', color: 'bg-gray-500' }
  ];

  // Show loading state
  if (isLoading) {
    return (
      <DashboardLayout title="Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-rental-600 mx-auto"></div>
            <p className="mt-2 text-muted-foreground">Loading dashboard...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // Show error state
  if (error) {
    return (
      <DashboardLayout title="Dashboard">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // Return early if no data
  if (!dashboardData) {
    return (
      <DashboardLayout title="Dashboard">
        <div className="flex items-center justify-center h-64">
          <p className="text-muted-foreground">No dashboard data available</p>
        </div>
      </DashboardLayout>
    );
  }

  const stats = [
    { icon: Building, label: 'Properties Listed', value: dashboardData.stats.totalProperties, color: 'text-blue-600' },
    { icon: Eye, label: 'Total Views', value: dashboardData.stats.totalViews.toLocaleString(), color: 'text-green-600' },
    { icon: Heart, label: 'Saved Properties', value: dashboardData.stats.savedProperties, color: 'text-red-600' },
    { icon: Calendar, label: 'Upcoming Appointments', value: dashboardData.stats.upcomingAppointments, color: 'text-purple-600' }
  ];

  return (
    <DashboardLayout title="Dashboard">
      <div className="space-y-6">
        {/* Welcome Message */}
        <div className="bg-gradient-to-r from-rental-500 to-rental-600 rounded-lg p-6 text-white">
          <h2 className="text-2xl font-bold mb-2">Welcome back, {dashboardData.user.name}!</h2>
          <p className="opacity-90">Here's what's happening with your properties today.</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {stats.map((stat, index) => (
            <Card key={index}>
              <CardContent className="p-6">
                <div className="flex items-center">
                  <stat.icon className={`h-8 w-8 ${stat.color} mr-3`} />
                  <div>
                    <p className="text-2xl font-bold">{stat.value}</p>
                    <p className="text-sm text-muted-foreground">{stat.label}</p>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Manage your account and properties</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4">
              {quickActions.map((action, index) => (
                <Link key={index} to={action.path}>
                  <div className="flex flex-col items-center p-4 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer">
                    <div className={`p-3 rounded-full ${action.color} text-white mb-2`}>
                      <action.icon className="h-6 w-6" />
                    </div>
                    <span className="text-sm font-medium text-center">{action.label}</span>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Recent Properties */}
        <Card>
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Recent Properties</CardTitle>
              <CardDescription>Your latest property listings</CardDescription>
            </div>
            <Button asChild variant="outline">
              <Link to="/dashboard/properties">View All</Link>
            </Button>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {dashboardData.recentProperties.length > 0 ? (
                dashboardData.recentProperties.map((property) => (
                  <div key={property.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-rental-100 dark:bg-rental-800 rounded-lg flex items-center justify-center">
                        <Home className="h-6 w-6 text-rental-600" />
                      </div>
                      <div>
                        <h3 className="font-medium">{property.title}</h3>
                        <div className="flex items-center text-sm text-muted-foreground">
                          <MapPin className="h-3 w-3 mr-1" />
                          {property.location}
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold">{property.price}</div>
                      <div className="flex items-center text-sm text-muted-foreground">
                        <Eye className="h-3 w-3 mr-1" />
                        {property.views} views
                      </div>
                    </div>
                    <Badge variant={property.status === 'Active' ? 'default' : 'secondary'}>
                      {property.status}
                    </Badge>
                  </div>
                ))
              ) : (
                <div className="text-center py-8 text-muted-foreground">
                  <Home className="h-12 w-12 mx-auto mb-4 opacity-50" />
                  <p>No recent properties found</p>
                  <Button className="mt-4" asChild>
                    <Link to="/list-property">List Your First Property</Link>
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default DashboardPage;
