
import React from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import Footer from './Footer';
import { MessagingWidget } from './messaging/MessagingWidget';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();
  
  return (
    <div className="flex flex-col min-h-screen">
      <Navbar />
      <main className="flex-grow transition-opacity duration-500 ease-in-out animate-fade-in">
        {children}
      </main>
      <Footer />
      <MessagingWidget />
    </div>
  );
};

export default Layout;
