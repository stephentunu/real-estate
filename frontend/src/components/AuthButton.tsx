import React, { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { Button } from '@/components/ui/button';
import { MiniLoader } from '@/components/ui/mini-loader';
import { User, LogOut } from 'lucide-react';
import { Link } from 'react-router-dom';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { handleAPIError } from '@/services/errorHandler';

export const AuthButton: React.FC = () => {
  const [isSigningOut, setIsSigningOut] = useState(false);
  
  // Always call useAuth hook - handle errors in the component logic
  const auth = useAuth();
  
  if (!auth) {
    // If auth context is not available, show sign in button
    return (
      <Button asChild variant="ghost" size="sm" className="text-gray-800 dark:text-gray-100 hover:text-primary hover:bg-primary/10">
        <Link to="/auth">
          <User className="h-4 w-4 mr-2" />
          Sign In
        </Link>
      </Button>
    );
  }

  const { user, profile, signOut, loading } = auth;

  const handleSignOut = async () => {
    setIsSigningOut(true);
    try {
      await signOut();
    } catch (error) {
      handleAPIError(error, 'Signing out');
    } finally {
      setIsSigningOut(false);
    }
  };

    if (loading) {
      return (
        <Button variant="ghost" size="sm" disabled>
          <MiniLoader size="sm" className="mr-2" />
          Loading...
        </Button>
      );
    }

    if (!user) {
      return (
        <Button asChild variant="ghost" size="sm" className="text-gray-800 dark:text-gray-100 hover:text-primary hover:bg-primary/10">
          <Link to="/auth">
            <User className="h-4 w-4 mr-2" />
            Sign In
          </Link>
        </Button>
      );
    }

    return (
      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="sm" className="text-gray-800 dark:text-gray-100 hover:text-primary hover:bg-primary/10">
            <User className="h-4 w-4 mr-2" />
            {profile?.full_name || user.email}
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem asChild>
            <Link to="/dashboard">Dashboard</Link>
          </DropdownMenuItem>
          <DropdownMenuItem asChild>
            <Link to="/dashboard/profile">Profile</Link>
          </DropdownMenuItem>
          <DropdownMenuItem 
            onClick={handleSignOut}
            disabled={isSigningOut}
            className="cursor-pointer"
          >
            {isSigningOut ? (
              <>
                <MiniLoader size="sm" className="mr-2" />
                Signing out...
              </>
            ) : (
              <>
                <LogOut className="h-4 w-4 mr-2" />
                Sign out
              </>
            )}
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    );
};