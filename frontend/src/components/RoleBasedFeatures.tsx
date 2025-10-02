import React from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { useFeatures } from '@/hooks/useFeatures';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';
import { MiniLoader } from '@/components/ui/mini-loader';
import { Badge } from '@/components/ui/badge';
import { useToast } from '@/hooks/use-toast';
import { handleAPIError } from '@/services/errorHandler';
import { 
  MessageSquare, 
  Shield, 
  BarChart3, 
  Star,
  Settings,
  Users,
  TrendingUp
} from 'lucide-react';

const featureIcons: Record<string, React.ReactNode> = {
  messaging: <MessageSquare className="h-5 w-5" />,
  insurance: <Shield className="h-5 w-5" />,
  analytics: <BarChart3 className="h-5 w-5" />,
  premium_listings: <Star className="h-5 w-5" />,
};

export const RoleBasedFeatures: React.FC = () => {
  const { profile } = useAuth();
  const { 
    features, 
    userFeatures, 
    loading, 
    enableFeature, 
    disableFeature, 
    hasFeature 
  } = useFeatures();
  const { toast } = useToast();

  const handleFeatureToggle = async (featureId: string, enabled: boolean) => {
    try {
      if (enabled) {
        await enableFeature(featureId);
        toast({
          title: "Feature enabled",
          description: "The feature has been enabled for your account.",
        });
      } else {
        await disableFeature(featureId);
        toast({
          title: "Feature disabled", 
          description: "The feature has been disabled for your account.",
        });
      }
    } catch (error) {
      handleAPIError(error, 'Updating feature settings');
    }
  };

  const getRoleDisplayName = (role: string) => {
    const roleNames: Record<string, string> = {
      buyer: 'Property Seeker',
      seller: 'Property Owner',
      agent: 'Real Estate Agent',
      admin: 'Administrator'
    };
    return roleNames[role] || role;
  };

  const getRoleDescription = (role: string) => {
    const descriptions: Record<string, string> = {
      buyer: 'Find and secure your perfect property with our comprehensive search and viewing tools.',
      seller: 'List your properties and connect with potential buyers through our powerful platform.',
      agent: 'Manage multiple listings, track leads, and access advanced analytics to grow your business.',
      admin: 'Full platform access with advanced management and analytics capabilities.'
    };
    return descriptions[role] || '';
  };

  const getRoleIcon = (role: string) => {
    const icons: Record<string, React.ReactNode> = {
      buyer: <Users className="h-6 w-6" />,
      seller: <TrendingUp className="h-6 w-6" />,
      agent: <BarChart3 className="h-6 w-6" />,
      admin: <Settings className="h-6 w-6" />
    };
    return icons[role] || <Users className="h-6 w-6" />;
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <MiniLoader size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* User Role Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-primary/10 rounded-lg">
              {getRoleIcon(profile?.user_role || 'buyer')}
            </div>
            <div>
              <CardTitle className="flex items-center space-x-2">
                <span>{getRoleDisplayName(profile?.user_role || 'buyer')}</span>
                <Badge variant="secondary">{profile?.user_role || 'buyer'}</Badge>
              </CardTitle>
              <CardDescription>
                {getRoleDescription(profile?.user_role || 'buyer')}
              </CardDescription>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* Available Features */}
      <Card>
        <CardHeader>
          <CardTitle>Available Features</CardTitle>
          <CardDescription>
            Features available for your account type. Toggle them on or off as needed.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {features.map((feature) => {
              const isEnabled = hasFeature(feature.name);
              
              return (
                <div 
                  key={feature.id}
                  className="flex items-center justify-between p-4 rounded-lg border border-border"
                >
                  <div className="flex items-center space-x-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      {featureIcons[feature.name] || <Settings className="h-5 w-5" />}
                    </div>
                    <div>
                      <h4 className="font-medium">{feature.display_name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {feature.description}
                      </p>
                    </div>
                  </div>
                  <Switch
                    checked={isEnabled}
                    onCheckedChange={(checked) => 
                      handleFeatureToggle(feature.id, checked)
                    }
                  />
                </div>
              );
            })}
            
            {features.length === 0 && (
              <div className="text-center py-8 text-muted-foreground">
                <Settings className="h-8 w-8 mx-auto mb-3 opacity-50" />
                <p>No features available for your account type.</p>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Feature Benefits by Role */}
      <Card>
        <CardHeader>
          <CardTitle>Upgrade Your Experience</CardTitle>
          <CardDescription>
            See what's available when you upgrade your account type.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {profile?.user_role === 'buyer' && (
              <div className="p-4 border border-border rounded-lg">
                <h4 className="font-medium flex items-center space-x-2 mb-2">
                  <TrendingUp className="h-4 w-4" />
                  <span>Become a Property Owner</span>
                </h4>
                <p className="text-sm text-muted-foreground mb-3">
                  List your own properties and access seller tools.
                </p>
                <Button variant="outline" size="sm">
                  Upgrade Account
                </Button>
              </div>
            )}
            
            {(profile?.user_role === 'buyer' || profile?.user_role === 'seller') && (
              <div className="p-4 border border-border rounded-lg">
                <h4 className="font-medium flex items-center space-x-2 mb-2">
                  <BarChart3 className="h-4 w-4" />
                  <span>Agent Account</span>
                </h4>
                <p className="text-sm text-muted-foreground mb-3">
                  Access advanced analytics and manage multiple listings.
                </p>
                <Button variant="outline" size="sm">
                  Apply as Agent
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};