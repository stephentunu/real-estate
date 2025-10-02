
import React from 'react';
import Layout from '@/components/Layout';

const TermsPage = () => {
  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        <div className="container px-4 md:px-6 max-w-4xl">
          <h1 className="text-3xl font-bold mb-6">Terms of Service</h1>
          <p className="text-rental-600 dark:text-rental-400 mb-4">Last Updated: June 1, 2023</p>
          
          <div className="prose dark:prose-invert max-w-none">
            <p>
              Welcome to Jaston. These Terms of Service ("Terms") govern your access to and use of the Jaston website and services. By accessing or using our services, you agree to be bound by these Terms.
            </p>
            
            <h2>1. Acceptance of Terms</h2>
            <p>
              By accessing or using our services, you agree to be bound by these Terms and our Privacy Policy. If you do not agree to these Terms, you may not access or use our services.
            </p>
            
            <h2>2. Changes to Terms</h2>
            <p>
              We may revise these Terms from time to time. If we make material changes, we will notify you by email or through our services prior to the changes becoming effective. Your continued use of our services after the effective date of the revised Terms constitutes your acceptance of them.
            </p>
            
            <h2>3. Account Registration</h2>
            <p>
              To access certain features of our services, you may be required to register for an account. You must provide accurate and complete information and keep your account information updated. You are responsible for maintaining the confidentiality of your account credentials and for all activities that occur under your account.
            </p>
            
            <h2>4. User Conduct</h2>
            <p>
              You agree not to:
            </p>
            <ul>
              <li>Violate any applicable law or regulation</li>
              <li>Impersonate any person or entity</li>
              <li>Interfere with the operation of our services</li>
              <li>Engage in any fraudulent or deceptive activity</li>
              <li>Upload or transmit any viruses, malware, or other harmful code</li>
              <li>Attempt to gain unauthorized access to our systems or user accounts</li>
              <li>Use our services for any illegal or unauthorized purpose</li>
              <li>Harass, abuse, or harm another person</li>
            </ul>
            
            <h2>5. Property Listings</h2>
            <p>
              Property owners and managers who list properties on our platform agree to:
            </p>
            <ul>
              <li>Provide accurate and complete information about their properties</li>
              <li>Only list properties they have the legal right to rent or sell</li>
              <li>Comply with all applicable laws and regulations</li>
              <li>Respond to inquiries and booking requests in a timely manner</li>
              <li>Honor any bookings or agreements made through our platform</li>
            </ul>
            
            <h2>6. Booking and Payments</h2>
            <p>
              When you book a property through our services:
            </p>
            <ul>
              <li>You agree to pay all fees and charges associated with your booking</li>
              <li>You understand that bookings are subject to availability and confirmation</li>
              <li>You agree to comply with all property rules and policies</li>
              <li>You acknowledge that Jaston is not responsible for the condition or suitability of any property</li>
            </ul>
            
            <h2>7. Intellectual Property</h2>
            <p>
              The content, features, and functionality of our services are owned by Jaston and are protected by copyright, trademark, and other intellectual property laws. You may not copy, modify, distribute, sell, or lease any part of our services without our prior written consent.
            </p>
            
            <h2>8. Disclaimer of Warranties</h2>
            <p>
              Our services are provided "as is" and "as available" without any warranties of any kind, either express or implied, including but not limited to warranties of merchantability, fitness for a particular purpose, or non-infringement.
            </p>
            
            <h2>9. Limitation of Liability</h2>
            <p>
              To the maximum extent permitted by law, Jaston shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to loss of profits, data, or use, arising out of or in connection with these Terms or your use of our services.
            </p>
            
            <h2>10. Indemnification</h2>
            <p>
              You agree to indemnify, defend, and hold harmless Jaston and its officers, directors, employees, and agents from and against any claims, liabilities, damages, losses, and expenses, including reasonable attorneys' fees, arising out of or in any way connected with your access to or use of our services, your violation of these Terms, or your violation of any rights of another.
            </p>
            
            <h2>11. Governing Law</h2>
            <p>
              These Terms shall be governed by and construed in accordance with the laws of Kenya, without regard to its conflict of law provisions.
            </p>
            
            <h2>12. Dispute Resolution</h2>
            <p>
              Any dispute arising out of or relating to these Terms or our services shall be resolved through binding arbitration in accordance with the rules of the Nairobi Centre for International Arbitration.
            </p>
            
            <h2>13. Termination</h2>
            <p>
              We may terminate or suspend your access to our services at any time, without prior notice or liability, for any reason, including if you breach these Terms. Upon termination, your right to use our services will immediately cease.
            </p>
            
            <h2>14. Contact Information</h2>
            <p>
              If you have any questions about these Terms, please contact us at:
            </p>
            <p>
              Email: legal@jaston.co.ke<br />
              Phone: +254 712 345 678<br />
              Address: Westlands Business Park, Waiyaki Way, Nairobi, Kenya
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default TermsPage;
