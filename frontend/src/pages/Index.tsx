
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, MapPin, TrendingUp, Shield, Zap, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Layout from '@/components/Layout';
import SearchBar from '@/components/SearchBar';
import PropertyCard from '@/components/PropertyCard';
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  CarouselNext,
  CarouselPrevious,
} from "@/components/ui/carousel";
import { propertyService, PropertyListItem } from '@/services/propertyService';
import { cityService, CityListItem } from '@/services/cityService';

interface PropertyCardData {
  id: string;
  title: string;
  price: number;
  address: string;
  image: string;
  beds: number;
  baths: number;
  sqft: number;
  featured: boolean;
}

const Index = () => {
  const [isLoaded, setIsLoaded] = useState(false);
  const [featuredProperties, setFeaturedProperties] = useState<PropertyCardData[]>([]);
  const [cities, setCities] = useState<CityListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setIsLoaded(true);
    fetchFeaturedProperties();
    fetchCities();
  }, []);

  const fetchFeaturedProperties = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await propertyService.getFeaturedProperties(6);
      
      // Transform API data to match PropertyCard props
      const transformedProperties = response?.map((property: PropertyListItem) => ({
        id: property.id.toString(),
        title: property.title,
        price: parseFloat(property.price) || 0,
        address: `${property.address}, ${property.city}, ${property.state}`,
        image: property.primary_image || 'https://images.unsplash.com/photo-1545324418-9f1eda94ca43?q=80&w=1000',
        beds: property.bedrooms || 0,
        baths: property.bathrooms || 0,
        sqft: property.square_feet || 0,
        featured: property.is_featured
      })) || [];
      
      setFeaturedProperties(transformedProperties);
    } catch (err) {
      console.error('Error fetching featured properties:', err);
      setError('Failed to load featured properties');
      setFeaturedProperties([]);
    } finally {
      setLoading(false);
    }
  };

  const fetchCities = async () => {
    try {
      // Fetch top 4 cities by property count
      const response = await cityService.getCities({
        ordering: '-property_count',
        limit: 4
      });
      
      // Access the results array from the response
      setCities(response?.results || []);
    } catch (err) {
      console.error('Error fetching cities:', err);
      // Fallback to empty array on error
      setCities([]);
    }
  };

  // Default images for cities (fallback)
  const cityImages: { [key: string]: string } = {
    'Nairobi': 'https://images.unsplash.com/photo-1611348586840-ea9872d33411?q=80&w=1000',
    'Mombasa': 'https://images.unsplash.com/photo-1596005554384-d293674c91d7?q=80&w=1000',
    'Kisumu': 'https://images.unsplash.com/photo-1626868703110-eeab0323be65?q=80&w=1000',
    'Nakuru': 'https://images.unsplash.com/photo-1630857453903-0386bfb0d990?q=80&w=1000'
  };

  return (
    <Layout>
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <div className="absolute inset-0 bg-gradient-to-r from-black/60 to-black/40 z-10" />
          <img 
            src="https://images.unsplash.com/photo-1512917774080-9991f1c4c750?q=80&w=1000" 
            alt="Modern house exterior" 
            className="w-full h-full object-cover object-center"
          />
        </div>
        
        <div className="container mx-auto px-6 md:px-10 relative z-20 pt-32 pb-20">
          <div className="max-w-3xl">
            <div className={`transition-all duration-700 transform ${isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-6 leading-tight">
                Find Your Perfect <span className="text-green-400">Home</span> in Kenya
              </h1>
              <p className="text-lg md:text-xl text-white/90 mb-8 max-w-2xl">
                Discover premium properties across Kenya's most sought-after locations. Your perfect home is just a click away.
              </p>
            </div>
            
            <div className={`transition-all duration-700 delay-300 transform ${isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
              <SearchBar variant="expanded" className="mb-8" />
            </div>
            
            <div className={`transition-all duration-700 delay-500 transform ${isLoaded ? 'translate-y-0 opacity-100' : 'translate-y-10 opacity-0'}`}>
              <div className="flex flex-wrap gap-4 items-center mt-6">
                <span className="text-white/90">Popular:</span>
                {(cities.length > 0 ? cities.slice(0, 5) : [
                  { id: 1, name: 'Nairobi' },
                  { id: 2, name: 'Mombasa' },
                  { id: 3, name: 'Kisumu' },
                  { id: 4, name: 'Nakuru' },
                  { id: 5, name: 'Eldoret' }
                ]).map((city) => (
                  <Link 
                    key={city.id || city.name} 
                    to={`/search?query=${city.name}`}
                    className="px-3 py-1.5 bg-white/10 hover:bg-green-500/20 backdrop-blur-sm rounded-full text-white text-sm transition-colors"
                  >
                    {city.name}
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Featured Properties with Carousel */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900 graph-background dark:graph-background-dark">
        <div className="container mx-auto px-6 md:px-10">
          <div className="flex justify-between items-end mb-10">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
                Featured Properties
              </h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-2xl">
                Exclusive selections from our latest listings across Kenya, handpicked for their exceptional value and appeal.
              </p>
            </div>
            <Link 
              to="/properties" 
              className="hidden md:flex items-center text-green-600 hover:text-green-700 font-medium"
            >
              View All
              <ArrowRight size={18} className="ml-1" />
            </Link>
          </div>

          {loading ? (
            <div className="flex justify-center items-center py-20">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                <p className="text-gray-600 dark:text-gray-400">Loading featured properties...</p>
              </div>
            </div>
          ) : error ? (
            <div className="text-center py-20">
              <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
              <Button 
                onClick={fetchFeaturedProperties}
                variant="outline" 
                className="border-green-600 text-green-600 hover:bg-green-50"
              >
                Try Again
              </Button>
            </div>
          ) : !featuredProperties || featuredProperties.length === 0 ? (
            <div className="text-center py-20">
              <p className="text-gray-600 dark:text-gray-400 mb-4">No featured properties available at the moment.</p>
              <Button asChild variant="outline" className="border-green-600 text-green-600 hover:bg-green-50">
                <Link to="/properties">Browse All Properties</Link>
              </Button>
            </div>
          ) : (
            <Carousel className="w-full">
              <CarouselContent>
                {featuredProperties.map((property) => (
                  <CarouselItem key={property.id} className="md:basis-1/2 lg:basis-1/3">
                    <PropertyCard {...property} />
                  </CarouselItem>
                ))}
              </CarouselContent>
              <CarouselPrevious />
              <CarouselNext />
            </Carousel>
          )}
          
          <div className="mt-8 text-center md:hidden">
            <Button asChild variant="outline" className="border-green-600 text-green-600 hover:bg-green-50">
              <Link to="/properties">
                View All Properties
                <ArrowRight size={16} className="ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white dark:bg-gray-800 graph-dots">
        <div className="container mx-auto px-6 md:px-10">
          <div className="text-center mb-16 max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
              How Jaston Works
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              We make finding and securing your ideal property in Kenya simple, transparent, and hassle-free.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
            {[
              { 
                icon: <Search className="w-10 h-10 text-green-600" />, 
                title: 'Browse Properties', 
                description: 'Explore our extensive collection of verified listings with detailed information and high-quality photos.' 
              },
              { 
                icon: <TrendingUp className="w-10 h-10 text-green-600" />, 
                title: 'Schedule Viewings', 
                description: 'Book property tours at your convenience through our platform with just a few clicks.' 
              },
              { 
                icon: <Shield className="w-10 h-10 text-green-600" />, 
                title: 'Secure Your Home', 
                description: 'Complete the rental or purchase process with our guidance and secure payment processing.' 
              }
            ].map((step, index) => (
              <div key={index} className="text-center p-6 bg-gray-50 dark:bg-gray-700/30 rounded-xl hover:shadow-md transition-shadow group">
                <div className="w-20 h-20 mx-auto mb-6 flex items-center justify-center bg-white dark:bg-gray-800 rounded-full shadow-sm group-hover:shadow transition-shadow">
                  {step.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                  {step.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  {step.description}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-16 text-center">
            <Button asChild variant="default" size="lg" className="bg-green-600 hover:bg-green-700 text-white">
              <Link to="/services">
                Learn More
                <ArrowRight size={16} className="ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Popular Cities with Carousel */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900 graph-diagonal">
        <div className="container mx-auto px-6 md:px-10">
          <div className="flex justify-between items-end mb-10">
            <div>
              <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-3">
                Explore Kenyan Cities
              </h2>
              <p className="text-gray-600 dark:text-gray-400 max-w-2xl">
                Discover rental properties in these sought-after areas across Kenya.
              </p>
            </div>
            <Link 
              to="/cities" 
              className="hidden md:flex items-center text-green-600 hover:text-green-700 font-medium"
            >
              View All Cities
              <ArrowRight size={18} className="ml-1" />
            </Link>
          </div>

          <Carousel className="w-full">
            <CarouselContent>
              {Array.isArray(cities) && cities.map((city) => (
                <CarouselItem key={city.id} className="md:basis-1/2 lg:basis-1/4">
                  <Link 
                    to={`/search?query=${city.name}`}
                    className="group relative rounded-xl overflow-hidden aspect-square block"
                  >
                    <div className="absolute inset-0 bg-gradient-to-t from-black/70 via-black/30 to-transparent z-10" />
                    <img 
                      src={city.images?.[0] || cityImages[city.name] || 'https://images.unsplash.com/photo-1545324418-9f1eda94ca43?q=80&w=1000'} 
                      alt={city.name} 
                      className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                    />
                    <div className="absolute bottom-0 left-0 right-0 p-6 z-20">
                      <h3 className="text-xl font-semibold text-white mb-1">
                        {city.name}
                      </h3>
                      <div className="flex items-center text-white/90 text-sm">
                        <MapPin className="w-4 h-4 mr-1" />
                        <span>{city.population ? `${city.population.toLocaleString()} people` : 'Featured city'}</span>
                      </div>
                    </div>
                  </Link>
                </CarouselItem>
              ))}
            </CarouselContent>
            <CarouselPrevious />
            <CarouselNext />
          </Carousel>
          
          <div className="mt-8 text-center md:hidden">
            <Button asChild variant="outline" className="border-green-600 text-green-600 hover:bg-green-50">
              <Link to="/cities">
                View All Cities
                <ArrowRight size={16} className="ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-green-600">
        <div className="container mx-auto px-6 md:px-10">
          <div className="max-w-4xl mx-auto text-center">
            <Zap className="w-12 h-12 text-white/90 mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Find Your Perfect Home in Kenya?
            </h2>
            <p className="text-white/90 text-lg mb-8 max-w-2xl mx-auto">
              Join thousands of satisfied tenants who found their ideal properties through Jaston. Start your search today.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Button asChild size="lg" variant="default" className="bg-white text-green-600 hover:bg-gray-100">
                <Link to="/properties">
                  Browse Properties
                </Link>
              </Button>
              <Button asChild size="lg" variant="outline" className="text-white border-white/30 hover:bg-white/10">
                <Link to="/auth">
                  Get Started
                </Link>
              </Button>
            </div>
          </div>
        </div>
      </section>
    </Layout>
  );
};

export default Index;
