/**
 * Ultra-Sleek Newsletter Subscription Component
 * Modern React component with Tailwind CSS styling and smooth animations
 */

import React, { useState, useEffect } from 'react';
import { NewsletterSubscription, NewsletterUtils } from '../services/newsletterService.js';

const NewsletterSubscriptionComponent = ({ 
    showCategories = true, 
    showFrequency = true, 
    theme = 'light' 
}) => {
    const [categories, setCategories] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [messageType, setMessageType] = useState('');
    const [formData, setFormData] = useState({
        email: '',
        frequency: 'weekly',
        categories: []
    });
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        loadCategories();
        // Trigger entrance animation
        setTimeout(() => setIsVisible(true), 100);
    }, []);

    const loadCategories = async () => {
        try {
            const loadedCategories = await NewsletterUtils.getCategories();
            setCategories(loadedCategories);
        } catch (error) {
            console.error('Failed to load categories:', error);
            const fallbackCategories = ['General', 'Property Updates', 'Market News'];
            setCategories(fallbackCategories);
        }
    };

    const handleInputChange = (e) => {
        const { name, value, type, checked } = e.target;
        
        if (type === 'checkbox') {
            setFormData(prev => ({
                ...prev,
                categories: checked 
                    ? [...prev.categories, value]
                    : prev.categories.filter(cat => cat !== value)
            }));
        } else {
            setFormData(prev => ({
                ...prev,
                [name]: value
            }));
        }
    };

    const validateEmail = (email) => {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    };

    const showError = (errorMessage) => {
        setMessage(errorMessage);
        setMessageType('error');
        setTimeout(() => setMessage(''), 5000);
    };

    const showSuccess = (successMessage) => {
        setMessage(successMessage);
        setMessageType('success');
        setTimeout(() => setMessage(''), 5000);
    };

    const handleSubmit = async (event) => {
        event.preventDefault();
        
        if (isLoading) return;
        
        if (!validateEmail(formData.email)) {
            showError('Please enter a valid email address');
            return;
        }

        setIsLoading(true);

        try {
            const response = await NewsletterSubscription.subscribe({
                email: formData.email,
                frequency: formData.frequency,
                categories: formData.categories
            });

            showSuccess('🎉 Welcome aboard! Check your email to confirm your subscription.');
            setFormData({
                email: '',
                frequency: 'weekly',
                categories: []
            });
            
        } catch (error) {
            showError(error.message || 'Oops! Something went wrong. Please try again.');
        } finally {
            setIsLoading(false);
        }
    };

    const frequencyOptions = [
        { value: 'daily', label: 'Daily', description: 'Stay updated every day' },
        { value: 'weekly', label: 'Weekly', description: 'Perfect weekly digest' },
        { value: 'monthly', label: 'Monthly', description: 'Monthly highlights' }
    ];

    return (
        <div className={`
            relative max-w-2xl mx-auto p-8 
            bg-gradient-to-br from-white via-gray-50 to-blue-50
            dark:from-gray-900 dark:via-gray-800 dark:to-blue-900
            rounded-3xl shadow-2xl border border-gray-200/50 dark:border-gray-700/50
            backdrop-blur-sm
            transform transition-all duration-1000 ease-out
            ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-8 opacity-0'}
        `}>
            {/* Decorative Elements */}
            <div className="absolute -top-4 -right-4 w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full opacity-20 blur-xl"></div>
            <div className="absolute -bottom-6 -left-6 w-32 h-32 bg-gradient-to-br from-green-400 to-blue-500 rounded-full opacity-15 blur-2xl"></div>
            
            {/* Header */}
            <div className="text-center mb-8 relative z-10">
                <div className="inline-flex items-center justify-center w-16 h-16 bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl mb-4 shadow-lg">
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                </div>
                <h3 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-600 dark:from-white dark:to-gray-300 bg-clip-text text-transparent mb-2">
                    Stay in the Loop
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-lg">
                    Get the latest property insights delivered to your inbox
                </p>
            </div>

            {/* Message Display */}
            {message && (
                <div className={`
                    mb-6 p-4 rounded-2xl border backdrop-blur-sm
                    transform transition-all duration-500 ease-out animate-fade-up
                    ${messageType === 'error' 
                        ? 'bg-red-50/80 border-red-200 text-red-700 dark:bg-red-900/20 dark:border-red-800 dark:text-red-400' 
                        : 'bg-green-50/80 border-green-200 text-green-700 dark:bg-green-900/20 dark:border-green-800 dark:text-green-400'
                    }
                `}>
                    <div className="flex items-center gap-3">
                        {messageType === 'error' ? (
                            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                            </svg>
                        ) : (
                            <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                            </svg>
                        )}
                        <span className="font-medium">{message}</span>
                    </div>
                </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-8">
                {/* Email Input */}
                <div className="space-y-2">
                    <label htmlFor="email" className="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                        Email Address
                    </label>
                    <div className="relative group">
                        <input
                            type="email"
                            id="email"
                            name="email"
                            required
                            placeholder="your@email.com"
                            value={formData.email}
                            onChange={handleInputChange}
                            className="
                                w-full px-6 py-4 text-lg
                                bg-white/70 dark:bg-gray-800/70
                                border-2 border-gray-200 dark:border-gray-600
                                rounded-2xl
                                focus:border-blue-500 focus:ring-4 focus:ring-blue-500/20
                                transition-all duration-300 ease-out
                                placeholder-gray-400 dark:placeholder-gray-500
                                text-gray-900 dark:text-white
                                backdrop-blur-sm
                                group-hover:border-gray-300 dark:group-hover:border-gray-500
                            "
                        />
                        <div className="absolute inset-0 rounded-2xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none"></div>
                    </div>
                </div>

                {/* Frequency Selection */}
                {showFrequency && (
                    <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                            How often would you like to hear from us?
                        </label>
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                            {frequencyOptions.map((option) => (
                                <label
                                    key={option.value}
                                    className={`
                                        relative cursor-pointer group
                                        p-4 rounded-2xl border-2 transition-all duration-300
                                        ${formData.frequency === option.value
                                            ? 'border-blue-500 bg-blue-50/50 dark:bg-blue-900/20 shadow-lg shadow-blue-500/20'
                                            : 'border-gray-200 dark:border-gray-600 bg-white/50 dark:bg-gray-800/50 hover:border-gray-300 dark:hover:border-gray-500'
                                        }
                                    `}
                                >
                                    <input
                                        type="radio"
                                        name="frequency"
                                        value={option.value}
                                        checked={formData.frequency === option.value}
                                        onChange={handleInputChange}
                                        className="sr-only"
                                    />
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <div className="font-semibold text-gray-900 dark:text-white">
                                                {option.label}
                                            </div>
                                            <div className="text-sm text-gray-500 dark:text-gray-400">
                                                {option.description}
                                            </div>
                                        </div>
                                        <div className={`
                                            w-5 h-5 rounded-full border-2 transition-all duration-200
                                            ${formData.frequency === option.value
                                                ? 'border-blue-500 bg-blue-500'
                                                : 'border-gray-300 dark:border-gray-600'
                                            }
                                        `}>
                                            {formData.frequency === option.value && (
                                                <div className="w-full h-full rounded-full bg-white scale-50"></div>
                                            )}
                                        </div>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>
                )}

                {/* Categories */}
                {showCategories && categories.length > 0 && (
                    <div className="space-y-4">
                        <label className="block text-sm font-semibold text-gray-700 dark:text-gray-300">
                            What interests you most?
                        </label>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {categories.map((category) => (
                                <label
                                    key={category}
                                    className={`
                                        relative cursor-pointer group
                                        p-4 rounded-xl border-2 transition-all duration-300
                                        ${formData.categories.includes(category)
                                            ? 'border-green-500 bg-green-50/50 dark:bg-green-900/20 shadow-md shadow-green-500/20'
                                            : 'border-gray-200 dark:border-gray-600 bg-white/50 dark:bg-gray-800/50 hover:border-gray-300 dark:hover:border-gray-500'
                                        }
                                    `}
                                >
                                    <input
                                        type="checkbox"
                                        name="categories"
                                        value={category}
                                        checked={formData.categories.includes(category)}
                                        onChange={handleInputChange}
                                        className="sr-only"
                                    />
                                    <div className="flex items-center justify-between">
                                        <span className="font-medium text-gray-900 dark:text-white">
                                            {category}
                                        </span>
                                        <div className={`
                                            w-5 h-5 rounded border-2 transition-all duration-200 flex items-center justify-center
                                            ${formData.categories.includes(category)
                                                ? 'border-green-500 bg-green-500'
                                                : 'border-gray-300 dark:border-gray-600'
                                            }
                                        `}>
                                            {formData.categories.includes(category) && (
                                                <svg className="w-3 h-3 text-white" fill="currentColor" viewBox="0 0 20 20">
                                                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                                                </svg>
                                            )}
                                        </div>
                                    </div>
                                </label>
                            ))}
                        </div>
                    </div>
                )}

                {/* Submit Button */}
                <button
                    type="submit"
                    disabled={isLoading}
                    className={`
                        w-full py-4 px-8 text-lg font-semibold rounded-2xl
                        bg-gradient-to-r from-blue-600 to-purple-600
                        hover:from-blue-700 hover:to-purple-700
                        text-white shadow-xl shadow-blue-500/25
                        transform transition-all duration-300 ease-out
                        hover:scale-[1.02] hover:shadow-2xl hover:shadow-blue-500/30
                        focus:outline-none focus:ring-4 focus:ring-blue-500/50
                        disabled:opacity-70 disabled:cursor-not-allowed disabled:transform-none
                        relative overflow-hidden group
                    `}
                >
                    <div className="absolute inset-0 bg-gradient-to-r from-white/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
                    <div className="relative flex items-center justify-center gap-3">
                        {isLoading ? (
                            <>
                                <svg className="animate-spin w-5 h-5" fill="none" viewBox="0 0 24 24">
                                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                                <span>Subscribing...</span>
                            </>
                        ) : (
                            <>
                                <span>Subscribe Now</span>
                                <svg className="w-5 h-5 transform group-hover:translate-x-1 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                                </svg>
                            </>
                        )}
                    </div>
                </button>
            </form>

            {/* Footer */}
            <div className="mt-8 pt-6 border-t border-gray-200/50 dark:border-gray-700/50">
                <p className="text-center text-sm text-gray-500 dark:text-gray-400">
                    🔒 We respect your privacy. Unsubscribe at any time.
                </p>
            </div>
        </div>
    );
};

export default NewsletterSubscriptionComponent;