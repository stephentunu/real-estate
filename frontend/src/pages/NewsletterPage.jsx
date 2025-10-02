/**
 * Newsletter Page
 * Main page for newsletter functionality - subscription and admin interface
 */

import React, { useState, useEffect } from 'react';
import Layout from '../components/Layout';
import NewsletterSubscriptionComponent from '../components/NewsletterSubscription.jsx';
import NewsletterAdminComponent from '../components/NewsletterAdmin.jsx';
import { useAuth } from '../contexts/AuthContext';
import newsletterService from '../services/newsletterService.js';

const NewsletterPage = () => {
    const { user, profile, loading } = useAuth();
    const [userSubscriptions, setUserSubscriptions] = useState([]);
    const [loadingSubscriptions, setLoadingSubscriptions] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('info');

    useEffect(() => {
        if (user) {
            loadUserSubscriptions();
        }
    }, [user]);

    const loadUserSubscriptions = async () => {
        setLoadingSubscriptions(true);
        try {
            const subscriptions = await newsletterService.NewsletterSubscription.getUserSubscriptions();
            setUserSubscriptions(subscriptions);
        } catch (error) {
            console.error('Error loading subscriptions:', error);
            setMessage('Failed to load your subscriptions');
            setMessageType('error');
        } finally {
            setLoadingSubscriptions(false);
        }
    };

    const handleUnsubscribe = async (subscriptionId) => {
        try {
            await newsletterService.NewsletterSubscription.unsubscribe(subscriptionId);
            setMessage('Successfully unsubscribed');
            setMessageType('success');
            await loadUserSubscriptions(); // Reload subscriptions
        } catch (error) {
            console.error('Error unsubscribing:', error);
            setMessage('Failed to unsubscribe');
            setMessageType('error');
        }
    };

    const handleReactivate = async (subscriptionId) => {
        try {
            await newsletterService.NewsletterSubscription.updateSubscription(subscriptionId, { is_active: true });
            setMessage('Subscription reactivated successfully');
            setMessageType('success');
            await loadUserSubscriptions(); // Reload subscriptions
        } catch (error) {
            console.error('Error reactivating subscription:', error);
            setMessage('Failed to reactivate subscription');
            setMessageType('error');
        }
    };

    const renderUserSubscriptions = () => {
        if (loadingSubscriptions) {
            return <div className="loading">Loading your subscriptions...</div>;
        }

        if (userSubscriptions.length === 0) {
            return (
                <div className="no-subscriptions">
                    <p>You don't have any newsletter subscriptions yet.</p>
                </div>
            );
        }

        return (
            <div className="user-subscriptions">
                <h3>Your Newsletter Subscriptions</h3>
                <div className="subscriptions-list">
                    {userSubscriptions.map(subscription => (
                        <div key={subscription.id} className={`subscription-item ${subscription.is_active ? 'active' : 'inactive'}`}>
                            <div className="subscription-info">
                                <p><strong>Email:</strong> {subscription.email}</p>
                                <p><strong>Frequency:</strong> {subscription.frequency}</p>
                                <p><strong>Categories:</strong> {subscription.categories.join(', ')}</p>
                                <p><strong>Status:</strong> {subscription.is_active ? 'Active' : 'Inactive'}</p>
                                <p><strong>Confirmed:</strong> {subscription.is_confirmed ? 'Yes' : 'No'}</p>
                            </div>
                            <div className="subscription-actions">
                                {subscription.is_active ? (
                                    <button 
                                        onClick={() => handleUnsubscribe(subscription.id)}
                                        className="btn btn-danger"
                                    >
                                        Unsubscribe
                                    </button>
                                ) : (
                                    <button 
                                        onClick={() => handleReactivate(subscription.id)}
                                        className="btn btn-success"
                                    >
                                        Reactivate
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        );
    };

    if (loading) {
        return (
            <Layout>
                <div className="newsletter-page loading-state">
                    <div className="container">
                        <div className="loading">Loading...</div>
                    </div>
                </div>
            </Layout>
        );
    }

    return (
        <Layout>
            <div className="newsletter-page">
                <div className="container">
                    <header className="page-header">
                        <h1>Newsletter</h1>
                        <p>Stay updated with our latest news and property listings</p>
                    </header>

                    {message && (
                        <div className={`message ${messageType}`}>
                            {message}
                            <button onClick={() => setMessage('')} className="close-btn">×</button>
                        </div>
                    )}

                    <div className="newsletter-content">
                        {/* Newsletter Subscription Section */}
                        <section className="subscription-section">
                            <h2>Subscribe to Our Newsletter</h2>
                            <div id="newsletter-subscription-container">
                                <NewsletterSubscriptionComponent />
                            </div>
                        </section>

                        {/* User Subscriptions Section */}
                        {user && (
                            <section className="user-subscriptions-section">
                                {renderUserSubscriptions()}
                            </section>
                        )}

                        {/* Admin Section */}
                        {user && profile && profile.is_staff && (
                            <section className="admin-section">
                                <h2>Newsletter Administration</h2>
                                <div id="newsletter-admin-container">
                                    <NewsletterAdminComponent />
                                </div>
                            </section>
                        )}
                    </div>
                </div>

                <style jsx>{`
                    .newsletter-page {
                        min-height: 100vh;
                        padding: 2rem 0;
                        background-color: #f8f9fa;
                    }

                    .container {
                        max-width: 1200px;
                        margin: 0 auto;
                        padding: 0 1rem;
                    }

                    .page-header {
                        text-align: center;
                        margin-bottom: 3rem;
                        padding: 2rem 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border-radius: 10px;
                    }

                    .page-header h1 {
                        font-size: 2.5rem;
                        margin-bottom: 0.5rem;
                        font-weight: 700;
                    }

                    .page-header p {
                        font-size: 1.1rem;
                        opacity: 0.9;
                    }

                    .message {
                        padding: 1rem;
                        margin-bottom: 2rem;
                        border-radius: 5px;
                        position: relative;
                        font-weight: 500;
                    }

                    .message.success {
                        background-color: #d4edda;
                        color: #155724;
                        border: 1px solid #c3e6cb;
                    }

                    .message.error {
                        background-color: #f8d7da;
                        color: #721c24;
                        border: 1px solid #f5c6cb;
                    }

                    .message.info {
                        background-color: #d1ecf1;
                        color: #0c5460;
                        border: 1px solid #bee5eb;
                    }

                    .close-btn {
                        position: absolute;
                        top: 0.5rem;
                        right: 1rem;
                        background: none;
                        border: none;
                        font-size: 1.5rem;
                        cursor: pointer;
                        color: inherit;
                    }

                    .newsletter-content {
                        display: grid;
                        gap: 3rem;
                    }

                    .subscription-section,
                    .user-subscriptions-section,
                    .admin-section {
                        background: white;
                        padding: 2rem;
                        border-radius: 10px;
                        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
                    }

                    .subscription-section h2,
                    .user-subscriptions-section h2,
                    .admin-section h2 {
                        color: #333;
                        margin-bottom: 1.5rem;
                        font-size: 1.8rem;
                        font-weight: 600;
                    }

                    .user-subscriptions h3 {
                        color: #555;
                        margin-bottom: 1rem;
                        font-size: 1.4rem;
                    }

                    .subscriptions-list {
                        display: grid;
                        gap: 1rem;
                    }

                    .subscription-item {
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        padding: 1.5rem;
                        border: 1px solid #e0e0e0;
                        border-radius: 8px;
                        background: #fafafa;
                    }

                    .subscription-item.active {
                        border-color: #28a745;
                        background: #f8fff9;
                    }

                    .subscription-item.inactive {
                        border-color: #dc3545;
                        background: #fff8f8;
                        opacity: 0.8;
                    }

                    .subscription-info p {
                        margin: 0.25rem 0;
                        color: #555;
                    }

                    .subscription-actions {
                        flex-shrink: 0;
                        margin-left: 1rem;
                    }

                    .btn {
                        padding: 0.5rem 1rem;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                        font-weight: 500;
                        transition: all 0.3s ease;
                    }

                    .btn-danger {
                        background-color: #dc3545;
                        color: white;
                    }

                    .btn-danger:hover {
                        background-color: #c82333;
                    }

                    .btn-success {
                        background-color: #28a745;
                        color: white;
                    }

                    .btn-success:hover {
                        background-color: #218838;
                    }

                    .loading {
                        text-align: center;
                        padding: 2rem;
                        color: #666;
                        font-size: 1.1rem;
                    }

                    .loading-state {
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        min-height: 50vh;
                    }

                    .no-subscriptions {
                        text-align: center;
                        padding: 2rem;
                        color: #666;
                    }

                    @media (max-width: 768px) {
                        .subscription-item {
                            flex-direction: column;
                            align-items: flex-start;
                        }

                        .subscription-actions {
                            margin-left: 0;
                            margin-top: 1rem;
                            width: 100%;
                        }

                        .btn {
                            width: 100%;
                        }

                        .page-header h1 {
                            font-size: 2rem;
                        }
                    }
                `}</style>
            </div>
        </Layout>
    );
};

export default NewsletterPage;