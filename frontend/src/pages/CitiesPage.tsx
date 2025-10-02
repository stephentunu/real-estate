
import React, { useState, useEffect } from 'react';
import { MapPin, Loader2 } from 'lucide-react';
import { Link } from 'react-router-dom';
import Layout from '@/components/Layout';
import { cityService, CityListItem } from '@/services/cityService';
import { handleAPIError } from '@/services/errorHandler';

const CitiesPage = () => {
  const [cities, setCities] = useState<CityListItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Default images for cities (fallback)
  const cityImages: { [key: string]: string } = {
    'Nairobi': 'https://images.unsplash.com/photo-1611348586840-ea9872d33411?q=80&w=1000',
    'Mombasa': 'https://images.unsplash.com/photo-1596005554384-d293674c91d7?q=80&w=1000',
    'Kisumu': 'https://images.unsplash.com/photo-1626868703110-eeab0323be65?q=80&w=1000',
    'Nakuru': 'https://images.unsplash.com/photo-1630857453903-0386bfb0d990?q=80&w=1000',
    'Eldoret': 'https://images.unsplash.com/photo-1580629905970-f6f5f7318ba2?q=80&w=1000',
    'Thika': 'https://images.unsplash.com/photo-1518780664697-55e3ad937233?q=80&w=1000',
    'Malindi': 'https://images.unsplash.com/photo-1518548419970-58e3b4079ab2?q=80&w=1000',
    'Kitale': 'https://images.unsplash.com/photo-1559841644-08984562005a?q=80&w=1000'
  };

  useEffect(() => {
    const fetchCities = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        // Fetch cities with property counts
        const response = await cityService.getCities({
          ordering: '-property_count',
          limit: 20
        });
        
        setCities(response.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch cities');
        handleAPIError(err, 'Loading cities');
      } finally {
        setIsLoading(false);
      }
    };

    fetchCities();
  }, []);

  const handleRetry = () => {
    const fetchCities = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const response = await cityService.getCities({
          ordering: '-property_count',
          limit: 20
        });
        
        setCities(response.results);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch cities');
        console.error('Error fetching cities:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchCities();
  };

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen graph-background dark:graph-background-dark">
        <div className="container px-4 md:px-6">
          <h1 className="text-3xl font-bold mb-2">Explore Cities</h1>
          <p className="text-rental-600 dark:text-rental-400 mb-10">
            Discover properties across Kenya's major cities
          </p>

          {isLoading && (
            <div className="flex items-center justify-center py-20">
              <Loader2 className="w-8 h-8 animate-spin text-green-600" />
              <span className="ml-2 text-lg">Loading cities...</span>
            </div>
          )}

          {error && (
            <div className="text-center py-20">
              <div className="text-red-600 mb-4">
                <h3 className="text-lg font-semibold mb-2">Failed to load cities</h3>
                <p className="text-sm">{error}</p>
              </div>
              <button
                onClick={handleRetry}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
              >
                Try Again
              </button>
            </div>
          )}

          {!isLoading && !error && cities.length === 0 && (
            <div className="text-center py-20">
              <h3 className="text-lg font-semibold mb-2">No cities found</h3>
              <p className="text-rental-600 dark:text-rental-400">Please try again later.</p>
            </div>
          )}

          {!isLoading && !error && cities.length > 0 && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              {cities.map((city) => (
                <Link 
                  key={city.id} 
                  to={`/search?query=${city.name}`}
                  className="group relative rounded-xl overflow-hidden aspect-square"
                >
                  <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent z-10" />
                  <img 
                    src={city.image || cityImages[city.name] || 'https://images.unsplash.com/photo-1449824913935-59a10b8d2000?q=80&w=1000'} 
                    alt={city.name} 
                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                  />
                  <div className="absolute bottom-0 left-0 right-0 p-6 z-20">
                    <h3 className="text-xl font-semibold text-white mb-1">
                      {city.name}
                    </h3>
                    <div className="flex items-center text-white/90 text-sm">
                      <MapPin className="w-4 h-4 mr-1" />
                      <span>{city.property_count} properties</span>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default CitiesPage;
