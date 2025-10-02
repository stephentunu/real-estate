
import React from 'react';
import { Link } from 'react-router-dom';
import { Facebook, Twitter, Instagram, Linkedin, ChevronRight } from 'lucide-react';
import { Button } from '@/components/ui/button';

const Footer = () => {
  return (
    <footer className="bg-white dark:bg-rental-950 border-t border-rental-100 dark:border-rental-800">
      <div className="max-w-7xl mx-auto py-12 px-6 md:px-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Company info */}
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-rental-900 dark:text-white">
              Jas<span className="text-primary">ton</span>
            </h2>
            <p className="text-sm text-rental-600 dark:text-rental-300 max-w-xs">
              Kenya's premier property management and real estate solutions provider, helping Kenyans find their perfect home.
            </p>
            <div className="flex space-x-4">
              <a href="https://facebook.com/jaston" className="text-rental-400 hover:text-primary transition-colors">
                <Facebook size={20} />
              </a>
              <a href="https://twitter.com/jaston" className="text-rental-400 hover:text-primary transition-colors">
                <Twitter size={20} />
              </a>
              <a href="https://instagram.com/jaston" className="text-rental-400 hover:text-primary transition-colors">
                <Instagram size={20} />
              </a>
              <a href="https://linkedin.com/company/jaston" className="text-rental-400 hover:text-primary transition-colors">
                <Linkedin size={20} />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="text-sm font-semibold text-rental-900 dark:text-white uppercase tracking-wider mb-4">
              Explore
            </h3>
            <ul className="space-y-2">
              {[
                { name: 'Properties', path: '/properties' },
                { name: 'Services', path: '/services' },
                { name: 'About Us', path: '/about' },
                { name: 'Contact', path: '/contact' },
                { name: 'Cities', path: '/cities' },
                { name: 'Blog', path: '/blog' }
              ].map((item) => (
                <li key={item.name}>
                  <Link 
                    to={item.path}
                    className="text-sm text-rental-600 dark:text-rental-300 hover:text-primary dark:hover:text-primary transition-colors flex items-center group"
                  >
                    <ChevronRight size={14} className="opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all duration-200" />
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* About */}
          <div>
            <h3 className="text-sm font-semibold text-rental-900 dark:text-white uppercase tracking-wider mb-4">
              Company
            </h3>
            <ul className="space-y-2">
              {[
                { name: 'About Us', path: '/about' },
                { name: 'Our Team', path: '/team' },
                { name: 'Careers', path: '/careers' },
                { name: 'Contact Us', path: '/contact' },
                { name: 'Help Center', path: '/help' },
                { name: 'Privacy Policy', path: '/privacy' }
              ].map((item) => (
                <li key={item.name}>
                  <Link 
                    to={item.path}
                    className="text-sm text-rental-600 dark:text-rental-300 hover:text-primary dark:hover:text-primary transition-colors flex items-center group"
                  >
                    <ChevronRight size={14} className="opacity-0 -ml-4 group-hover:opacity-100 group-hover:ml-0 transition-all duration-200" />
                    {item.name}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Newsletter */}
          <div>
            <h3 className="text-sm font-semibold text-rental-900 dark:text-white uppercase tracking-wider mb-4">
              Stay Updated
            </h3>
            <p className="text-sm text-rental-600 dark:text-rental-300 mb-4">
              Subscribe to our newsletter for the latest property listings and real estate news in Kenya.
            </p>
            <div className="flex flex-col sm:flex-row space-y-2 sm:space-y-0 sm:space-x-2">
              <input
                type="email"
                placeholder="Your email"
                className="px-3 py-2 text-sm rounded-md border border-rental-200 dark:border-rental-700 bg-white dark:bg-rental-900 focus:outline-none focus:ring-2 focus:ring-primary"
              />
              <Button size="sm" className="bg-primary hover:bg-primary/90 text-white whitespace-nowrap">
                Subscribe
              </Button>
            </div>
          </div>
        </div>

        <div className="border-t border-rental-100 dark:border-rental-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-sm text-rental-500 dark:text-rental-400">
            © {new Date().getFullYear()} Jaston. All rights reserved.
          </p>
          <div className="flex space-x-6 mt-4 md:mt-0">
            <Link to="/terms" className="text-sm text-rental-500 dark:text-rental-400 hover:text-primary dark:hover:text-primary transition-colors">
              Terms of Service
            </Link>
            <Link to="/privacy" className="text-sm text-rental-500 dark:text-rental-400 hover:text-primary dark:hover:text-primary transition-colors">
              Privacy Policy
            </Link>
            <Link to="/cookies" className="text-sm text-rental-500 dark:text-rental-400 hover:text-primary dark:hover:text-primary transition-colors">
              Cookie Policy
            </Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
