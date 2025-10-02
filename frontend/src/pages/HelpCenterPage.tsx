
import React, { useState } from 'react';
import { Search, ChevronDown, ChevronUp, HelpCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import Layout from '@/components/Layout';

const HelpCenterPage = () => {
  const [activeCategory, setActiveCategory] = useState('general');
  const [expandedFaqs, setExpandedFaqs] = useState<string[]>([]);

  const toggleFaq = (id: string) => {
    if (expandedFaqs.includes(id)) {
      setExpandedFaqs(expandedFaqs.filter(faqId => faqId !== id));
    } else {
      setExpandedFaqs([...expandedFaqs, id]);
    }
  };

  const categories = [
    { id: 'general', name: 'General Questions' },
    { id: 'rentals', name: 'Rental Process' },
    { id: 'payments', name: 'Payments & Fees' },
    { id: 'account', name: 'Account Management' },
    { id: 'listings', name: 'Property Listings' },
    { id: 'landlords', name: 'For Landlords' }
  ];

  const faqs = {
    general: [
      {
        id: 'general-1',
        question: 'What is Jaston?',
        answer: 'Jaston is Kenya\'s premier property management and real estate platform, connecting property owners with tenants and providing comprehensive property management services.'
      },
      {
        id: 'general-2',
        question: 'How do I contact customer support?',
        answer: 'You can reach our customer support team by calling +254 712 345 678, emailing support@jaston.co.ke, or using the contact form on our Contact page.'
      },
      {
        id: 'general-3',
        question: 'What areas of Kenya do you cover?',
        answer: 'We currently cover major cities across Kenya including Nairobi, Mombasa, Kisumu, Nakuru, Eldoret, and their surrounding areas. We\'re continuously expanding to new locations.'
      },
      {
        id: 'general-4',
        question: 'Is Jaston only for residential properties?',
        answer: 'No, Jaston handles both residential and commercial properties. We offer services for apartments, houses, offices, retail spaces, and more.'
      }
    ],
    rentals: [
      {
        id: 'rentals-1',
        question: 'How do I apply for a rental property?',
        answer: 'To apply for a rental property, create an account on our platform, browse available listings, and click "Apply" on the property you\'re interested in. You\'ll need to complete an application form and provide necessary documentation.'
      },
      {
        id: 'rentals-2',
        question: 'What documents do I need to apply for a rental?',
        answer: 'Typically, you\'ll need identification (ID/passport), proof of income (pay stubs, employment letter), bank statements, references from previous landlords, and sometimes a credit report.'
      },
      {
        id: 'rentals-3',
        question: 'How long does the application process take?',
        answer: 'The application process usually takes 2-3 business days, depending on how quickly we can verify your information and check references.'
      }
    ],
    payments: [
      {
        id: 'payments-1',
        question: 'What payment methods are accepted for rent?',
        answer: 'We accept various payment methods including M-Pesa, bank transfers, credit/debit cards, and direct deposits. The specific methods available may vary by property.'
      },
      {
        id: 'payments-2',
        question: 'Do I need to pay a security deposit?',
        answer: 'Yes, most properties require a security deposit equivalent to 1-3 months\' rent, which is refundable at the end of your lease, subject to the condition of the property.'
      }
    ],
    account: [
      {
        id: 'account-1',
        question: 'How do I create an account?',
        answer: 'Click on the "Sign In" button at the top of the page, then select "Create Account". Fill in your details, verify your email, and you\'re all set.'
      },
      {
        id: 'account-2',
        question: 'How do I reset my password?',
        answer: 'On the sign-in page, click "Forgot password?", enter your email address, and follow the instructions sent to your email to reset your password.'
      }
    ],
    listings: [
      {
        id: 'listings-1',
        question: 'How often are new properties added?',
        answer: 'New properties are added daily. You can set up alerts to be notified when new listings matching your criteria become available.'
      },
      {
        id: 'listings-2',
        question: 'How do I schedule a viewing?',
        answer: 'On the property listing page, click the "Schedule Viewing" button and select your preferred date and time. Our team will confirm the appointment with you.'
      }
    ],
    landlords: [
      {
        id: 'landlords-1',
        question: 'How do I list my property with Jaston?',
        answer: 'To list your property, create a landlord account, click on "List Property", fill in the details about your property, upload photos, and submit for review.'
      },
      {
        id: 'landlords-2',
        question: 'What are the fees for property management services?',
        answer: 'Our property management fees typically range from 7-10% of the monthly rent, depending on the services required and the property type. Contact us for a custom quote.'
      }
    ]
  };

  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        {/* Hero Section */}
        <div className="bg-primary py-16 mb-16">
          <div className="container mx-auto px-6 text-center">
            <HelpCircle className="w-16 h-16 text-white/80 mx-auto mb-6" />
            <h1 className="text-4xl font-bold text-white mb-6">
              How Can We Help You?
            </h1>
            <p className="text-white/90 text-lg mb-8 max-w-2xl mx-auto">
              Find answers to common questions about Jaston's services and features.
            </p>
            <div className="max-w-2xl mx-auto relative">
              <Search className="absolute left-3 top-3 h-5 w-5 text-muted-foreground" />
              <Input 
                placeholder="Search for answers..."
                className="pl-10 py-6 text-base"
              />
              <Button className="absolute right-1 top-1">
                Search
              </Button>
            </div>
          </div>
        </div>

        <div className="container px-4 md:px-6">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Categories Sidebar */}
            <div className="md:w-1/4">
              <h2 className="text-xl font-semibold mb-4">Topics</h2>
              <nav className="space-y-1">
                {categories.map(category => (
                  <button
                    key={category.id}
                    onClick={() => setActiveCategory(category.id)}
                    className={`block w-full text-left px-4 py-2 rounded-md transition-colors ${
                      activeCategory === category.id
                        ? 'bg-primary text-white'
                        : 'hover:bg-rental-100 dark:hover:bg-rental-800'
                    }`}
                  >
                    {category.name}
                  </button>
                ))}
              </nav>

              <div className="mt-8 p-4 bg-rental-50 dark:bg-rental-900 rounded-lg">
                <h3 className="font-medium mb-2">Need More Help?</h3>
                <p className="text-sm text-rental-600 dark:text-rental-400 mb-4">
                  Can't find what you're looking for? Our support team is ready to assist you.
                </p>
                <Button asChild variant="default" size="sm" className="w-full">
                  <a href="/contact">
                    Contact Support
                  </a>
                </Button>
              </div>
            </div>

            {/* FAQs */}
            <div className="md:w-3/4">
              <h2 className="text-2xl font-bold mb-6">
                {categories.find(c => c.id === activeCategory)?.name}
              </h2>

              <div className="space-y-4">
                {faqs[activeCategory as keyof typeof faqs].map(faq => (
                  <div 
                    key={faq.id} 
                    className="border border-rental-100 dark:border-rental-800 rounded-lg overflow-hidden"
                  >
                    <button
                      className="w-full flex justify-between items-center p-4 text-left font-medium focus:outline-none"
                      onClick={() => toggleFaq(faq.id)}
                    >
                      {faq.question}
                      {expandedFaqs.includes(faq.id) ? (
                        <ChevronUp className="h-5 w-5 text-rental-500" />
                      ) : (
                        <ChevronDown className="h-5 w-5 text-rental-500" />
                      )}
                    </button>
                    {expandedFaqs.includes(faq.id) && (
                      <div className="p-4 pt-0 text-rental-600 dark:text-rental-400 border-t border-rental-100 dark:border-rental-800">
                        {faq.answer}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {faqs[activeCategory as keyof typeof faqs].length === 0 && (
                <div className="text-center py-12">
                  <p className="text-rental-600 dark:text-rental-400">
                    No FAQs available for this category.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default HelpCenterPage;
