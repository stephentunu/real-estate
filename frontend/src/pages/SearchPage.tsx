
import React, { useEffect, useState, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import Layout from '@/components/Layout';
import SearchBar from '@/components/SearchBar';
import PropertyCard from '@/components/PropertyCard';
import { Button } from '@/components/ui/button';
import { Filter, ChevronDown } from 'lucide-react';
import { propertyService, PropertyListItem, PropertyFilters } from '@/services/propertyService';

const SearchPage = () => {
  const location = useLocation();
  const [searchResults, setSearchResults] = useState<PropertyListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterOpen, setFilterOpen] = useState(false);
  const [totalCount, setTotalCount] = useState(0);

  const fetchSearchResults = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const searchParams = new URLSearchParams(location.search);
      const query = searchParams.get('query') || '';
      const priceRange = searchParams.get('price') || '';
      const propertyType = searchParams.get('type') || '';
      
      // Build search filters
      const filters: PropertyFilters = {
        page: 1,
        limit: 20
      };
      
      if (query) {
        filters.search = query;
      }
      
      if (propertyType) {
        filters.property_type = propertyType;
      }
      
      if (priceRange) {
        const [minPrice, maxPrice] = priceRange.split('-').map(Number);
        if (minPrice) filters.min_price = minPrice;
        if (maxPrice) filters.max_price = maxPrice;
      }
      
      // Fetch properties from API
      const response = await propertyService.getProperties(filters);
      
      // Transform API data to match PropertyCard props
      const transformedProperties = response.results.map(property => ({
          id: property.id.toString(),
          title: property.title,
          price: parseFloat(property.price) || 0,
          address: `${property.address}, ${property.city}, ${property.state}`,
          beds: property.bedrooms || 0,
          baths: property.bathrooms || 0,
          sqft: property.square_feet || 0,
          image: property.primary_image || '/images/placeholder-property.jpg'
        }));
        
        setSearchResults(transformedProperties);
      setTotalCount(response.count || 0);
    } catch (err) {
      console.error('Error fetching search results:', err);
      setError('Failed to load search results');
      setSearchResults([]);
      setTotalCount(0);
    } finally {
      setLoading(false);
    }
  }, [location.search]);

  useEffect(() => {
    fetchSearchResults();
  }, [fetchSearchResults]);

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        <div className="container px-4 md:px-6">
          <div className="mb-8">
            <h1 className="text-3xl font-bold mb-6">Search Properties</h1>
            <SearchBar variant="expanded" className="mb-8" />
            
            <div className="flex justify-between items-center mb-6">
              <p className="text-rental-600 dark:text-rental-400">
                {searchResults.length} properties found
              </p>
              <div className="flex gap-3">
                <Button 
                  variant="outline" 
                  size="sm"
                  onClick={() => setFilterOpen(!filterOpen)}
                  className="flex items-center"
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
          </div>

          {loading ? (
            <div className="text-center py-12">
              <p className="text-rental-600 dark:text-rental-400">Loading properties...</p>
            </div>
          ) : (
            <>
              {!searchResults || searchResults.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-rental-600 dark:text-rental-400 mb-4">
                    No properties found matching your search criteria.
                  </p>
                  <Button onClick={() => window.history.back()}>
                    Go Back
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {(searchResults || []).map((property) => (
                    <PropertyCard 
                      key={property.id} 
                      {...property} 
                    />
                  ))}
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default SearchPage;
