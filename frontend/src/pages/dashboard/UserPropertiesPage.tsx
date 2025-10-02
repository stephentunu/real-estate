
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Home, Plus, Eye, Edit, Trash, MapPin, Bed, Bath, Square, Calendar, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import DashboardLayout from '@/components/DashboardLayout';
import { useToast } from '@/hooks/use-toast';
import { handleAPIError } from '@/services/errorHandler';
import { propertyService, PropertyListItem } from '@/services/propertyService';

const UserPropertiesPage = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [properties, setProperties] = useState<PropertyListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch user properties on component mount
  useEffect(() => {
    const fetchUserProperties = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const userProperties = await propertyService.getUserProperties();
        setProperties(userProperties);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load properties');
        handleAPIError(err, 'Loading your properties');
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserProperties();
  }, []);

  const handleDeleteProperty = async (id: string) => {
    try {
      await propertyService.deleteProperty(parseInt(id));
      // Remove the property from local state
      setProperties(prev => prev.filter(property => property.id.toString() !== id));
      toast({
        title: "Property deleted",
        description: "The property has been removed from your listings.",
      });
    } catch (err) {
      handleAPIError(err, 'Deleting property');
    }
  };

  const filteredProperties = (status: string) => {
    return properties
      .filter(property => {
        // Check if property.status exists before accessing its properties
        if (!property.status || !property.status.name) {
          return false;
        }
        
        // Map API status to component status
        const propertyStatus = property.status.name.toLowerCase();
        const targetStatus = status.toLowerCase();
        
        // Map status names (adjust based on your backend status names)
        if (targetStatus === 'active' && (propertyStatus === 'active' || propertyStatus === 'available')) return true;
        if (targetStatus === 'pending' && (propertyStatus === 'pending' || propertyStatus === 'under_review')) return true;
        if (targetStatus === 'draft' && propertyStatus === 'draft') return true;
        
        return false;
      })
      .filter(property => {
        const searchLower = searchQuery.toLowerCase();
        const fullAddress = `${property.address || ''}, ${property.city || ''}, ${property.state || ''}`;
        return (property.title || '').toLowerCase().includes(searchLower) ||
               fullAddress.toLowerCase().includes(searchLower);
      });
  };

  // Show loading state
  if (isLoading) {
    return (
      <DashboardLayout title="My Properties">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <Loader2 className="h-8 w-8 animate-spin mx-auto mb-4 text-rental-600" />
            <p className="text-muted-foreground">Loading your properties...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  // Show error state
  if (error) {
    return (
      <DashboardLayout title="My Properties">
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <p className="text-red-600 mb-4">{error}</p>
            <Button onClick={() => window.location.reload()}>Try Again</Button>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout title="My Properties">
      <div className="mb-6 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div className="relative w-full sm:w-auto">
          <Input
            placeholder="Search properties..."
            className="pl-10 w-full sm:w-[300px]"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
        <Button asChild>
          <Link to="/list-property">
            <Plus className="h-4 w-4 mr-2" />
            Add New Property
          </Link>
        </Button>
      </div>

      <Tabs defaultValue="active">
        <TabsList className="mb-4">
          <TabsTrigger value="active">Active ({filteredProperties('active').length})</TabsTrigger>
          <TabsTrigger value="pending">Pending ({filteredProperties('pending').length})</TabsTrigger>
          <TabsTrigger value="draft">Drafts ({filteredProperties('draft').length})</TabsTrigger>
        </TabsList>
        
        {['active', 'pending', 'draft'].map((status) => (
          <TabsContent value={status} key={status}>
            {!filteredProperties(status) || filteredProperties(status).length === 0 ? (
              <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
                <Home className="h-12 w-12 mx-auto text-rental-400" />
                <h3 className="mt-4 text-lg font-medium">No {status} properties</h3>
                <p className="mt-2 text-rental-600 dark:text-rental-400">
                  {status === 'active' && "You don't have any active property listings yet."}
                  {status === 'pending' && "You don't have any pending property listings."}
                  {status === 'draft' && "You don't have any property drafts. Create a new listing to get started."}
                </p>
                {status !== 'active' && (
                  <Button className="mt-4" asChild>
                    <Link to="/list-property">
                      <Plus className="h-4 w-4 mr-2" />
                      Add New Property
                    </Link>
                  </Button>
                )}
              </div>
            ) : (
              <div className="space-y-4">
                {filteredProperties(status).map((property) => (
                  <Card key={property.id} className="overflow-hidden">
                    <CardContent className="p-0">
                      <div className="flex flex-col sm:flex-row">
                        <div className="sm:w-48 h-48 bg-rental-100 dark:bg-rental-800 rounded-lg overflow-hidden">
                          {property.primary_image ? (
                            <img 
                              src={property.primary_image} 
                              alt={property.title} 
                              className="w-full h-full object-cover"
                            />
                          ) : (
                            <div className="w-full h-full flex items-center justify-center text-rental-400">
                              <Home className="h-12 w-12" />
                            </div>
                          )}
                        </div>
                        <div className="p-4 flex-grow">
                          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
                            <div>
                              <h3 className="text-lg font-semibold">{property.title}</h3>
                              <p className="text-sm text-rental-600 dark:text-rental-400">
                                {property.address}, {property.city}, {property.state}
                              </p>
                            </div>
                            <div className="mt-2 sm:mt-0">
                              <Badge
                                className={
                                  property.status?.name?.toLowerCase() === 'active' || property.status?.name?.toLowerCase() === 'available' ? "bg-green-100 text-green-800 hover:bg-green-100" :
                                  property.status?.name?.toLowerCase() === 'pending' || property.status?.name?.toLowerCase() === 'under_review' ? "bg-yellow-100 text-yellow-800 hover:bg-yellow-100" :
                                  "bg-gray-100 text-gray-800 hover:bg-gray-100"
                                }
                              >
                                {property.status?.name || 'Unknown'}
                              </Badge>
                            </div>
                          </div>
                          
                          <div className="mt-2 flex flex-wrap gap-3">
                            <span className="text-sm text-rental-600 dark:text-rental-400">
                              {property.property_type?.name}
                            </span>
                            <span className="text-sm text-rental-600 dark:text-rental-400">
                              {property.bedrooms} bed • {property.bathrooms} bath
                            </span>
                          </div>
                          
                          <div className="mt-3">
                            <p className="text-lg font-bold">
                              KSh {Number(property.price).toLocaleString()}
                              <span className="text-sm font-normal text-rental-600 dark:text-rental-400">/month</span>
                            </p>
                          </div>
                          
                          {(property.status.name.toLowerCase() === 'active' || property.status.name.toLowerCase() === 'available') && (
                            <div className="mt-3 flex flex-wrap gap-4">
                              <div className="text-sm">
                                <span className="text-rental-600 dark:text-rental-400">Views: </span>
                                <span className="font-medium">{property.views_count || 0}</span>
                              </div>
                            </div>
                          )}
                          
                          <div className="mt-4 flex flex-wrap gap-2">
                            <Button size="sm" variant="outline" asChild>
                              <Link to={`/properties/${property.id}`}>
                                <Eye className="h-4 w-4 mr-1" />
                                View
                              </Link>
                            </Button>
                            <Button size="sm" variant="outline" asChild>
                              <Link to={`/list-property?edit=${property.id}`}>
                                <Edit className="h-4 w-4 mr-1" />
                                Edit
                              </Link>
                            </Button>

                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="text-red-600 hover:text-red-700 hover:bg-red-50"
                              onClick={() => handleDeleteProperty(property.id.toString())}
                            >
                              <Trash className="h-4 w-4 mr-1" />
                              Delete
                            </Button>
                          </div>
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
    </DashboardLayout>
  );
};

export default UserPropertiesPage;
