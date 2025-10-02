
import React from 'react';
import Layout from '@/components/Layout';

const PrivacyPolicyPage = () => {
  return (
    <Layout>
      <div className="pt-24 pb-16 min-h-screen">
        <div className="container px-4 md:px-6 max-w-4xl">
          <h1 className="text-3xl font-bold mb-6">Privacy Policy</h1>
          <p className="text-rental-600 dark:text-rental-400 mb-4">Last Updated: June 1, 2023</p>
          
          <div className="prose dark:prose-invert max-w-none">
            <p>
              At Jaston, we are committed to protecting your privacy and ensuring the security of your personal information. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you visit our website or use our services.
            </p>
            
            <h2>Information We Collect</h2>
            <p>
              We collect information that you provide directly to us, information we collect automatically when you use our services, and information from third parties.
            </p>
            
            <h3>Information You Provide to Us</h3>
            <ul>
              <li>Personal identification information (name, email address, phone number)</li>
              <li>Login credentials</li>
              <li>Profile information (employment details, income, identification documents)</li>
              <li>Payment information</li>
              <li>Information you provide in communications with us</li>
            </ul>
            
            <h3>Information We Collect Automatically</h3>
            <ul>
              <li>Usage information (IP address, browser type, operating system)</li>
              <li>Device information</li>
              <li>Location information</li>
              <li>Cookies and similar technologies</li>
            </ul>
            
            <h2>How We Use Your Information</h2>
            <p>We may use the information we collect for various purposes, including to:</p>
            <ul>
              <li>Provide, maintain, and improve our services</li>
              <li>Process transactions and send related information</li>
              <li>Send you technical notices, updates, and administrative messages</li>
              <li>Respond to your comments, questions, and requests</li>
              <li>Communicate with you about products, services, and events</li>
              <li>Monitor and analyze trends, usage, and activities</li>
              <li>Detect, investigate, and prevent fraudulent transactions and other illegal activities</li>
              <li>Personalize and improve your experience</li>
            </ul>
            
            <h2>Sharing of Information</h2>
            <p>We may share your information in the following situations:</p>
            <ul>
              <li>With property owners or tenants as part of our services</li>
              <li>With third-party service providers who perform services on our behalf</li>
              <li>In connection with a business transaction (merger, acquisition, sale)</li>
              <li>If we believe disclosure is necessary to comply with any law, regulation, or legal process</li>
              <li>To protect the rights, property, and safety of Jaston, our users, and others</li>
              <li>With your consent or at your direction</li>
            </ul>
            
            <h2>Your Choices</h2>
            <p>You have several choices regarding the information we collect and how it's used:</p>
            <ul>
              <li>Account Information: You may update or correct your account information at any time by logging into your account</li>
              <li>Cookies: Most web browsers are set to accept cookies by default. You can usually set your browser to remove or reject cookies</li>
              <li>Promotional Communications: You may opt out of receiving promotional communications from us by following the instructions in those communications</li>
            </ul>
            
            <h2>Data Security</h2>
            <p>
              We take reasonable measures to help protect your personal information from loss, theft, misuse, and unauthorized access, disclosure, alteration, and destruction. However, no security system is impenetrable, and we cannot guarantee the security of our systems.
            </p>
            
            <h2>International Data Transfers</h2>
            <p>
              Your information may be transferred to, and maintained on, computers located outside of your country or jurisdiction where the data protection laws may differ from those in your jurisdiction.
            </p>
            
            <h2>Children's Privacy</h2>
            <p>
              Our services are not directed to children under 18, and we do not knowingly collect personal information from children under 18. If we learn we have collected personal information from a child under 18, we will delete that information.
            </p>
            
            <h2>Changes to This Privacy Policy</h2>
            <p>
              We may update this Privacy Policy from time to time. If we make material changes, we will notify you by email or through our services prior to the changes becoming effective.
            </p>
            
            <h2>Contact Us</h2>
            <p>
              If you have any questions about this Privacy Policy, please contact us at:
            </p>
            <p>
              Email: privacy@jaston.co.ke<br />
              Phone: +254 712 345 678<br />
              Address: Westlands Business Park, Waiyaki Way, Nairobi, Kenya
            </p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PrivacyPolicyPage;
