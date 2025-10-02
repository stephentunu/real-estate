
import React, { useState } from 'react';
import { MapPin, Phone, Mail, Clock, Send } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Layout from '@/components/Layout';
import { useToast } from '@/hooks/use-toast';

const ContactPage = () => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const { toast } = useToast();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);

    // Simulate form submission
    setTimeout(() => {
      setIsLoading(false);
      toast({
        title: "Message sent",
        description: "Thank you for contacting us. We'll get back to you soon!",
      });
      setFormData({
        name: '',
        email: '',
        phone: '',
        subject: '',
        message: ''
      });
    }, 1500);
  };

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        {/* Hero Section */}
        <div className="relative py-16 mb-16 overflow-hidden">
          <div className="absolute inset-0 z-0">
            <div className="absolute inset-0 bg-rental-900/70 z-10" />
            <img 
              src="https://images.unsplash.com/photo-1497366754035-f200968a6e72?q=80&w=1000" 
              alt="Jaston office" 
              className="w-full h-full object-cover object-center"
            />
          </div>
          
          <div className="container mx-auto px-6 relative z-20">
            <div className="max-w-3xl">
              <h1 className="text-4xl md:text-5xl font-bold text-white mb-6 leading-tight">
                Contact Us
              </h1>
              <p className="text-lg md:text-xl text-white/90 mb-8">
                We're here to help you with any questions or concerns about our properties or services.
              </p>
            </div>
          </div>
        </div>

        <div className="container px-4 md:px-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-12">
            {/* Contact Information */}
            <div className="lg:col-span-1">
              <h2 className="text-2xl font-bold mb-6">Get in Touch</h2>
              <div className="space-y-6">
                <div className="flex space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <MapPin className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium mb-1">Our Office</h3>
                    <p className="text-rental-600 dark:text-rental-400">
                      Westlands Business Park<br />
                      Waiyaki Way, Nairobi<br />
                      Kenya
                    </p>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Phone className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium mb-1">Phone</h3>
                    <p className="text-rental-600 dark:text-rental-400">
                      +254 712 345 678<br />
                      +254 734 567 890
                    </p>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Mail className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium mb-1">Email</h3>
                    <p className="text-rental-600 dark:text-rental-400">
                      info@jaston.co.ke<br />
                      support@jaston.co.ke
                    </p>
                  </div>
                </div>

                <div className="flex space-x-4">
                  <div className="flex-shrink-0">
                    <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                      <Clock className="h-5 w-5 text-primary" />
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-medium mb-1">Office Hours</h3>
                    <p className="text-rental-600 dark:text-rental-400">
                      Monday - Friday: 8:00 AM - 5:00 PM<br />
                      Saturday: 9:00 AM - 1:00 PM<br />
                      Sunday: Closed
                    </p>
                  </div>
                </div>
              </div>

              <div className="mt-8 p-4 bg-rental-50 dark:bg-rental-800 rounded-lg">
                <h3 className="font-medium mb-2">Find Us on Map</h3>
                <div className="h-60 bg-rental-200 dark:bg-rental-700 rounded-lg overflow-hidden">
                  {/* Placeholder for the map. In a real implementation, this would be a Google Maps or similar integration */}
                  <div className="w-full h-full flex items-center justify-center bg-rental-100 dark:bg-rental-800">
                    <MapPin className="h-8 w-8 text-primary/50" />
                    <span className="ml-2 text-rental-600 dark:text-rental-400">Map Loading...</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Contact Form */}
            <div className="lg:col-span-2">
              <div className="bg-white dark:bg-rental-900 p-8 rounded-lg shadow-sm border border-rental-100 dark:border-rental-800">
                <h2 className="text-2xl font-bold mb-6">Send Us a Message</h2>
                
                <form onSubmit={handleSubmit} className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium" htmlFor="name">Full Name</label>
                      <Input 
                        id="name"
                        name="name"
                        placeholder="Enter your name" 
                        value={formData.name}
                        onChange={handleInputChange}
                        required
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium" htmlFor="email">Email Address</label>
                      <Input 
                        id="email"
                        name="email"
                        type="email"
                        placeholder="Enter your email" 
                        value={formData.email}
                        onChange={handleInputChange}
                        required
                      />
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="space-y-2">
                      <label className="text-sm font-medium" htmlFor="phone">Phone Number</label>
                      <Input 
                        id="phone"
                        name="phone"
                        placeholder="Enter your phone number" 
                        value={formData.phone}
                        onChange={handleInputChange}
                      />
                    </div>

                    <div className="space-y-2">
                      <label className="text-sm font-medium" htmlFor="subject">Subject</label>
                      <select 
                        id="subject"
                        name="subject"
                        className="w-full px-3 py-2 text-base rounded-md border border-input bg-background ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm h-10" 
                        value={formData.subject}
                        onChange={handleInputChange}
                        required
                      >
                        <option value="">Select a subject</option>
                        <option value="property-inquiry">Property Inquiry</option>
                        <option value="rental-application">Rental Application</option>
                        <option value="property-management">Property Management</option>
                        <option value="general-question">General Question</option>
                        <option value="feedback">Feedback</option>
                      </select>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <label className="text-sm font-medium" htmlFor="message">Message</label>
                    <textarea 
                      id="message"
                      name="message"
                      placeholder="Type your message here" 
                      className="w-full px-3 py-2 text-base rounded-md border border-input bg-background ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 md:text-sm min-h-[120px]" 
                      value={formData.message}
                      onChange={handleInputChange}
                      required
                    />
                  </div>

                  <Button type="submit" disabled={isLoading} className="w-full md:w-auto">
                    {isLoading ? (
                      "Sending..."
                    ) : (
                      <>
                        <Send className="h-4 w-4 mr-2" />
                        Send Message
                      </>
                    )}
                  </Button>
                </form>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default ContactPage;
