
import React, { useState, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Menu, X, Search } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { AuthButton } from '@/components/AuthButton';
import { ConnectionStatus } from '@/components/ConnectionStatus';
import { cn } from '@/lib/utils';

const Navbar = () => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const location = useLocation();
  const navigate = useNavigate();

  // Detect scroll position to change navbar style
  useEffect(() => {
    const handleScroll = () => {
      if (window.scrollY > 20) {
        setIsScrolled(true);
      } else {
        setIsScrolled(false);
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
    setIsSearchOpen(false);
  }, [location]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?query=${encodeURIComponent(searchQuery)}`);
      setIsSearchOpen(false);
    }
  };

  const navItems = [
    { name: 'Home', path: '/' },
    { name: 'Properties', path: '/properties' },
    { name: 'Services', path: '/services' },
    { name: 'Newsletter', path: '/newsletter' },
    { name: 'About Us', path: '/about' },
    { name: 'Contact', path: '/contact' },
  ];

  return (
    <header 
      className={cn(
        "fixed top-0 left-0 right-0 z-50 transition-all duration-300 py-4 px-4 md:px-6 lg:px-10",
        isScrolled ? "bg-white/95 dark:bg-gray-950/95 shadow-sm backdrop-blur-md" : "bg-transparent"
      )}
    >
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        {/* Logo */}
        <Link to="/" className="flex items-center">
          <h1 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white">
            Jas<span className="text-green-500">ton</span>
          </h1>
        </Link>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center space-x-6 lg:space-x-8">
          {navItems.map((item) => (
            <Link
              key={item.name}
              to={item.path}
              className={cn(
                "text-sm font-medium transition-colors duration-200 relative group",
                location.pathname === item.path
                  ? "text-green-600"
                  : "text-gray-800 dark:text-gray-100 hover:text-green-600 dark:hover:text-green-400"
              )}
            >
              {item.name}
              <span className={cn(
                "absolute bottom-0 left-0 w-full h-0.5 bg-green-500 transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300",
                location.pathname === item.path ? "scale-x-100" : ""
              )} />
            </Link>
          ))}
        </nav>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center space-x-3 lg:space-x-4">
          <ConnectionStatus showText={false} className="mr-2" />
          
          <Button 
            variant="ghost" 
            size="sm" 
            className="text-gray-800 dark:text-gray-100 hover:text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20"
            onClick={() => setIsSearchOpen(!isSearchOpen)}
          >
            <Search className="h-4 w-4 mr-2" />
            Search
          </Button>
          
          <AuthButton />
          
          <Button asChild size="sm" className="bg-green-600 hover:bg-green-700 text-white">
            <Link to="/list-property">
              List Property
            </Link>
          </Button>
        </div>

        {/* Mobile Menu Button */}
        <div className="md:hidden flex items-center space-x-2">
          <ConnectionStatus showText={false} className="mr-2" />
          
          <button
            className="text-gray-800 dark:text-white hover:text-green-600"
            onClick={() => setIsSearchOpen(!isSearchOpen)}
          >
            <Search size={20} />
          </button>
          
          <button
            className="text-gray-800 dark:text-white hover:text-green-600"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>

        {/* Search Overlay */}
        {isSearchOpen && (
          <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-20 px-4">
            <div className="bg-white dark:bg-gray-900 w-full max-w-2xl rounded-lg shadow-lg p-6 animate-fade-in">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Search Properties</h2>
                <button onClick={() => setIsSearchOpen(false)} className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200">
                  <X className="h-5 w-5" />
                </button>
              </div>
              <form onSubmit={handleSearch}>
                <div className="relative">
                  <input 
                    type="text"
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search for locations, properties, or keywords..."
                    className="w-full border border-gray-200 dark:border-gray-700 rounded-lg py-3 pl-10 pr-4 text-gray-900 dark:text-white dark:bg-gray-800 focus:outline-none focus:ring-2 focus:ring-green-500"
                  />
                  <Search className="absolute left-3 top-3.5 h-5 w-5 text-gray-400" />
                </div>
                <div className="mt-4 flex justify-end">
                  <Button 
                    type="button" 
                    variant="outline" 
                    className="mr-2"
                    onClick={() => setIsSearchOpen(false)}
                  >
                    Cancel
                  </Button>
                  <Button type="submit" className="bg-green-600 hover:bg-green-700">
                    Search
                  </Button>
                </div>
              </form>
              <div className="mt-4">
                <h3 className="text-sm font-medium mb-2 text-gray-900 dark:text-white">Popular Searches:</h3>
                <div className="flex flex-wrap gap-2">
                  {['Nairobi', 'Mombasa', 'Kilimani', 'Apartments', '2 Bedroom'].map(tag => (
                    <button 
                      key={tag}
                      className="px-3 py-1 bg-gray-100 dark:bg-gray-800 rounded-full text-sm hover:bg-green-100 dark:hover:bg-green-900/20 transition-colors text-gray-900 dark:text-white"
                      onClick={() => {
                        setSearchQuery(tag);
                      }}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Mobile Menu */}
        {isMobileMenuOpen && (
          <div className="md:hidden absolute top-full left-0 right-0 bg-white dark:bg-gray-950 shadow-lg animate-fade-in">
            <div className="flex flex-col p-6 space-y-4">
              {navItems.map((item) => (
                <Link
                  key={item.name}
                  to={item.path}
                  className={cn(
                    "text-base py-2 border-b border-gray-100 dark:border-gray-800",
                    location.pathname === item.path
                      ? "text-green-600 font-medium"
                      : "text-gray-800 dark:text-gray-100"
                  )}
                >
                  {item.name}
                </Link>
              ))}
              
              <Link to="/auth" className="flex items-center text-base py-2 border-b border-gray-100 dark:border-gray-800 text-gray-800 dark:text-gray-100">
                Account
              </Link>
              
              <Button asChild size="sm" className="bg-green-600 hover:bg-green-700 text-white mt-2">
                <Link to="/list-property">
                  List Property
                </Link>
              </Button>
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
