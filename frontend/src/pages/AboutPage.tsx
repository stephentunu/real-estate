
import React from 'react';
import { Link } from 'react-router-dom';
import { CheckCircle, Users, Clock, Zap, Building, Award, Home } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Layout from '@/components/Layout';

const AboutPage = () => {
  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        {/* Hero Section */}
        <div className="relative py-20 mb-16 overflow-hidden">
          <div className="absolute inset-0 z-0">
            <div className="absolute inset-0 bg-primary/80 z-10" />
            <img 
              src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=1000" 
              alt="Jaston office" 
              className="w-full h-full object-cover object-center"
            />
          </div>
          
          <div className="container mx-auto px-6 relative z-20">
            <div className="max-w-3xl">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                About Jaston
              </h1>
              <p className="text-lg md:text-xl text-white/90 mb-8">
                Kenya's premier property management company, dedicated to connecting people with their dream homes and creating thriving communities.
              </p>
            </div>
          </div>
        </div>

        {/* Our Story */}
        <div className="container px-4 md:px-6 mb-20">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">Our Story</h2>
              <p className="text-rental-600 dark:text-rental-400 mb-4">
                Founded in 2018, Jaston emerged from a vision to transform Kenya's real estate landscape. What began as a small team of passionate real estate professionals has grown into one of Kenya's most trusted property management companies.
              </p>
              <p className="text-rental-600 dark:text-rental-400 mb-4">
                Our journey started with a simple mission: to create a transparent and efficient property rental platform that would make finding a home as easy as possible for Kenyans across the country.
              </p>
              <p className="text-rental-600 dark:text-rental-400">
                Today, we're proud to have helped thousands of families and individuals find their perfect homes, while providing property owners with reliable management services that maximize their investments.
              </p>
            </div>
            <div className="relative">
              <div className="rounded-lg overflow-hidden">
                <img 
                  src="https://images.unsplash.com/photo-1557804506-669a67965ba0?q=80&w=1000" 
                  alt="Jaston team" 
                  className="w-full h-auto"
                />
              </div>
              <div className="absolute -bottom-6 -left-6 bg-white dark:bg-rental-900 p-6 rounded-lg shadow-lg">
                <div className="flex items-center space-x-2 text-primary font-bold">
                  <Building className="h-5 w-5" />
                  <span>Since 2018</span>
                </div>
                <div className="mt-2 grid grid-cols-2 gap-4">
                  <div>
                    <p className="text-3xl font-bold">5000+</p>
                    <p className="text-sm text-rental-600 dark:text-rental-400">Properties Managed</p>
                  </div>
                  <div>
                    <p className="text-3xl font-bold">15K+</p>
                    <p className="text-sm text-rental-600 dark:text-rental-400">Happy Clients</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Our Values */}
        <div className="bg-rental-50 dark:bg-rental-900 py-20">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-3xl mx-auto mb-12">
              <h2 className="text-3xl font-bold mb-4">Our Values</h2>
              <p className="text-rental-600 dark:text-rental-400">
                These core principles guide everything we do at Jaston
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: <CheckCircle className="h-10 w-10 text-primary" />,
                  title: "Integrity",
                  description: "We believe in honest, transparent dealings with all our clients and partners. Trust is the foundation of our business."
                },
                {
                  icon: <Users className="h-10 w-10 text-primary" />,
                  title: "Community",
                  description: "We're committed to building and supporting thriving communities across Kenya through quality housing solutions."
                },
                {
                  icon: <Clock className="h-10 w-10 text-primary" />,
                  title: "Reliability",
                  description: "Our clients can count on us to deliver consistent, professional service every step of the way."
                },
                {
                  icon: <Zap className="h-10 w-10 text-primary" />,
                  title: "Innovation",
                  description: "We constantly seek new ways to improve our services and enhance the property management experience."
                },
                {
                  icon: <Award className="h-10 w-10 text-primary" />,
                  title: "Excellence",
                  description: "We strive for excellence in every interaction, transaction and property we manage."
                },
                {
                  icon: <Home className="h-10 w-10 text-primary" />,
                  title: "Accessibility",
                  description: "We believe everyone deserves access to quality housing, and work to make the process as smooth as possible."
                }
              ].map((value, index) => (
                <div key={index} className="bg-white dark:bg-rental-800 p-6 rounded-lg shadow-sm">
                  <div className="mb-4">{value.icon}</div>
                  <h3 className="text-xl font-semibold mb-2">{value.title}</h3>
                  <p className="text-rental-600 dark:text-rental-400">{value.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Team Preview */}
        <div className="container px-4 md:px-6 py-20">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-3xl font-bold mb-4">Meet Our Leadership</h2>
            <p className="text-rental-600 dark:text-rental-400">
              The experienced team behind Jaston's success
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                name: "David Kimani",
                title: "Founder & CEO",
                image: "https://images.unsplash.com/photo-1560250097-0b93528c311a?q=80&w=1000",
              },
              {
                name: "Sarah Omondi",
                title: "Chief Operations Officer",
                image: "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?q=80&w=1000",
              },
              {
                name: "Michael Njoroge",
                title: "Head of Property Management",
                image: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?q=80&w=1000",
              },
              {
                name: "Grace Wanjiku",
                title: "Customer Experience Director",
                image: "https://images.unsplash.com/photo-1580489944761-15a19d654956?q=80&w=1000",
              }
            ].map((member, index) => (
              <div key={index} className="text-center">
                <div className="rounded-full overflow-hidden w-48 h-48 mx-auto mb-4">
                  <img 
                    src={member.image} 
                    alt={member.name} 
                    className="w-full h-full object-cover"
                  />
                </div>
                <h3 className="text-xl font-semibold">{member.name}</h3>
                <p className="text-rental-600 dark:text-rental-400">{member.title}</p>
              </div>
            ))}
          </div>
          
          <div className="text-center mt-12">
            <Button asChild>
              <Link to="/team">
                Meet the Full Team
              </Link>
            </Button>
          </div>
        </div>

        {/* CTA */}
        <div className="bg-primary py-16">
          <div className="container px-4 md:px-6 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">Ready to Work With Us?</h2>
            <p className="text-white/90 max-w-2xl mx-auto mb-8">
              Whether you're looking for your next home or need help managing your property, our team is here to help you every step of the way.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4">
              <Button asChild variant="default" className="bg-white text-primary hover:bg-white/90">
                <Link to="/properties">Browse Properties</Link>
              </Button>
              <Button asChild variant="outline" className="text-white border-white hover:bg-white/10">
                <Link to="/contact">Contact Us</Link>
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AboutPage;
