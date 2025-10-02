
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, MapPin, Home, DollarSign, X, Users } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { cn } from '@/lib/utils';

interface SearchBarProps {
  className?: string;
  variant?: 'default' | 'expanded';
}

const SearchBar: React.FC<SearchBarProps> = ({ 
  className,
  variant = 'default'
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [priceRange, setPriceRange] = useState('');
  const [propertyType, setPropertyType] = useState('');
  const [userType, setUserType] = useState('');
  const [isExpanded, setIsExpanded] = useState(variant === 'expanded');
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/search?query=${searchQuery}&price=${priceRange}&type=${propertyType}&userType=${userType}`);
  };

  const clearSearch = () => {
    setSearchQuery('');
    setPriceRange('');
    setPropertyType('');
    setUserType('');
  };

  return (
    <form 
      onSubmit={handleSubmit}
      className={cn(
        "relative w-full max-w-4xl transition-all duration-300",
        variant === 'expanded' ? "glass-effect rounded-xl p-6" : "",
        className
      )}
    >
      <div className={cn(
        "flex flex-col md:flex-row items-stretch gap-3",
        variant === 'expanded' ? "md:items-end" : "md:items-center"
      )}>
        {/* Location input */}
        <div className={cn(
          "flex-grow relative",
          variant === 'expanded' ? "flex flex-col gap-1" : ""
        )}>
          {variant === 'expanded' && (
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Location
            </label>
          )}
          <div className="relative flex items-center">
            <div className="absolute left-3 text-gray-400">
              <MapPin size={18} />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="City, neighborhood, or address"
              className={cn(
                "w-full rounded-lg border border-gray-200 dark:border-gray-700 py-2.5 pl-10 pr-4 text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-green-500/50 bg-white dark:bg-gray-900",
                searchQuery && "pr-8"
              )}
            />
            {searchQuery && (
              <button
                type="button"
                onClick={() => setSearchQuery('')}
                className="absolute right-3 text-gray-400 hover:text-gray-600"
              >
                <X size={16} />
              </button>
            )}
          </div>
        </div>

        {(isExpanded || variant === 'expanded') && (
          <>
            {/* User Type input */}
            <div className={cn(
              "md:w-48",
              variant === 'expanded' ? "flex flex-col gap-1" : ""
            )}>
              {variant === 'expanded' && (
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  I'm a
                </label>
              )}
              <div className="relative flex items-center">
                <div className="absolute left-3 text-gray-400">
                  <Users size={18} />
                </div>
                <select
                  value={userType}
                  onChange={(e) => setUserType(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 dark:border-gray-700 py-2.5 pl-10 pr-4 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500/50 bg-white dark:bg-gray-900 appearance-none"
                >
                  <option value="">User Type</option>
                  <option value="tenant">Tenant</option>
                  <option value="buyer">Buyer</option>
                  <option value="landlord">Landlord</option>
                  <option value="agent">Agent</option>
                </select>
              </div>
            </div>

            {/* Price Range input */}
            <div className={cn(
              "md:w-48",
              variant === 'expanded' ? "flex flex-col gap-1" : ""
            )}>
              {variant === 'expanded' && (
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Price Range
                </label>
              )}
              <div className="relative flex items-center">
                <div className="absolute left-3 text-gray-400">
                  <DollarSign size={18} />
                </div>
                <select
                  value={priceRange}
                  onChange={(e) => setPriceRange(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 dark:border-gray-700 py-2.5 pl-10 pr-4 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500/50 bg-white dark:bg-gray-900 appearance-none"
                >
                  <option value="">Price Range</option>
                  <option value="0-50000">KSh 0 - 50,000</option>
                  <option value="50000-100000">KSh 50,000 - 100,000</option>
                  <option value="100000-200000">KSh 100,000 - 200,000</option>
                  <option value="200000-500000">KSh 200,000 - 500,000</option>
                  <option value="500000+">KSh 500,000+</option>
                </select>
              </div>
            </div>

            {/* Property Type input */}
            <div className={cn(
              "md:w-48",
              variant === 'expanded' ? "flex flex-col gap-1" : ""
            )}>
              {variant === 'expanded' && (
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Property Type
                </label>
              )}
              <div className="relative flex items-center">
                <div className="absolute left-3 text-gray-400">
                  <Home size={18} />
                </div>
                <select
                  value={propertyType}
                  onChange={(e) => setPropertyType(e.target.value)}
                  className="w-full rounded-lg border border-gray-200 dark:border-gray-700 py-2.5 pl-10 pr-4 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-green-500/50 bg-white dark:bg-gray-900 appearance-none"
                >
                  <option value="">Property Type</option>
                  <option value="apartment">Apartment</option>
                  <option value="house">House</option>
                  <option value="condo">Condo</option>
                  <option value="townhouse">Townhouse</option>
                  <option value="studio">Studio</option>
                </select>
              </div>
            </div>
          </>
        )}

        {/* Toggle and Search buttons */}
        <div className="flex gap-2">
          {variant !== 'expanded' && (
            <Button
              type="button"
              variant="outline"
              size="icon"
              onClick={() => setIsExpanded(!isExpanded)}
              className="h-10 w-10 flex-shrink-0 border-gray-200 dark:border-gray-700"
            >
              <Search size={18} />
            </Button>
          )}
          
          <Button 
            type="submit" 
            className="h-10 bg-green-600 hover:bg-green-700 text-white flex-shrink-0 px-6"
          >
            Search
          </Button>
        </div>
      </div>
    </form>
  );
};

export default SearchBar;
