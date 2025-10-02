
import React from 'react';
import { ArrowRight, CheckCircle, MapPin, Calendar, DollarSign } from 'lucide-react';
import { Button } from '@/components/ui/button';
import Layout from '@/components/Layout';

const CareersPage = () => {
  const jobs = [
    {
      id: '1',
      title: 'Property Manager',
      location: 'Nairobi, Kenya',
      type: 'Full-time',
      salary: 'KSh 70,000 - 100,000 per month',
      description: 'We\'re looking for an experienced Property Manager to join our Nairobi team, responsible for managing a portfolio of premium properties and ensuring client satisfaction.',
      requirements: [
        'Minimum 3 years experience in property management',
        'Strong customer service skills',
        'Knowledge of Kenyan real estate laws and regulations',
        'Excellent communication and negotiation skills',
        'Bachelor\'s degree in Real Estate, Business, or related field'
      ]
    },
    {
      id: '2',
      title: 'Sales Representative',
      location: 'Mombasa, Kenya',
      type: 'Full-time',
      salary: 'KSh 60,000 - 90,000 per month + commission',
      description: 'Join our sales team in Mombasa to help clients find their perfect properties. You\'ll be responsible for property viewings, client consultations, and closing deals.',
      requirements: [
        'Previous sales experience, preferably in real estate',
        'Strong interpersonal and communication skills',
        'Results-oriented with a drive to exceed targets',
        'Knowledge of the Mombasa property market',
        'Valid driver\'s license'
      ]
    },
    {
      id: '3',
      title: 'Marketing Specialist',
      location: 'Nairobi, Kenya',
      type: 'Full-time',
      salary: 'KSh 65,000 - 85,000 per month',
      description: 'We\'re seeking a creative Marketing Specialist to develop and implement marketing strategies that promote our properties and services across Kenya.',
      requirements: [
        'Bachelor\'s degree in Marketing, Communications, or related field',
        'Minimum 2 years experience in marketing, preferably in real estate',
        'Experience with digital marketing, content creation, and social media',
        'Strong analytical skills to track and measure campaign performance',
        'Excellent written and verbal communication skills'
      ]
    }
  ];

  const benefits = [
    {
      title: 'Competitive Salary',
      description: 'We offer competitive compensation packages to attract and retain the best talent.'
    },
    {
      title: 'Health Insurance',
      description: 'Comprehensive health coverage for you and your family.'
    },
    {
      title: 'Career Growth',
      description: 'Clear career progression paths and regular performance reviews.'
    },
    {
      title: 'Training & Development',
      description: 'Ongoing professional development opportunities and training programs.'
    },
    {
      title: 'Flexible Work Hours',
      description: 'We understand the importance of work-life balance.'
    },
    {
      title: 'Team Events',
      description: 'Regular team building activities and social events.'
    }
  ];

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        {/* Hero Section */}
        <div className="relative py-16 mb-16 overflow-hidden">
          <div className="absolute inset-0 z-0">
            <div className="absolute inset-0 bg-rental-900/70 z-10" />
            <img 
              src="https://images.unsplash.com/photo-1517245386807-bb43f82c33c4?q=80&w=1000" 
              alt="Jaston office" 
              className="w-full h-full object-cover object-center"
            />
          </div>
          
          <div className="container mx-auto px-6 relative z-20">
            <div className="max-w-3xl">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                Join Our Team
              </h1>
              <p className="text-lg md:text-xl text-white/90 mb-8">
                Help us transform Kenya\'s real estate experience by bringing your talent and passion to Jaston.
              </p>
            </div>
          </div>
        </div>

        <div className="container px-4 md:px-6">
          {/* Why Join Us */}
          <div className="mb-20">
            <div className="text-center max-w-3xl mx-auto mb-12">
              <h2 className="text-3xl font-bold mb-4">Why Work With Us?</h2>
              <p className="text-rental-600 dark:text-rental-400">
                At Jaston, we\'re building a team of passionate professionals dedicated to revolutionizing Kenya\'s real estate industry
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {benefits.map((benefit, index) => (
                <div key={index} className="bg-white dark:bg-rental-900 p-6 rounded-lg border border-rental-100 dark:border-rental-800">
                  <CheckCircle className="w-8 h-8 text-primary mb-4" />
                  <h3 className="text-lg font-semibold mb-2">{benefit.title}</h3>
                  <p className="text-rental-600 dark:text-rental-400">{benefit.description}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Open Positions */}
          <div>
            <div className="text-center max-w-3xl mx-auto mb-12">
              <h2 className="text-3xl font-bold mb-4">Open Positions</h2>
              <p className="text-rental-600 dark:text-rental-400">
                Explore current job opportunities at Jaston and find your next career move
              </p>
            </div>

            <div className="space-y-6">
              {jobs.map((job) => (
                <div key={job.id} className="bg-white dark:bg-rental-900 rounded-lg border border-rental-100 dark:border-rental-800 overflow-hidden hover:shadow-md transition-shadow">
                  <div className="p-6">
                    <div className="flex flex-col md:flex-row md:items-center md:justify-between mb-4">
                      <div>
                        <h3 className="text-xl font-semibold">{job.title}</h3>
                        <div className="flex flex-wrap gap-3 mt-2">
                          <div className="flex items-center text-sm text-rental-600 dark:text-rental-400">
                            <MapPin className="w-4 h-4 mr-1" />
                            {job.location}
                          </div>
                          <div className="flex items-center text-sm text-rental-600 dark:text-rental-400">
                            <Calendar className="w-4 h-4 mr-1" />
                            {job.type}
                          </div>
                          <div className="flex items-center text-sm text-rental-600 dark:text-rental-400">
                            <DollarSign className="w-4 h-4 mr-1" />
                            {job.salary}
                          </div>
                        </div>
                      </div>
                      <Button className="mt-4 md:mt-0">
                        Apply Now
                      </Button>
                    </div>
                    
                    <p className="text-rental-600 dark:text-rental-400 mb-4">
                      {job.description}
                    </p>
                    
                    <div>
                      <h4 className="font-medium mb-2">Requirements:</h4>
                      <ul className="list-disc pl-5 space-y-1 text-rental-600 dark:text-rental-400">
                        {job.requirements.map((req, index) => (
                          <li key={index}>{req}</li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {jobs.length === 0 && (
              <div className="text-center py-12">
                <p className="text-rental-600 dark:text-rental-400 mb-4">
                  No open positions at the moment. Please check back later or send us your resume.
                </p>
              </div>
            )}

            {/* General Application */}
            <div className="bg-rental-50 dark:bg-rental-900 rounded-lg p-8 mt-10 text-center">
              <h3 className="text-xl font-semibold mb-3">Don\'t see a position that fits your skills?</h3>
              <p className="text-rental-600 dark:text-rental-400 mb-6 max-w-2xl mx-auto">
                We\'re always looking for talented individuals to join our team. Send us your resume and let us know how you can contribute to Jaston\'s success.
              </p>
              <Button>
                Send General Application
                <ArrowRight size={16} className="ml-2" />
              </Button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CareersPage;
