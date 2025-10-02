
import React, { useState, useEffect } from 'react';
import { Search, MapPin, Bed, Bath, Square, Heart, Eye, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent } from '@/components/ui/card';
import DashboardLayout from '@/components/DashboardLayout';
import { useToast } from '@/hooks/use-toast';
import { handleAPIError } from '@/services/errorHandler';
import { Link } from 'react-router-dom';
import { propertyService, SavedProperty } from '@/services/propertyService';

const SavedPropertiesPage = () => {
  const { toast } = useToast();
  const [searchQuery, setSearchQuery] = useState('');
  const [savedProperties, setSavedProperties] = useState<SavedProperty[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch saved properties on component mount
  useEffect(() => {
    const fetchSavedProperties = async () => {
      try {
        setIsLoading(true);
        setError(null);
        const savedProps = await propertyService.getSavedProperties();
        setSavedProperties(savedProps);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load saved properties');
        handleAPIError(err, 'Loading saved properties');
      } finally {
        setIsLoading(false);
      }
    };

    fetchSavedProperties();
  }, []);

  const handleRemoveSaved = async (propertyId: number) => {
    try {
      await propertyService.unsaveProperty(propertyId);
      setSavedProperties(savedProperties.filter(savedProp => savedProp.property.id !== propertyId));
      toast({
        title: "Property removed",
        description: "The property has been removed from your saved listings.",
      });
    } catch (err) {
      handleAPIError(err, 'Removing saved property');
    }
  };

  const filteredProperties = savedProperties.filter(savedProp => {
    const title = savedProp.property?.title || '';
    const address = savedProp.property?.address || '';
    const city = savedProp.property?.city || '';
    const state = savedProp.property?.state || '';
    const fullAddress = `${address}, ${city}, ${state}`;
    
    return title.toLowerCase().includes(searchQuery.toLowerCase()) ||
           fullAddress.toLowerCase().includes(searchQuery.toLowerCase());
  });

  return (
    <DashboardLayout title="Saved Properties">
      <div className="mb-6">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search saved properties..."
            className="pl-10 w-full max-w-md"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="h-8 w-8 animate-spin text-rental-600" />
          <span className="ml-2 text-rental-600">Loading saved properties...</span>
        </div>
      ) : error ? (
        <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
          <div className="text-red-500 mb-4">
            <span className="text-lg font-medium">Error loading saved properties</span>
          </div>
          <p className="text-rental-600 dark:text-rental-400 mb-6">{error}</p>
          <Button onClick={() => window.location.reload()}>
            Try Again
          </Button>
        </div>
      ) : !filteredProperties || filteredProperties.length === 0 ? (
        <div className="text-center py-12 bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg">
          <Heart className="h-12 w-12 mx-auto text-rental-400" />
          <h3 className="mt-4 text-lg font-medium">No saved properties</h3>
          <p className="mt-2 text-rental-600 dark:text-rental-400">
            You haven't saved any properties yet. Browse our listings and save properties you're interested in.
          </p>
          <Button className="mt-4" asChild>
            <Link to="/properties">
              Browse Properties
            </Link>
          </Button>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {filteredProperties.map((savedProp) => (
            <Card key={savedProp.id} className="overflow-hidden hover:shadow-md transition-shadow">
              <CardContent className="p-0">
                <div className="flex flex-col">
                  <div className="aspect-video relative">
                    <img 
                      src={savedProp.property.primary_image || 'https://images.unsplash.com/photo-1545324418-9f1eda94ca43?q=80&w=1000'} 
                      alt={savedProp.property.title} 
                      className="w-full h-full object-cover"
                    />
                    <Button 
                      variant="ghost" 
                      size="icon" 
                      className="absolute top-2 right-2 bg-white/80 hover:bg-white text-red-500 rounded-full"
                      onClick={() => handleRemoveSaved(savedProp.property.id)}
                    >
                      <Heart className="h-5 w-5 fill-current" />
                    </Button>
                  </div>
                  <div className="p-4">
                    <h3 className="text-lg font-semibold mb-1">{savedProp.property.title}</h3>
                    <div className="flex items-center text-sm text-rental-600 dark:text-rental-400 mb-2">
                      <MapPin className="h-4 w-4 mr-1 flex-shrink-0" />
                      <span className="truncate">{savedProp.property.address}, {savedProp.property.city}, {savedProp.property.state}</span>
                    </div>
                    <div className="flex flex-wrap gap-3 mb-3">
                      {savedProp.property.bedrooms && (
                        <span className="flex items-center text-sm text-rental-600 dark:text-rental-400">
                          <Bed className="h-4 w-4 mr-1" />
                          {savedProp.property.bedrooms} {savedProp.property.bedrooms === 1 ? 'Bed' : 'Beds'}
                        </span>
                      )}
                      {savedProp.property.bathrooms && (
                        <span className="flex items-center text-sm text-rental-600 dark:text-rental-400">
                          <Bath className="h-4 w-4 mr-1" />
                          {savedProp.property.bathrooms} {savedProp.property.bathrooms === 1 ? 'Bath' : 'Baths'}
                        </span>
                      )}
                      {savedProp.property.square_feet && (
                        <span className="flex items-center text-sm text-rental-600 dark:text-rental-400">
                          <Square className="h-4 w-4 mr-1" />
                          {savedProp.property.square_feet} ft²
                        </span>
                      )}
                    </div>
                    <p className="text-lg font-bold mb-3">
                      KSh {parseFloat(savedProp.property.price).toLocaleString()}
                      <span className="text-sm font-normal text-rental-500">/month</span>
                    </p>
                    <div className="flex items-center justify-between">
                      <div className="text-xs text-rental-500">
                        Saved on {new Date(savedProp.created_at).toLocaleDateString('en-US', {
                          year: 'numeric',
                          month: 'short',
                          day: 'numeric'
                        })}
                      </div>
                      <Button size="sm" asChild>
                        <Link to={`/properties/${savedProp.property.id}`}>
                          <Eye className="h-4 w-4 mr-1" />
                          View Property
                        </Link>
                      </Button>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
};

export default SavedPropertiesPage;
