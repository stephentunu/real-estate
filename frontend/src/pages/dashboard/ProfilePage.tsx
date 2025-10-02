
import React, { useState } from 'react';
import { UserCircle, MapPin, Mail, Phone, Edit } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent } from '@/components/ui/card';
import DashboardLayout from '@/components/DashboardLayout';
import { useToast } from '@/hooks/use-toast';

const ProfilePage = () => {
  const { toast } = useToast();
  const [isEditing, setIsEditing] = useState(false);
  
  // Mock user data
  const [userData, setUserData] = useState({
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+254 712 345 678',
    location: 'Nairobi, Kenya',
    bio: 'Property enthusiast and real estate investor with 5 years of experience in the Kenyan market.',
    profileImage: 'https://i.pravatar.cc/150?img=68'
  });

  const handleSaveProfile = () => {
    setIsEditing(false);
    toast({
      title: "Profile updated",
      description: "Your profile information has been saved successfully.",
    });
  };

  return (
    <DashboardLayout title="Profile">
      <Card>
        <CardContent className="p-6">
          <div className="flex flex-col md:flex-row gap-6">
            {/* Profile Image */}
            <div className="flex flex-col items-center">
              <div className="relative w-32 h-32 rounded-full overflow-hidden mb-4">
                <img 
                  src={userData.profileImage} 
                  alt={userData.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <Button variant="outline" size="sm" className="w-full">
                Change Photo
              </Button>
            </div>
            
            {/* Profile Info */}
            <div className="flex-grow">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Personal Information</h2>
                {!isEditing ? (
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setIsEditing(true)}
                  >
                    <Edit className="h-4 w-4 mr-2" />
                    Edit Profile
                  </Button>
                ) : (
                  <div className="space-x-2">
                    <Button 
                      variant="outline" 
                      size="sm"
                      onClick={() => setIsEditing(false)}
                    >
                      Cancel
                    </Button>
                    <Button 
                      size="sm"
                      onClick={handleSaveProfile}
                    >
                      Save Changes
                    </Button>
                  </div>
                )}
              </div>
              
              {isEditing ? (
                <div className="space-y-4">
                  <div>
                    <label className="text-sm font-medium mb-1 block">Full Name</label>
                    <Input 
                      value={userData.name}
                      onChange={(e) => setUserData({...userData, name: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Email</label>
                    <Input 
                      value={userData.email}
                      onChange={(e) => setUserData({...userData, email: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Phone</label>
                    <Input 
                      value={userData.phone}
                      onChange={(e) => setUserData({...userData, phone: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Location</label>
                    <Input 
                      value={userData.location}
                      onChange={(e) => setUserData({...userData, location: e.target.value})}
                    />
                  </div>
                  <div>
                    <label className="text-sm font-medium mb-1 block">Bio</label>
                    <Textarea 
                      value={userData.bio}
                      onChange={(e) => setUserData({...userData, bio: e.target.value})}
                      rows={4}
                    />
                  </div>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center">
                    <UserCircle className="h-5 w-5 text-rental-500 mr-3" />
                    <div>
                      <div className="text-sm text-rental-500 dark:text-rental-400">Full Name</div>
                      <div className="font-medium">{userData.name}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <Mail className="h-5 w-5 text-rental-500 mr-3" />
                    <div>
                      <div className="text-sm text-rental-500 dark:text-rental-400">Email</div>
                      <div className="font-medium">{userData.email}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <Phone className="h-5 w-5 text-rental-500 mr-3" />
                    <div>
                      <div className="text-sm text-rental-500 dark:text-rental-400">Phone</div>
                      <div className="font-medium">{userData.phone}</div>
                    </div>
                  </div>
                  <div className="flex items-center">
                    <MapPin className="h-5 w-5 text-rental-500 mr-3" />
                    <div>
                      <div className="text-sm text-rental-500 dark:text-rental-400">Location</div>
                      <div className="font-medium">{userData.location}</div>
                    </div>
                  </div>
                  <div>
                    <div className="text-sm text-rental-500 dark:text-rental-400 mb-1">Bio</div>
                    <p className="text-rental-900 dark:text-rental-100">{userData.bio}</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    </DashboardLayout>
  );
};

export default ProfilePage;
