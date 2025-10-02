import React, { useState, useEffect } from 'react';
import { MapPin, Filter, Home, Building, ChevronDown, X, Search, Users, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import PropertyCard from '@/components/PropertyCard';
import Layout from '@/components/Layout';
import { propertyService, PropertyListItem, PropertyFilters } from '@/services/propertyService';
import { handleAPIError } from '@/services/errorHandler';

const PropertiesPage = () => {
  const [filterOpen, setFilterOpen] = useState(false);
  const [priceRange, setPriceRange] = useState([0, 10000]);
  const [propertyType, setPropertyType] = useState('all');
  const [userType, setUserType] = useState('all');
  const [location, setLocation] = useState('');
  const [properties, setProperties] = useState<PropertyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);

  // Fetch properties from API
  const fetchProperties = async (filters?: PropertyFilters) => {
    try {
      setLoading(true);
      setError(null);
      const response = await propertyService.getProperties(filters);
      setProperties(response.results);
      setTotalCount(response.count);
      setHasNext(!!response.next);
      setHasPrevious(!!response.previous);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch properties');
      handleAPIError(err, 'Loading properties');
    } finally {
      setLoading(false);
    }
  };

  // Initial load
  useEffect(() => {
    fetchProperties();
  }, []);

  // Apply filters
  const applyFilters = () => {
    const filters: PropertyFilters = {
      ...(propertyType !== 'all' && { property_type: propertyType === 'house' ? 1 : 2 }), // Assuming 1=house, 2=apartment
      ...(priceRange[0] > 0 && { min_price: priceRange[0] }),
      ...(priceRange[1] < 10000 && { max_price: priceRange[1] }),
      ...(location && { search: location }),
      ordering: '-created_at'
    };
    fetchProperties(filters);
    setFilterOpen(false);
  };

  // Reset filters
  const resetFilters = () => {
    setPriceRange([0, 10000]);
    setPropertyType('all');
    setUserType('all');
    setLocation('');
    fetchProperties();
  };

  // Handle pagination
  const handlePrevious = () => {
    if (hasPrevious && currentPage > 1) {
      setCurrentPage(currentPage - 1);
      // In a real implementation, you'd pass page parameter to fetchProperties
    }
  };

  const handleNext = () => {
    if (hasNext) {
      setCurrentPage(currentPage + 1);
      // In a real implementation, you'd pass page parameter to fetchProperties
    }
  };

  // Transform API data to match PropertyCard props
  const transformProperty = (property: PropertyListItem) => ({
    id: property.id.toString(),
    title: property.title,
    price: parseFloat(property.price),
    address: `${property.address}, ${property.city}, ${property.state}`,
    image: property.primary_image || 'https://images.unsplash.com/photo-1545324418-9f1eda94ca43?q=80&w=1000',
    beds: property.bedrooms || 0,
    baths: property.bathrooms || 0,
    sqft: property.square_feet || 0,
    featured: property.is_featured
  });

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        <div className="container px-4 md:px-6">
          <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold mb-2">Properties in Kenya</h1>
              <p className="text-gray-600 dark:text-gray-400">
                {loading ? 'Loading properties...' : `Discover ${totalCount} properties available for rent`}
              </p>
            </div>
            <div className="mt-4 md:mt-0 flex gap-3">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setFilterOpen(!filterOpen)}
                className="flex items-center border-green-600 text-green-600 hover:bg-green-50"
              >
                <Filter className="w-4 h-4 mr-2" />
                Filters
              </Button>
              <div className="relative">
                <Button 
                  variant="outline" 
                  size="sm"
                  className="flex items-center"
                >
                  <span>Sort By</span>
                  <ChevronDown className="w-4 h-4 ml-2" />
                </Button>
              </div>
            </div>
          </div>

          {filterOpen && (
            <div className="bg-white dark:bg-gray-900 p-6 rounded-lg shadow-md mb-8 border border-gray-100 dark:border-gray-800 animate-fade-in">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold">Filter Properties</h2>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setFilterOpen(false)}
                >
                  <X className="w-4 h-4" />
                </Button>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div>
                  <label className="text-sm font-medium mb-2 block">Location</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <Input 
                      placeholder="Search location" 
                      className="pl-10 focus:ring-green-500" 
                      value={location}
                      onChange={(e) => setLocation(e.target.value)}
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">User Type</label>
                  <div className="relative">
                    <Users className="absolute left-3 top-3 h-4 w-4 text-muted-foreground" />
                    <select
                      value={userType}
                      onChange={(e) => setUserType(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-input rounded-md focus:ring-2 focus:ring-green-500"
                    >
                      <option value="all">All Users</option>
                      <option value="tenant">Tenants</option>
                      <option value="buyer">Buyers</option>
                      <option value="landlord">Landlords</option>
                      <option value="agent">Agents</option>
                    </select>
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Price Range (KSh)</label>
                  <div className="flex items-center space-x-2">
                    <Input 
                      type="number" 
                      placeholder="Min" 
                      value={priceRange[0]}
                      onChange={(e) => setPriceRange([parseInt(e.target.value), priceRange[1]])}
                      className="focus:ring-green-500"
                    />
                    <span>-</span>
                    <Input 
                      type="number" 
                      placeholder="Max" 
                      value={priceRange[1]}
                      onChange={(e) => setPriceRange([priceRange[0], parseInt(e.target.value)])}
                      className="focus:ring-green-500"
                    />
                  </div>
                </div>
                <div>
                  <label className="text-sm font-medium mb-2 block">Property Type</label>
                  <div className="flex space-x-2">
                    <Button
                      variant={propertyType === 'all' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setPropertyType('all')}
                      className={propertyType === 'all' ? 'bg-green-600 hover:bg-green-700' : 'border-green-600 text-green-600 hover:bg-green-50'}
                    >
                      All
                    </Button>
                    <Button
                      variant={propertyType === 'house' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setPropertyType('house')}
                      className={propertyType === 'house' ? 'bg-green-600 hover:bg-green-700' : 'border-green-600 text-green-600 hover:bg-green-50'}
                    >
                      <Home className="w-4 h-4 mr-2" />
                      Houses
                    </Button>
                    <Button
                      variant={propertyType === 'apartment' ? 'default' : 'outline'}
                      size="sm"
                      onClick={() => setPropertyType('apartment')}
                      className={propertyType === 'apartment' ? 'bg-green-600 hover:bg-green-700' : 'border-green-600 text-green-600 hover:bg-green-50'}
                    >
                      <Building className="w-4 h-4 mr-2" />
                      Apartments
                    </Button>
                  </div>
                </div>
              </div>
              <div className="flex justify-end mt-6">
                <Button variant="outline" size="sm" className="mr-2" onClick={resetFilters}>
                  Reset
                </Button>
                <Button className="bg-green-600 hover:bg-green-700" onClick={applyFilters}>
                  Apply Filters
                </Button>
              </div>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-8">
              <p className="text-red-600">Error: {error}</p>
              <Button 
                variant="outline" 
                size="sm" 
                className="mt-2"
                onClick={() => fetchProperties()}
              >
                Try Again
              </Button>
            </div>
          )}

          {loading ? (
            <div className="flex justify-center items-center py-12">
              <Loader2 className="h-8 w-8 animate-spin text-green-600" />
              <span className="ml-2 text-gray-600">Loading properties...</span>
            </div>
          ) : !properties || properties.length === 0 ? (
            <div className="text-center py-12">
              <Home className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No properties found</h3>
              <p className="text-gray-600">Try adjusting your filters or search criteria.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {properties.map((property) => (
                <PropertyCard 
                  key={property.id} 
                  {...transformProperty(property)} 
                />
              ))}
            </div>
          )}

          {!loading && properties && properties.length > 0 && (
            <div className="mt-12 flex justify-center items-center space-x-4">
              <Button 
                variant="outline" 
                onClick={handlePrevious}
                disabled={!hasPrevious}
              >
                Previous
              </Button>
              <span className="text-sm text-gray-600">
                Page {currentPage}
              </span>
              <Button 
                className="bg-green-600 hover:bg-green-700"
                onClick={handleNext}
                disabled={!hasNext}
              >
                Next
              </Button>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default PropertiesPage;
