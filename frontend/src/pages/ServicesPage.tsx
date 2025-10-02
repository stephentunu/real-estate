
import React from 'react';
import { Link } from 'react-router-dom';
import { Home, Building, CheckCircle, Key, ShieldCheck, ClipboardList, ArrowRight, Users, HeartHandshake, Briefcase } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Layout from '@/components/Layout';

const ServicesPage = () => {
  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        {/* Hero Section */}
        <div className="relative py-20 mb-16 overflow-hidden">
          <div className="absolute inset-0 z-0">
            <div className="absolute inset-0 bg-gradient-to-r from-rental-900/80 to-primary/50 z-10" />
            <img 
              src="https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?q=80&w=1000" 
              alt="Modern building" 
              className="w-full h-full object-cover object-center"
            />
          </div>
          
          <div className="container mx-auto px-6 relative z-20">
            <div className="max-w-3xl">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                Our Services
              </h1>
              <p className="text-lg md:text-xl text-white/90 mb-8">
                Comprehensive real estate solutions designed for property owners, investors, and tenants across Kenya.
              </p>
            </div>
          </div>
        </div>

        {/* Main Services */}
        <div className="container px-4 md:px-6 mb-20">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-3xl font-bold mb-4">What We Offer</h2>
            <p className="text-rental-600 dark:text-rental-400">
              Jaston provides comprehensive property management and real estate services to meet all your needs
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[
              {
                icon: <Home className="h-10 w-10 text-primary" />,
                title: "Property Rentals",
                description: "Find your perfect rental home from our extensive portfolio of quality properties across Kenya.",
                link: "/properties"
              },
              {
                icon: <Building className="h-10 w-10 text-primary" />,
                title: "Property Management",
                description: "We handle everything from tenant screening to maintenance, maximizing your investment returns.",
                link: "/property-management"
              },
              {
                icon: <Key className="h-10 w-10 text-primary" />,
                title: "Property Sales",
                description: "Looking to buy or sell? Our experienced agents will guide you through every step of the process.",
                link: "/property-sales"
              },
              {
                icon: <ClipboardList className="h-10 w-10 text-primary" />,
                title: "Property Listing",
                description: "List your property with us for maximum exposure to qualified tenants and buyers.",
                link: "/list-property"
              },
              {
                icon: <ShieldCheck className="h-10 w-10 text-primary" />,
                title: "Tenant Screening",
                description: "We conduct thorough background checks to ensure reliable tenants for your properties.",
                link: "/tenant-screening"
              },
              {
                icon: <HeartHandshake className="h-10 w-10 text-primary" />,
                title: "Real Estate Consulting",
                description: "Expert advice on property investments, market trends, and real estate strategy.",
                link: "/consulting"
              }
            ].map((service, index) => (
              <div key={index} className="bg-white dark:bg-rental-900 p-8 rounded-lg shadow-sm border border-rental-100 dark:border-rental-800 group hover:shadow-md transition-all">
                <div className="w-16 h-16 bg-primary/10 rounded-lg flex items-center justify-center mb-6">
                  {service.icon}
                </div>
                <h3 className="text-xl font-semibold mb-3">{service.title}</h3>
                <p className="text-rental-600 dark:text-rental-400 mb-6">
                  {service.description}
                </p>
                <Link 
                  to={service.link} 
                  className="inline-flex items-center text-primary font-medium group-hover:underline"
                >
                  Learn More
                  <ArrowRight size={16} className="ml-1" />
                </Link>
              </div>
            ))}
          </div>
        </div>

        {/* How It Works */}
        <div className="bg-rental-50 dark:bg-rental-900 py-20">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl font-bold mb-4">How It Works</h2>
              <p className="text-rental-600 dark:text-rental-400">
                Our streamlined process makes property management and rentals simple
              </p>
            </div>

            <div className="relative">
              {/* Process line */}
              <div className="hidden md:block absolute top-1/2 left-0 right-0 h-0.5 bg-rental-200 dark:bg-rental-700 -translate-y-1/2 z-0"></div>
              
              <div className="grid grid-cols-1 md:grid-cols-4 gap-8 relative z-10">
                {[
                  {
                    step: "01",
                    title: "Initial Consultation",
                    description: "We meet to understand your needs and goals, whether you're a property owner, buyer, or tenant."
                  },
                  {
                    step: "02",
                    title: "Customized Plan",
                    description: "We develop a tailored strategy based on your specific requirements and market conditions."
                  },
                  {
                    step: "03",
                    title: "Implementation",
                    description: "Our team executes the plan, handling all aspects of property management or the buying/selling process."
                  },
                  {
                    step: "04",
                    title: "Ongoing Support",
                    description: "We provide continuous service and regular updates to ensure long-term satisfaction."
                  }
                ].map((process, index) => (
                  <div key={index} className="bg-white dark:bg-rental-800 p-6 rounded-lg shadow-sm relative">
                    <div className="w-12 h-12 rounded-full bg-primary text-white flex items-center justify-center text-lg font-bold absolute -top-6 left-1/2 transform -translate-x-1/2">
                      {process.step}
                    </div>
                    <div className="mt-8 text-center">
                      <h3 className="text-lg font-semibold mb-3">{process.title}</h3>
                      <p className="text-rental-600 dark:text-rental-400">
                        {process.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>

        {/* Benefits */}
        <div className="container px-4 md:px-6 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
            <div>
              <h2 className="text-3xl font-bold mb-6">Why Choose Jaston</h2>
              <p className="text-rental-600 dark:text-rental-400 mb-8">
                With years of experience in the Kenyan real estate market, we offer unmatched expertise and service quality to our clients.
              </p>
              
              <div className="space-y-4">
                {[
                  {
                    title: "Local Expertise",
                    description: "Deep understanding of Kenya's real estate market and neighborhoods."
                  },
                  {
                    title: "Transparent Pricing",
                    description: "Clear fee structures with no hidden costs or surprises."
                  },
                  {
                    title: "Professional Team",
                    description: "Skilled agents and property managers dedicated to your success."
                  },
                  {
                    title: "Technology-Driven",
                    description: "Modern tools and systems for efficient property management."
                  },
                  {
                    title: "Customer-Focused",
                    description: "Personalized service tailored to your unique needs and goals."
                  }
                ].map((benefit, index) => (
                  <div key={index} className="flex">
                    <CheckCircle className="h-6 w-6 text-primary flex-shrink-0 mt-0.5" />
                    <div className="ml-3">
                      <h3 className="font-medium">{benefit.title}</h3>
                      <p className="text-rental-600 dark:text-rental-400 text-sm">
                        {benefit.description}
                      </p>
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8">
                <Button asChild>
                  <Link to="/contact">
                    Get Started Today
                  </Link>
                </Button>
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-4">
                <div className="rounded-lg overflow-hidden h-48">
                  <img 
                    src="https://images.unsplash.com/photo-1556912172-45b7abe8b7e1?q=80&w=1000" 
                    alt="Property management" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="rounded-lg overflow-hidden h-64">
                  <img 
                    src="https://images.unsplash.com/photo-1560518883-ce09059eeffa?q=80&w=1000" 
                    alt="Luxury property" 
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
              <div className="space-y-4 mt-6">
                <div className="rounded-lg overflow-hidden h-64">
                  <img 
                    src="https://images.unsplash.com/photo-1560749003-f4b1e17e2dff?q=80&w=1000" 
                    alt="Modern apartment" 
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="rounded-lg overflow-hidden h-48">
                  <img 
                    src="https://images.unsplash.com/photo-1555041469-a586c61ea9bc?q=80&w=1000" 
                    alt="Home interior" 
                    className="w-full h-full object-cover"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Client Types */}
        <div className="bg-primary py-20">
          <div className="container px-4 md:px-6">
            <div className="text-center max-w-3xl mx-auto mb-16">
              <h2 className="text-3xl font-bold text-white mb-4">Who We Serve</h2>
              <p className="text-white/80">
                Our services are designed for a wide range of clients in the Kenyan real estate market
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: <Users className="h-12 w-12 text-primary" />,
                  title: "Property Owners",
                  description: "We help property owners maximize returns through effective management and tenant placement.",
                  link: "/for-owners"
                },
                {
                  icon: <Home className="h-12 w-12 text-primary" />,
                  title: "Tenants",
                  description: "We connect tenants with quality rental properties that meet their needs and budget.",
                  link: "/for-tenants"
                },
                {
                  icon: <Briefcase className="h-12 w-12 text-primary" />,
                  title: "Investors",
                  description: "We provide strategic guidance to investors looking to build their real estate portfolio.",
                  link: "/for-investors"
                }
              ].map((client, index) => (
                <div key={index} className="bg-white dark:bg-rental-900 p-8 rounded-lg shadow-md text-center">
                  <div className="w-20 h-20 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
                    {client.icon}
                  </div>
                  <h3 className="text-xl font-semibold mb-3">{client.title}</h3>
                  <p className="text-rental-600 dark:text-rental-400 mb-6">
                    {client.description}
                  </p>
                  <Button asChild variant="outline">
                    <Link to={client.link}>
                      Learn More
                    </Link>
                  </Button>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="container px-4 md:px-6 py-20 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Get Started?</h2>
          <p className="text-rental-600 dark:text-rental-400 max-w-2xl mx-auto mb-8">
            Contact our team today to discuss how Jaston can help with your property management, rental, or real estate needs.
          </p>
          <Button asChild size="lg">
            <Link to="/contact">
              Contact Us Today
            </Link>
          </Button>
        </div>
      </div>
    </Layout>
  );
};

export default ServicesPage;
