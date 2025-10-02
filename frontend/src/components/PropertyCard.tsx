
import React from 'react';
import { Link } from 'react-router-dom';
import { Heart, MapPin, BedDouble, Bath, Square } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PropertyCardProps {
  id: string;
  title: string;
  price: number;
  address: string;
  image: string;
  beds: number;
  baths: number;
  sqft: number;
  className?: string;
  featured?: boolean;
}

const PropertyCard: React.FC<PropertyCardProps> = ({
  id,
  title,
  price,
  address,
  image,
  beds,
  baths,
  sqft,
  className,
  featured = false,
}) => {
  return (
    <div 
      className={cn(
        "group overflow-hidden rounded-xl bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 transition-all duration-300 hover:shadow-lg hover:-translate-y-1 subtle-shadow",
        featured ? "col-span-1 md:col-span-2 lg:flex" : "",
        className
      )}
    >
      <Link 
        to={`/properties/${id}`} 
        className={cn(
          "block relative overflow-hidden",
          featured ? "lg:w-1/2" : "aspect-video"
        )}
      >
        <img 
          src={image} 
          alt={title}
          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
        />
        <div className="absolute inset-x-0 bottom-0 h-24 bg-gradient-to-t from-black/60 to-transparent"></div>
        <button className="absolute top-3 right-3 p-2 rounded-full bg-white/20 backdrop-blur-sm hover:bg-white/40 transition-colors">
          <Heart className="w-5 h-5 text-white" />
        </button>
        {featured && (
          <div className="absolute top-3 left-3 px-3 py-1 rounded-full bg-primary text-white text-xs font-medium">
            Featured
          </div>
        )}
      </Link>

      <div className={cn(
        "p-4",
        featured ? "lg:w-1/2 lg:p-6" : ""
      )}>
        <div className="flex justify-between items-start mb-2">
          <div>
            <h3 className="font-medium text-rental-900 dark:text-white text-lg mb-1 line-clamp-1">
              {title}
            </h3>
            <div className="flex items-center text-rental-500 dark:text-rental-400 text-sm">
              <MapPin className="w-3.5 h-3.5 mr-1" />
              <span className="line-clamp-1">{address}</span>
            </div>
          </div>
          <div className="text-primary font-semibold">
            ${price.toLocaleString()}{featured ? '/mo' : ''}
          </div>
        </div>

        <div className="flex items-center justify-between mt-4 pt-4 border-t border-rental-100 dark:border-rental-800">
          <div className="flex items-center text-rental-600 dark:text-rental-300 text-sm">
            <BedDouble className="w-4 h-4 mr-1" />
            <span>{beds} {beds === 1 ? 'Bed' : 'Beds'}</span>
          </div>
          <div className="flex items-center text-rental-600 dark:text-rental-300 text-sm">
            <Bath className="w-4 h-4 mr-1" />
            <span>{baths} {baths === 1 ? 'Bath' : 'Baths'}</span>
          </div>
          <div className="flex items-center text-rental-600 dark:text-rental-300 text-sm">
            <Square className="w-4 h-4 mr-1" />
            <span>{sqft.toLocaleString()} sqft</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PropertyCard;
