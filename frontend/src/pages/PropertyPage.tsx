
import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapPin, BedDouble, Bath, Square, Calendar, Heart, Share2, DollarSign, ArrowLeft, Phone, Mail, Clock, CheckCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import Layout from '@/components/Layout';
import ImagePreview from '@/components/ImagePreview';
import ApplyNowModal from '@/components/ApplyNowModal';
import ScheduleTourModal from '@/components/ScheduleTourModal';
import { propertyService, Property } from '@/services/propertyService';
import { handleAPIError } from '@/services/errorHandler';

const PropertyPage = () => {
  const { id } = useParams<{ id: string }>();
  const [isLiked, setIsLiked] = useState(false);
  const [imagePreviewIndex, setImagePreviewIndex] = useState<number | null>(null);
  const [isApplyModalOpen, setIsApplyModalOpen] = useState(false);
  const [isTourModalOpen, setIsTourModalOpen] = useState(false);
  const [property, setProperty] = useState<Property | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProperty = async () => {
      if (!id) {
        setError('Property ID is required');
        setIsLoading(false);
        return;
      }

      try {
        setIsLoading(true);
        setError(null);
        const propertyData = await propertyService.getProperty(parseInt(id));
        setProperty(propertyData);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load property');
        handleAPIError(err, 'Loading property details');
      } finally {
        setIsLoading(false);
      }
    };

    fetchProperty();
  }, [id]);

  // Transform API data to match component expectations
  const transformedProperty = property ? {
    id: property.id.toString(),
    title: property.title || '',
    price: parseFloat(property.price) || 0,
    address: `${property.address || ''}, ${property.city || ''}, ${property.state || ''} ${property.zip_code || ''}`.trim(),
    description: property.description || '',
    beds: property.bedrooms || 0,
    baths: property.bathrooms || 0,
    sqft: property.square_feet || 0,
    yearBuilt: property.year_built || new Date().getFullYear(),
    available: 'Available Now', // Default value since API doesn't provide this
    petPolicy: 'Contact agent for pet policy', // Default value
    parkingInfo: 'Contact agent for parking information', // Default value
    amenities: property.features?.map(feature => feature?.name || '') || [],
    images: property.images?.length > 0 
      ? property.images.sort((a, b) => (a?.order || 0) - (b?.order || 0)).map(img => img?.image || '')
      : ['https://images.unsplash.com/photo-1545324418-9f1eda94ca43?q=80&w=1000'], // Fallback image
    agent: {
      name: property.agent 
        ? `${property.agent.first_name} ${property.agent.last_name}`.trim() 
        : `${property.owner.first_name} ${property.owner.last_name}`.trim(),
      phone: '(555) 123-4567', // Default since API doesn't provide this
      email: property.agent?.username || property.owner.username,
      response: '1 hour', // Default value
      image: 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=1000&auto=format&fit=crop' // Default avatar
    }
  } : null;

   const handleImageClick = (index: number) => {
     setImagePreviewIndex(index);
   };

   const handleImagePreviewClose = () => {
     setImagePreviewIndex(null);
   };

   const handleImagePreviewPrevious = () => {
     if (imagePreviewIndex !== null && imagePreviewIndex > 0) {
       setImagePreviewIndex(imagePreviewIndex - 1);
     }
   };

   const handleImagePreviewNext = () => {
     if (imagePreviewIndex !== null && transformedProperty && imagePreviewIndex < transformedProperty.images.length - 1) {
       setImagePreviewIndex(imagePreviewIndex + 1);
     }
   };

   if (isLoading) {
    return (
      <Layout>
        <div className="pt-20 pb-16">
          <div className="container mx-auto px-4 md:px-6 lg:px-10 py-16">
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600"></div>
              <span className="ml-3 text-gray-600 dark:text-gray-400">Loading property...</span>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="pt-20 pb-16">
          <div className="container mx-auto px-4 md:px-6 lg:px-10 py-16">
            <div className="text-center">
              <div className="text-red-600 dark:text-red-400 mb-4">
                <span className="text-lg font-medium">Error loading property</span>
              </div>
              <p className="text-gray-600 dark:text-gray-400 mb-6">{error}</p>
              <Button 
                onClick={() => window.location.reload()}
                className="bg-green-600 hover:bg-green-700 text-white"
              >
                Try Again
              </Button>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  if (!transformedProperty) {
    return (
      <Layout>
        <div className="pt-20 pb-16">
          <div className="container mx-auto px-4 md:px-6 lg:px-10 py-16">
            <div className="text-center">
              <div className="text-gray-600 dark:text-gray-400 mb-4">
                <span className="text-lg font-medium">Property not found</span>
              </div>
              <p className="text-gray-500 dark:text-gray-500 mb-6">The property you're looking for doesn't exist or has been removed.</p>
              <Link to="/properties">
                <Button className="bg-green-600 hover:bg-green-700 text-white">
                  Browse Properties
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="pt-20 pb-16">
        {/* Back Button & Actions */}
        <div className="container mx-auto px-4 md:px-6 lg:px-10 py-6">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <Link 
              to="/properties" 
              className="inline-flex items-center text-gray-700 dark:text-gray-300 hover:text-green-600 dark:hover:text-green-400 transition-colors"
            >
              <ArrowLeft size={18} className="mr-2" />
              Back to listings
            </Link>
            <div className="flex items-center gap-3">
              <Button 
                variant="outline" 
                size="sm"
                onClick={() => setIsLiked(!isLiked)}
                className={isLiked ? "text-red-500 border-red-200 hover:bg-red-50 dark:border-red-800/50 dark:hover:bg-red-900/20" : ""}
              >
                <Heart size={16} className={`mr-2 ${isLiked ? "fill-red-500" : ""}`} />
                {isLiked ? "Saved" : "Save"}
              </Button>
              <Button variant="outline" size="sm">
                <Share2 size={16} className="mr-2" />
                Share
              </Button>
            </div>
          </div>
        </div>

        {/* Property Images */}
        <div className="container mx-auto px-4 md:px-6 lg:px-10 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-2 md:gap-4 aspect-[16/9] md:aspect-[16/7]">
            <div 
              className="col-span-1 md:col-span-2 row-span-2 overflow-hidden rounded-lg cursor-pointer"
              onClick={() => handleImageClick(0)}
            >
              <img 
                src={transformedProperty.images[0]} 
                alt={transformedProperty.title} 
                className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
              />
            </div>
            {transformedProperty.images.slice(1, 5).map((image, index) => (
              <div 
                key={index} 
                className={`overflow-hidden rounded-lg cursor-pointer ${index > 1 ? 'hidden lg:block' : ''}`}
                onClick={() => handleImageClick(index + 1)}
              >
                <img 
                  src={image} 
                  alt={`${transformedProperty.title} - view ${index + 2}`} 
                  className="w-full h-full object-cover hover:scale-105 transition-transform duration-500"
                />
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="container mx-auto px-4 md:px-6 lg:px-10">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Left Column (Property Details) */}
            <div className="lg:col-span-2">
              <div className="mb-8">
                <div className="flex flex-col sm:flex-row justify-between items-start mb-4">
                  <div className="mb-4 sm:mb-0">
                    <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-2">
                      {transformedProperty.title}
                    </h1>
                    <div className="flex items-center text-gray-600 dark:text-gray-400">
                      <MapPin className="w-4 h-4 mr-1 flex-shrink-0" />
                      <span>{transformedProperty.address}</span>
                    </div>
                  </div>
                  <div className="text-2xl font-bold text-green-600">
                    ${transformedProperty.price.toLocaleString()}<span className="text-lg font-normal">/mo</span>
                  </div>
                </div>

                <div className="flex flex-wrap gap-x-6 gap-y-3 mt-6 pb-6 border-b border-gray-100 dark:border-gray-800">
                  <div className="flex items-center text-gray-700 dark:text-gray-300">
                    <BedDouble className="w-5 h-5 mr-2 text-gray-500" />
                    <span>{transformedProperty.beds} {transformedProperty.beds === 1 ? 'Bedroom' : 'Bedrooms'}</span>
                  </div>
                  <div className="flex items-center text-gray-700 dark:text-gray-300">
                    <Bath className="w-5 h-5 mr-2 text-gray-500" />
                    <span>{transformedProperty.baths} {transformedProperty.baths === 1 ? 'Bathroom' : 'Bathrooms'}</span>
                  </div>
                  <div className="flex items-center text-gray-700 dark:text-gray-300">
                    <Square className="w-5 h-5 mr-2 text-gray-500" />
                    <span>{transformedProperty.sqft.toLocaleString()} sq ft</span>
                  </div>
                  <div className="flex items-center text-gray-700 dark:text-gray-300">
                    <Calendar className="w-5 h-5 mr-2 text-gray-500" />
                    <span>Built in {transformedProperty.yearBuilt}</span>
                  </div>
                </div>
              </div>

              <Tabs defaultValue="details" className="mb-8">
                <TabsList className="grid grid-cols-3 mb-6 w-full">
                  <TabsTrigger value="details">Details</TabsTrigger>
                  <TabsTrigger value="amenities">Amenities</TabsTrigger>
                  <TabsTrigger value="location">Location</TabsTrigger>
                </TabsList>
                
                <TabsContent value="details" className="space-y-6">
                  <div>
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-3">
                      About this property
                    </h2>
                    <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-line">
                      {transformedProperty.description}
                    </p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-4 pt-4 border-t border-gray-100 dark:border-gray-800">
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                        Availability
                      </h3>
                      <p className="text-gray-900 dark:text-white">
                        {transformedProperty.available}
                      </p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                        Pet Policy
                      </h3>
                      <p className="text-gray-900 dark:text-white">
                        {transformedProperty.petPolicy}
                      </p>
                    </div>
                    <div>
                      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-1">
                        Parking
                      </h3>
                      <p className="text-gray-900 dark:text-white">
                        {transformedProperty.parkingInfo}
                      </p>
                    </div>
                  </div>
                </TabsContent>
                
                <TabsContent value="amenities">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    Amenities
                  </h2>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-3">
                    {transformedProperty.amenities.map((amenity, index) => (
                      <div key={index} className="flex items-center text-gray-700 dark:text-gray-300">
                        <CheckCircle className="w-5 h-5 mr-2 text-green-600/80" />
                        <span>{amenity}</span>
                      </div>
                    ))}
                  </div>
                </TabsContent>
                
                <TabsContent value="location">
                  <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
                    Location
                  </h2>
                  <div className="rounded-lg overflow-hidden aspect-video bg-gray-100 dark:bg-gray-800">
                    <div className="h-full w-full flex items-center justify-center text-gray-500">
                      Map placeholder - would integrate with Google Maps or similar
                    </div>
                  </div>
                </TabsContent>
              </Tabs>
            </div>

            {/* Right Column (Contact and Apply) */}
            <div className="space-y-6">
              {/* Contact Card */}
              <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-6">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 rounded-full overflow-hidden mr-4">
                    <img 
                      src={transformedProperty.agent.image} 
                      alt={transformedProperty.agent.name} 
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {transformedProperty.agent.name}
                    </h3>
                    <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                      <Clock className="w-3.5 h-3.5 mr-1" />
                      <span>Responds in {transformedProperty.agent.response}</span>
                    </div>
                  </div>
                </div>

                <div className="space-y-3 mb-6">
                  <div className="flex items-center text-gray-700 dark:text-gray-300">
                    <Phone className="w-5 h-5 mr-3 text-gray-500" />
                    <span>{transformedProperty.agent.phone}</span>
                  </div>
                  <div className="flex items-center text-gray-700 dark:text-gray-300">
                    <Mail className="w-5 h-5 mr-3 text-gray-500" />
                    <span>{transformedProperty.agent.email}</span>
                  </div>
                </div>

                <Button className="w-full bg-green-600 hover:bg-green-700 text-white">
                  Contact Agent
                </Button>
              </div>

              {/* Application Card */}
              <div className="bg-white dark:bg-gray-900 rounded-xl shadow-sm border border-gray-100 dark:border-gray-800 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Interested in this property?
                </h3>
                <div className="flex items-center mb-6 p-3 bg-green-50 dark:bg-green-900/20 rounded-lg">
                  <DollarSign className="w-6 h-6 text-green-600 mr-3" />
                  <div>
                    <div className="text-lg font-medium text-gray-900 dark:text-white">
                      ${transformedProperty.price.toLocaleString()}/month
                    </div>
                    <div className="text-sm text-gray-600 dark:text-gray-400">
                      Security deposit: ${(transformedProperty.price * 1.5).toLocaleString()}
                    </div>
                  </div>
                </div>
                <div className="space-y-3">
                  <Button 
                    className="w-full bg-green-600 hover:bg-green-700 text-white"
                    onClick={() => setIsApplyModalOpen(true)}
                  >
                    Apply Now
                  </Button>
                  <Button 
                    variant="outline" 
                    className="w-full"
                    onClick={() => setIsTourModalOpen(true)}
                  >
                    Schedule a Tour
                  </Button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Image Preview Modal */}
      {imagePreviewIndex !== null && (
        <ImagePreview
          images={transformedProperty.images}
          currentIndex={imagePreviewIndex}
          onClose={handleImagePreviewClose}
          onPrevious={handleImagePreviewPrevious}
          onNext={handleImagePreviewNext}
          title={transformedProperty.title}
        />
      )}

      {/* Apply Now Modal */}
      <ApplyNowModal
        isOpen={isApplyModalOpen}
        onClose={() => setIsApplyModalOpen(false)}
        propertyTitle={transformedProperty.title}
        propertyPrice={transformedProperty.price}
      />

      {/* Schedule Tour Modal */}
      <ScheduleTourModal
        isOpen={isTourModalOpen}
        onClose={() => setIsTourModalOpen(false)}
        propertyTitle={transformedProperty.title}
        propertyAddress={transformedProperty.address}
      />
    </Layout>
  );
};

export default PropertyPage;
