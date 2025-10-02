/**
 * Newsletter Service
 * Handles all newsletter-related API calls to Django backend
 */

const API_BASE_URL = 'http://localhost:8000/api/v1/newsletter';

/**
 * Get authentication headers for API requests
 * @returns {Object} Headers object with authorization
 */
function getAuthHeaders() {
    const token = localStorage.getItem('authToken');
    return {
        'Content-Type': 'application/json',
        ...(token && { 'Authorization': `Token ${token}` })
    };
}

/**
 * Newsletter Subscription Interface
 */
export const NewsletterSubscription = {
    /**
     * Subscribe to newsletter (public endpoint)
     * @param {Object} subscriptionData - Subscription data
     * @param {string} subscriptionData.email - Email address
     * @param {string} subscriptionData.frequency - Subscription frequency (daily, weekly, monthly)
     * @param {Array} subscriptionData.categories - Array of category strings
     * @returns {Promise<Object>} Subscription response
     */
    async subscribe(subscriptionData) {
        try {
            const response = await fetch(`${API_BASE_URL}/subscribe/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(subscriptionData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to subscribe to newsletter');
            }
            
            return data;
        } catch (error) {
            console.error('Newsletter subscription error:', error);
            throw error;
        }
    },

    /**
     * Unsubscribe from newsletter (public endpoint)
     * @param {Object} unsubscribeData - Unsubscribe data
     * @param {string} unsubscribeData.email - Email address
     * @param {string} unsubscribeData.token - Optional unsubscribe token
     * @returns {Promise<Object>} Unsubscribe response
     */
    async unsubscribe(unsubscribeData) {
        try {
            const response = await fetch(`${API_BASE_URL}/unsubscribe/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(unsubscribeData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to unsubscribe from newsletter');
            }
            
            return data;
        } catch (error) {
            console.error('Newsletter unsubscribe error:', error);
            throw error;
        }
    },

    /**
     * Confirm newsletter subscription (public endpoint)
     * @param {string} token - Confirmation token
     * @returns {Promise<Object>} Confirmation response
     */
    async confirm(token) {
        try {
            const response = await fetch(`${API_BASE_URL}/confirm/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token })
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to confirm subscription');
            }
            
            return data;
        } catch (error) {
            console.error('Newsletter confirmation error:', error);
            throw error;
        }
    },

    /**
     * Get user's newsletter subscriptions (authenticated)
     * @param {Object} params - Query parameters
     * @returns {Promise<Array>} Array of subscriptions
     */
    async getUserSubscriptions(params = {}) {
        try {
            const queryParams = new URLSearchParams({
                user_only: 'true',
                ...params
            });
            
            const response = await fetch(`${API_BASE_URL}/subscriptions/?${queryParams}`, {
                method: 'GET',
                headers: getAuthHeaders()
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to fetch subscriptions');
            }
            
            return data.results || data;
        } catch (error) {
            console.error('Get user subscriptions error:', error);
            throw error;
        }
    },

    /**
     * Update newsletter subscription (authenticated)
     * @param {string} subscriptionId - Subscription ID
     * @param {Object} updateData - Update data
     * @returns {Promise<Object>} Updated subscription
     */
    async updateSubscription(subscriptionId, updateData) {
        try {
            const response = await fetch(`${API_BASE_URL}/subscriptions/${subscriptionId}/`, {
                method: 'PATCH',
                headers: getAuthHeaders(),
                body: JSON.stringify(updateData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to update subscription');
            }
            
            return data;
        } catch (error) {
            console.error('Update subscription error:', error);
            throw error;
        }
    }
};

/**
 * Newsletter Campaign Interface (Admin)
 */
export const NewsletterCampaign = {
    /**
     * Get all newsletter campaigns (authenticated)
     * @param {Object} params - Query parameters
     * @returns {Promise<Array>} Array of campaigns
     */
    async getAll(params = {}) {
        try {
            const queryParams = new URLSearchParams(params);
            
            const response = await fetch(`${API_BASE_URL}/campaigns/?${queryParams}`, {
                method: 'GET',
                headers: getAuthHeaders()
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to fetch campaigns');
            }
            
            return data.results || data;
        } catch (error) {
            console.error('Get campaigns error:', error);
            throw error;
        }
    },

    /**
     * Get single newsletter campaign (authenticated)
     * @param {string} campaignId - Campaign ID
     * @returns {Promise<Object>} Campaign data
     */
    async getById(campaignId) {
        try {
            const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/`, {
                method: 'GET',
                headers: getAuthHeaders()
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to fetch campaign');
            }
            
            return data;
        } catch (error) {
            console.error('Get campaign error:', error);
            throw error;
        }
    },

    /**
     * Create newsletter campaign (authenticated)
     * @param {Object} campaignData - Campaign data
     * @returns {Promise<Object>} Created campaign
     */
    async create(campaignData) {
        try {
            const response = await fetch(`${API_BASE_URL}/campaigns/`, {
                method: 'POST',
                headers: getAuthHeaders(),
                body: JSON.stringify(campaignData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to create campaign');
            }
            
            return data;
        } catch (error) {
            console.error('Create campaign error:', error);
            throw error;
        }
    },

    /**
     * Update newsletter campaign (authenticated)
     * @param {string} campaignId - Campaign ID
     * @param {Object} updateData - Update data
     * @returns {Promise<Object>} Updated campaign
     */
    async update(campaignId, updateData) {
        try {
            const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/`, {
                method: 'PATCH',
                headers: getAuthHeaders(),
                body: JSON.stringify(updateData)
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to update campaign');
            }
            
            return data;
        } catch (error) {
            console.error('Update campaign error:', error);
            throw error;
        }
    },

    /**
     * Delete newsletter campaign (authenticated)
     * @param {string} campaignId - Campaign ID
     * @returns {Promise<void>}
     */
    async delete(campaignId) {
        try {
            const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/`, {
                method: 'DELETE',
                headers: getAuthHeaders()
            });
            
            if (!response.ok) {
                const data = await response.json();
                throw new Error(data.message || 'Failed to delete campaign');
            }
        } catch (error) {
            console.error('Delete campaign error:', error);
            throw error;
        }
    },

    /**
     * Send newsletter campaign (authenticated, admin only)
     * @param {string} campaignId - Campaign ID
     * @returns {Promise<Object>} Send response
     */
    async send(campaignId) {
        try {
            const response = await fetch(`${API_BASE_URL}/campaigns/${campaignId}/send/`, {
                method: 'POST',
                headers: getAuthHeaders()
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to send campaign');
            }
            
            return data;
        } catch (error) {
            console.error('Send campaign error:', error);
            throw error;
        }
    }
};

/**
 * Newsletter Utilities
 */
export const NewsletterUtils = {
    /**
     * Get available newsletter categories
     * @returns {Promise<Array>} Array of category strings
     */
    async getCategories() {
        try {
            const response = await fetch(`${API_BASE_URL}/categories/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to fetch categories');
            }
            
            return data.categories || [];
        } catch (error) {
            console.error('Get categories error:', error);
            throw error;
        }
    },

    /**
     * Get newsletter statistics (authenticated, admin only)
     * @returns {Promise<Object>} Statistics data
     */
    async getStats() {
        try {
            const response = await fetch(`${API_BASE_URL}/stats/`, {
                method: 'GET',
                headers: getAuthHeaders()
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to fetch statistics');
            }
            
            return data;
        } catch (error) {
            console.error('Get stats error:', error);
            throw error;
        }
    },

    /**
     * Get newsletter deliveries (authenticated)
     * @param {Object} params - Query parameters
     * @returns {Promise<Array>} Array of deliveries
     */
    async getDeliveries(params = {}) {
        try {
            const queryParams = new URLSearchParams(params);
            
            const response = await fetch(`${API_BASE_URL}/deliveries/?${queryParams}`, {
                method: 'GET',
                headers: getAuthHeaders()
            });
            
            const data = await response.json();
            
            if (!response.ok) {
                throw new Error(data.message || 'Failed to fetch deliveries');
            }
            
            return data.results || data;
        } catch (error) {
            console.error('Get deliveries error:', error);
            throw error;
        }
    }
};

/**
 * Default export with all newsletter services
 */
export default {
    NewsletterSubscription,
    NewsletterCampaign,
    NewsletterUtils
};