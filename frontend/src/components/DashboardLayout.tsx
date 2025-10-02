
import React from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { 
  User, Home, Heart, Calendar, Bell, Settings, 
  LogOut, CreditCard, File, Menu, X, MessageCircle, Mail
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import Layout from '@/components/Layout';
import { useToast } from '@/hooks/use-toast';
import { cn } from '@/lib/utils';

interface DashboardLayoutProps {
  children: React.ReactNode;
  title?: string;
}

const DashboardLayout = ({ children, title = "Dashboard" }: DashboardLayoutProps) => {
  const location = useLocation();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [mobileMenuOpen, setMobileMenuOpen] = React.useState(false);

  // Mock user data
  const userData = {
    name: 'John Doe',
    email: 'john.doe@example.com',
    joinDate: 'January 2023',
    profileImage: 'https://i.pravatar.cc/150?img=68'
  };

  const handleSignOut = () => {
    toast({
      title: "Success",
      description: "You have been signed out successfully.",
    });
    navigate('/');
  };

  const navItems = [
    { path: '/dashboard/profile', label: 'Profile', icon: User },
    { path: '/dashboard/properties', label: 'Properties', icon: Home },
    { path: '/dashboard/saved', label: 'Saved', icon: Heart },
    { path: '/dashboard/appointments', label: 'Appointments', icon: Calendar },
    { path: '/dashboard/messages', label: 'Messages', icon: MessageCircle },
    { path: '/newsletter', label: 'Newsletter', icon: Mail },
    { path: '/dashboard/notifications', label: 'Notifications', icon: Bell },
    { path: '/dashboard/payments', label: 'Payments', icon: CreditCard },
    { path: '/dashboard/settings', label: 'Settings', icon: Settings },
  ];

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        <div className="container px-4 md:px-6">
          <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
            {/* Mobile menu toggle */}
            <div className="md:hidden flex items-center justify-between mb-4 col-span-1">
              <h1 className="text-2xl font-bold">{title}</h1>
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              >
                {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
              </Button>
            </div>

            {/* Sidebar */}
            <div className={cn(
              "md:col-span-3",
              mobileMenuOpen ? "block" : "hidden md:block"
            )}>
              <div className="bg-white dark:bg-rental-900 border border-rental-100 dark:border-rental-800 rounded-lg p-6 sticky top-24">
                <div className="flex flex-col items-center mb-6">
                  <div className="relative w-20 h-20 rounded-full overflow-hidden mb-4">
                    <img 
                      src={userData.profileImage} 
                      alt={userData.name}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  <h3 className="text-lg font-semibold">{userData.name}</h3>
                  <p className="text-sm text-rental-600 dark:text-rental-400">{userData.email}</p>
                  <p className="text-xs text-rental-500 dark:text-rental-500 mt-1">
                    Member since {userData.joinDate}
                  </p>
                </div>
                
                <nav className="space-y-1">
                  {navItems.map((item) => (
                    <Link key={item.path} to={item.path}>
                      <Button 
                        variant="ghost" 
                        className={cn(
                          "w-full justify-start",
                          location.pathname === item.path && "bg-rental-100 dark:bg-rental-800"
                        )}
                      >
                        <item.icon className="mr-2 h-4 w-4" />
                        {item.label}
                      </Button>
                    </Link>
                  ))}
                  <Button 
                    variant="ghost" 
                    className="w-full justify-start text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-950/20"
                    onClick={handleSignOut}
                  >
                    <LogOut className="mr-2 h-4 w-4" />
                    Sign Out
                  </Button>
                </nav>
              </div>
            </div>
            
            {/* Main Content */}
            <div className="md:col-span-9">
              <h1 className="text-3xl font-bold mb-6 hidden md:block">{title}</h1>
              {children}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default DashboardLayout;
