
import React, { useState, useEffect } from 'react';
import { Facebook, Twitter, Linkedin } from 'lucide-react';
import Layout from '../components/Layout';
import { teamService, TeamMemberListItem } from '../services/teamService';

const TeamPage = () => {
  const [teamMembers, setTeamMembers] = useState<TeamMemberListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTeamMembers();
  }, []);

  const fetchTeamMembers = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await teamService.getTeamMembers({ is_active: true, ordering: 'display_order' });
      setTeamMembers(response.results);
    } catch (err) {
      console.error('Error fetching team members:', err);
      setError(err instanceof Error ? err.message : 'Failed to load team members');
      // Fallback to static data if API fails
      setTeamMembers([
        {
          id: 1,
          first_name: 'David',
          last_name: 'Kimani',
          position: 'Founder & CEO',
          profile_image: 'https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=1000',
          linkedin_url: '#',
          twitter_url: '#',
          facebook_url: '#',
          is_featured: true,
          display_order: 1,
          department: { id: 1, name: 'Executive', color: '#3B82F6' }
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    fetchTeamMembers();
  };

  // Fallback static data for display
  const staticTeamMembers = [
    {
      name: "David Kimani",
      title: "Founder & CEO",
      bio: "David founded Jaston in 2018 with a vision to transform the Kenyan real estate market. With over 15 years of experience in real estate and technology, he leads the company's strategic direction.",
      image: "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=1000",
      social: {
        linkedin: "#",
        twitter: "#",
        facebook: "#"
      }
    },
    {
      name: "Sarah Omondi",
      title: "Chief Operations Officer",
      bio: "Sarah oversees Jaston's day-to-day operations, ensuring efficient processes and excellent service delivery. She brings 12 years of operations management experience from the hospitality sector.",
      image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=1000",
      social: {
        linkedin: "#",
        twitter: "#",
        facebook: "#"
      }
    },
    {
      name: "Michael Njoroge",
      title: "Head of Property Management",
      bio: "Michael leads our property management division, working closely with property owners and tenants to deliver exceptional service. He has managed over 1,000 properties throughout his career.",
      image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=1000",
      social: {
        linkedin: "#",
        twitter: "#",
        facebook: "#"
      }
    },
    {
      name: "Grace Wanjiku",
      title: "Customer Experience Director",
      bio: "Grace ensures every client interaction exceeds expectations. Her background in customer service and psychology helps her create meaningful experiences for Jaston's clients.",
      image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1000",
      social: {
        linkedin: "#",
        twitter: "#",
        facebook: "#"
      }
    },
    {
      name: "James Mwangi",
      title: "Chief Technology Officer",
      bio: "James drives technological innovation at Jaston, developing solutions that make property management and rentals more efficient. He previously founded a successful proptech startup.",
      image: "https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?q=80&w=1000",
      social: {
        linkedin: "#",
        twitter: "#",
        facebook: "#"
      }
    },
    {
      name: "Lucy Kamau",
      title: "Head of Marketing",
      bio: "Lucy leads all marketing initiatives at Jaston, building brand awareness and driving growth. Her creative strategies have helped Jaston become a recognizable name in Kenyan real estate.",
      image: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?q=80&w=1000",
      social: {
        linkedin: "#",
        twitter: "#",
        facebook: "#"
      }
    },
    {
      name: "Daniel Ochieng",
      title: "Legal Counsel",
      bio: "Daniel handles all legal aspects of Jaston's operations, from contracts to compliance. His expertise in Kenyan property law ensures our services meet the highest legal standards.",
      image: "https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?q=80&w=1000",
      social: {
        linkedin: "#",
        twitter: "#",
        facebook: "#"
      }
    },
    {
      name: "Esther Ngugi",
      title: "Financial Controller",
      bio: "Esther manages Jaston's finances, ensuring sustainable growth and financial health. Her background in financial analysis helps her make strategic decisions for the company's future.",
      image: "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?q=80&w=1000",
      social: {
        linkedin: "#",
        twitter: "#",
        facebook: "#"
      }
    }
  ];

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        {/* Hero Section */}
        <div className="relative py-16 mb-16 overflow-hidden">
          <div className="absolute inset-0 z-0">
            <div className="absolute inset-0 bg-primary/70 z-10" />
            <img 
              src="https://images.unsplash.com/photo-1600880292203-757bb62b4baf?q=80&w=1000" 
              alt="Jaston team" 
              className="w-full h-full object-cover object-center"
            />
          </div>
          
          <div className="container mx-auto px-6 relative z-20">
            <div className="max-w-3xl">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                Meet Our Team
              </h1>
              <p className="text-lg md:text-xl text-white/90 mb-8">
                The passionate professionals behind Jaston, dedicated to transforming Kenya's real estate experience.
              </p>
            </div>
          </div>
        </div>
        
        <div className="container px-4 md:px-6">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-3xl font-bold mb-4">Our Leadership</h2>
            <p className="text-rental-600 dark:text-rental-400">
              Meet the experienced team guiding Jaston's mission to transform Kenyan real estate
            </p>
          </div>

          {loading ? (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
              <p className="text-rental-600 dark:text-rental-400">Loading team members...</p>
            </div>
          ) : error ? (
            <div className="text-center py-12">
              <p className="text-red-600 mb-4">Error loading team members: {error}</p>
              <button 
                onClick={handleRetry}
                className="bg-primary text-white px-4 py-2 rounded hover:bg-primary/90 transition-colors"
              >
                Retry
              </button>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {teamMembers.length > 0 ? teamMembers.map((member) => (
                 <div key={member.id} className="bg-white dark:bg-rental-900 rounded-lg overflow-hidden border border-rental-100 dark:border-rental-800 hover:shadow-md transition-shadow">
                   <div className="aspect-square overflow-hidden">
                     <img 
                       src={member.profile_image || 'https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=1000'} 
                       alt={`${member.first_name} ${member.last_name}`} 
                       className="w-full h-full object-cover"
                     />
                   </div>
                   <div className="p-6">
                     <h3 className="text-xl font-semibold mb-1">{`${member.first_name} ${member.last_name}`}</h3>
                     <p className="text-primary font-medium mb-3">{member.position}</p>
                     <p className="text-rental-600 dark:text-rental-400 text-sm mb-4 line-clamp-4">
                       {`${member.first_name} is a key member of our team at Jaston.`}
                     </p>
                     <div className="flex space-x-3">
                       {member.linkedin_url && (
                         <a href={member.linkedin_url} className="text-rental-400 hover:text-primary transition-colors">
                           <Linkedin size={18} />
                         </a>
                       )}
                       {member.twitter_url && (
                         <a href={member.twitter_url} className="text-rental-400 hover:text-primary transition-colors">
                           <Twitter size={18} />
                         </a>
                       )}
                       {member.facebook_url && (
                         <a href={member.facebook_url} className="text-rental-400 hover:text-primary transition-colors">
                           <Facebook size={18} />
                         </a>
                       )}
                     </div>
                   </div>
                 </div>
               )) : staticTeamMembers.map((member, index) => (
                 <div key={index} className="bg-white dark:bg-rental-900 rounded-lg overflow-hidden border border-rental-100 dark:border-rental-800 hover:shadow-md transition-shadow">
                   <div className="aspect-square overflow-hidden">
                     <img 
                       src={member.image} 
                       alt={member.name} 
                       className="w-full h-full object-cover"
                     />
                   </div>
                   <div className="p-6">
                     <h3 className="text-xl font-semibold mb-1">{member.name}</h3>
                     <p className="text-primary font-medium mb-3">{member.title}</p>
                     <p className="text-rental-600 dark:text-rental-400 text-sm mb-4 line-clamp-4">
                       {member.bio}
                     </p>
                     <div className="flex space-x-3">
                       <a href={member.social.linkedin} className="text-rental-400 hover:text-primary transition-colors">
                         <Linkedin size={18} />
                       </a>
                       <a href={member.social.twitter} className="text-rental-400 hover:text-primary transition-colors">
                         <Twitter size={18} />
                       </a>
                       <a href={member.social.facebook} className="text-rental-400 hover:text-primary transition-colors">
                         <Facebook size={18} />
                       </a>
                     </div>
                   </div>
                 </div>
               ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default TeamPage;
