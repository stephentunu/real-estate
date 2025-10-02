/**
 * Newsletter Admin Component
 * Handles newsletter campaign management and statistics for admin users
 */

import { NewsletterCampaign, NewsletterUtils } from '../services/newsletterService.js';

export class NewsletterAdminComponent {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        this.options = {
            theme: 'light',
            ...options
        };
        this.campaigns = [];
        this.stats = null;
        this.categories = [];
        this.isLoading = false;
        this.currentView = 'dashboard'; // dashboard, campaigns, create-campaign
        
        this.init();
    }

    async init() {
        await this.loadInitialData();
        this.render();
        this.attachEventListeners();
    }

    async loadInitialData() {
        try {
            const [stats, campaigns, categories] = await Promise.all([
                NewsletterUtils.getStats(),
                NewsletterCampaign.getAll(),
                NewsletterUtils.getCategories()
            ]);
            
            this.stats = stats;
            this.campaigns = campaigns;
            this.categories = categories;
        } catch (error) {
            console.error('Failed to load initial data:', error);
        }
    }

    render() {
        this.container.innerHTML = `
            <div class="newsletter-admin ${this.options.theme}">
                <div class="admin-header">
                    <h2>Newsletter Administration</h2>
                    <div class="admin-nav">
                        <button class="nav-btn ${this.currentView === 'dashboard' ? 'active' : ''}" data-view="dashboard">
                            Dashboard
                        </button>
                        <button class="nav-btn ${this.currentView === 'campaigns' ? 'active' : ''}" data-view="campaigns">
                            Campaigns
                        </button>
                        <button class="nav-btn ${this.currentView === 'create-campaign' ? 'active' : ''}" data-view="create-campaign">
                            Create Campaign
                        </button>
                    </div>
                </div>

                <div class="admin-content">
                    ${this.renderCurrentView()}
                </div>

                <div class="admin-message" id="admin-message" style="display: none;"></div>
            </div>
        `;

        this.addStyles();
    }

    renderCurrentView() {
        switch (this.currentView) {
            case 'dashboard':
                return this.renderDashboard();
            case 'campaigns':
                return this.renderCampaigns();
            case 'create-campaign':
                return this.renderCreateCampaign();
            default:
                return this.renderDashboard();
        }
    }

    renderDashboard() {
        if (!this.stats) {
            return '<div class="loading">Loading statistics...</div>';
        }

        return `
            <div class="dashboard">
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-icon">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"></path>
                                <rect x="8" y="2" width="8" height="4" rx="1" ry="1"></rect>
                            </svg>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${this.stats.total_subscriptions || 0}</div>
                            <div class="stat-label">Total Subscriptions</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon active">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M22 6c0-1.1-.9-2-2-2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6zm-2 0l-8 5-8-5h16zm0 12H4V8l8 5 8-5v10z"/>
                            </svg>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${this.stats.active_subscriptions || 0}</div>
                            <div class="stat-label">Active Subscriptions</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon campaigns">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
                            </svg>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${this.stats.total_campaigns || 0}</div>
                            <div class="stat-label">Total Campaigns</div>
                        </div>
                    </div>

                    <div class="stat-card">
                        <div class="stat-icon success">
                            <svg viewBox="0 0 24 24" fill="currentColor">
                                <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                            </svg>
                        </div>
                        <div class="stat-content">
                            <div class="stat-value">${this.stats.confirmed_subscriptions || 0}</div>
                            <div class="stat-label">Confirmed Subscriptions</div>
                        </div>
                    </div>
                </div>

                <div class="dashboard-charts">
                    <div class="chart-card">
                        <h3>Subscription Frequency Breakdown</h3>
                        <div class="frequency-chart">
                            ${this.renderFrequencyChart()}
                        </div>
                    </div>

                    <div class="chart-card">
                        <h3>Recent Activity</h3>
                        <div class="activity-list">
                            ${this.renderRecentActivity()}
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    renderFrequencyChart() {
        if (!this.stats.frequency_breakdown) {
            return '<div class="no-data">No frequency data available</div>';
        }

        const total = Object.values(this.stats.frequency_breakdown).reduce((sum, count) => sum + count, 0);
        
        return Object.entries(this.stats.frequency_breakdown).map(([frequency, count]) => {
            const percentage = total > 0 ? (count / total * 100).toFixed(1) : 0;
            return `
                <div class="frequency-item">
                    <div class="frequency-label">${frequency.charAt(0).toUpperCase() + frequency.slice(1)}</div>
                    <div class="frequency-bar">
                        <div class="frequency-fill" style="width: ${percentage}%"></div>
                    </div>
                    <div class="frequency-value">${count} (${percentage}%)</div>
                </div>
            `;
        }).join('');
    }

    renderRecentActivity() {
        if (!this.stats.recent_activity || this.stats.recent_activity.length === 0) {
            return '<div class="no-data">No recent activity</div>';
        }

        return this.stats.recent_activity.map(activity => `
            <div class="activity-item">
                <div class="activity-icon">
                    <svg viewBox="0 0 24 24" fill="currentColor">
                        <circle cx="12" cy="12" r="3"/>
                    </svg>
                </div>
                <div class="activity-content">
                    <div class="activity-text">${activity.description}</div>
                    <div class="activity-time">${new Date(activity.timestamp).toLocaleDateString()}</div>
                </div>
            </div>
        `).join('');
    }

    renderCampaigns() {
        return `
            <div class="campaigns-view">
                <div class="campaigns-header">
                    <h3>Newsletter Campaigns</h3>
                    <button class="btn btn-primary" id="refresh-campaigns">
                        Refresh
                    </button>
                </div>

                <div class="campaigns-list">
                    ${this.campaigns.length === 0 ? 
                        '<div class="no-data">No campaigns found</div>' : 
                        this.campaigns.map(campaign => this.renderCampaignCard(campaign)).join('')
                    }
                </div>
            </div>
        `;
    }

    renderCampaignCard(campaign) {
        const statusClass = campaign.status.toLowerCase();
        const createdDate = new Date(campaign.created_at).toLocaleDateString();
        
        return `
            <div class="campaign-card" data-campaign-id="${campaign.id}">
                <div class="campaign-header">
                    <h4>${campaign.title}</h4>
                    <span class="campaign-status ${statusClass}">${campaign.status}</span>
                </div>
                
                <div class="campaign-details">
                    <p><strong>Subject:</strong> ${campaign.subject}</p>
                    <p><strong>Created:</strong> ${createdDate}</p>
                    <p><strong>Categories:</strong> ${campaign.target_categories.join(', ')}</p>
                    <p><strong>Frequency:</strong> ${campaign.target_frequency}</p>
                </div>

                <div class="campaign-actions">
                    <button class="btn btn-sm btn-secondary" onclick="newsletterAdmin.editCampaign('${campaign.id}')">
                        Edit
                    </button>
                    ${campaign.status === 'draft' ? `
                        <button class="btn btn-sm btn-primary" onclick="newsletterAdmin.sendCampaign('${campaign.id}')">
                            Send
                        </button>
                    ` : ''}
                    <button class="btn btn-sm btn-danger" onclick="newsletterAdmin.deleteCampaign('${campaign.id}')">
                        Delete
                    </button>
                </div>
            </div>
        `;
    }

    renderCreateCampaign() {
        return `
            <div class="create-campaign">
                <h3>Create New Campaign</h3>
                
                <form class="campaign-form" id="campaign-form">
                    <div class="form-group">
                        <label for="campaign-title">Campaign Title *</label>
                        <input type="text" id="campaign-title" name="title" required>
                    </div>

                    <div class="form-group">
                        <label for="campaign-subject">Email Subject *</label>
                        <input type="text" id="campaign-subject" name="subject" required>
                    </div>

                    <div class="form-group">
                        <label for="campaign-content">Email Content *</label>
                        <textarea id="campaign-content" name="content" rows="10" required placeholder="Enter your email content here..."></textarea>
                    </div>

                    <div class="form-row">
                        <div class="form-group">
                            <label>Target Categories</label>
                            <div class="checkbox-group">
                                ${this.categories.map(category => `
                                    <label class="checkbox-option">
                                        <input type="checkbox" name="target_categories" value="${category}" checked>
                                        <span class="checkbox-custom"></span>
                                        ${category}
                                    </label>
                                `).join('')}
                            </div>
                        </div>

                        <div class="form-group">
                            <label for="target-frequency">Target Frequency</label>
                            <select id="target-frequency" name="target_frequency">
                                <option value="all">All Frequencies</option>
                                <option value="daily">Daily Only</option>
                                <option value="weekly">Weekly Only</option>
                                <option value="monthly">Monthly Only</option>
                            </select>
                        </div>
                    </div>

                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="newsletterAdmin.switchView('campaigns')">
                            Cancel
                        </button>
                        <button type="submit" class="btn btn-primary" id="create-campaign-btn">
                            <span class="btn-text">Create Campaign</span>
                            <div class="loading-spinner" style="display: none;">
                                <svg class="spinner" viewBox="0 0 24 24">
                                    <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2" fill="none" stroke-dasharray="31.416" stroke-dashoffset="31.416">
                                        <animate attributeName="stroke-dasharray" dur="2s" values="0 31.416;15.708 15.708;0 31.416" repeatCount="indefinite"/>
                                        <animate attributeName="stroke-dashoffset" dur="2s" values="0;-15.708;-31.416" repeatCount="indefinite"/>
                                    </circle>
                                </svg>
                            </div>
                        </button>
                    </div>
                </form>
            </div>
        `;
    }

    attachEventListeners() {
        // Navigation
        this.container.addEventListener('click', (e) => {
            if (e.target.classList.contains('nav-btn')) {
                this.switchView(e.target.dataset.view);
            }
        });

        // Campaign form
        const campaignForm = this.container.querySelector('#campaign-form');
        if (campaignForm) {
            campaignForm.addEventListener('submit', this.handleCreateCampaign.bind(this));
        }

        // Refresh campaigns
        const refreshBtn = this.container.querySelector('#refresh-campaigns');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', this.refreshCampaigns.bind(this));
        }

        // Make methods available globally for onclick handlers
        window.newsletterAdmin = this;
    }

    switchView(view) {
        this.currentView = view;
        this.render();
        this.attachEventListeners();
    }

    async handleCreateCampaign(event) {
        event.preventDefault();
        
        if (this.isLoading) return;
        
        const formData = new FormData(event.target);
        const campaignData = {
            title: formData.get('title'),
            subject: formData.get('subject'),
            content: formData.get('content'),
            target_categories: formData.getAll('target_categories'),
            target_frequency: formData.get('target_frequency')
        };

        this.setLoading(true);

        try {
            const newCampaign = await NewsletterCampaign.create(campaignData);
            this.campaigns.unshift(newCampaign);
            this.showSuccess('Campaign created successfully!');
            this.switchView('campaigns');
        } catch (error) {
            this.showError(error.message || 'Failed to create campaign.');
        } finally {
            this.setLoading(false);
        }
    }

    async refreshCampaigns() {
        try {
            this.campaigns = await NewsletterCampaign.getAll();
            this.render();
            this.attachEventListeners();
        } catch (error) {
            this.showError('Failed to refresh campaigns.');
        }
    }

    async sendCampaign(campaignId) {
        if (!confirm('Are you sure you want to send this campaign?')) return;
        
        try {
            await NewsletterCampaign.send(campaignId);
            this.showSuccess('Campaign sent successfully!');
            await this.refreshCampaigns();
        } catch (error) {
            this.showError(error.message || 'Failed to send campaign.');
        }
    }

    async deleteCampaign(campaignId) {
        if (!confirm('Are you sure you want to delete this campaign?')) return;
        
        try {
            await NewsletterCampaign.delete(campaignId);
            this.campaigns = this.campaigns.filter(c => c.id !== campaignId);
            this.showSuccess('Campaign deleted successfully!');
            this.render();
            this.attachEventListeners();
        } catch (error) {
            this.showError(error.message || 'Failed to delete campaign.');
        }
    }

    editCampaign(campaignId) {
        // TODO: Implement edit functionality
        this.showError('Edit functionality coming soon!');
    }

    setLoading(loading) {
        this.isLoading = loading;
        const btn = this.container.querySelector('#create-campaign-btn');
        if (!btn) return;
        
        const btnText = btn.querySelector('.btn-text');
        const spinner = btn.querySelector('.loading-spinner');
        
        if (loading) {
            btn.disabled = true;
            btnText.style.display = 'none';
            spinner.style.display = 'block';
        } else {
            btn.disabled = false;
            btnText.style.display = 'block';
            spinner.style.display = 'none';
        }
    }

    showError(message) {
        const messageElement = this.container.querySelector('#admin-message');
        messageElement.textContent = message;
        messageElement.className = 'admin-message error-message';
        messageElement.style.display = 'block';
        
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 5000);
    }

    showSuccess(message) {
        const messageElement = this.container.querySelector('#admin-message');
        messageElement.textContent = message;
        messageElement.className = 'admin-message success-message';
        messageElement.style.display = 'block';
        
        setTimeout(() => {
            messageElement.style.display = 'none';
        }, 5000);
    }

    addStyles() {
        if (document.querySelector('#newsletter-admin-styles')) return;

        const styles = document.createElement('style');
        styles.id = 'newsletter-admin-styles';
        styles.textContent = `
            .newsletter-admin {
                max-width: 1200px;
                margin: 0 auto;
                padding: 2rem;
            }

            .admin-header {
                margin-bottom: 2rem;
                border-bottom: 1px solid var(--color-gray-200);
                padding-bottom: 1rem;
            }

            .admin-header h2 {
                margin: 0 0 1rem 0;
                color: var(--color-gray-900);
                font-size: 2rem;
                font-weight: 600;
            }

            .admin-nav {
                display: flex;
                gap: 1rem;
            }

            .nav-btn {
                padding: 0.5rem 1rem;
                border: 1px solid var(--color-gray-300);
                background: var(--color-white);
                color: var(--color-gray-700);
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.2s;
            }

            .nav-btn:hover {
                background: var(--color-gray-50);
            }

            .nav-btn.active {
                background: var(--color-primary);
                color: white;
                border-color: var(--color-primary);
            }

            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 1.5rem;
                margin-bottom: 2rem;
            }

            .stat-card {
                background: var(--color-white);
                border: 1px solid var(--color-gray-200);
                border-radius: 8px;
                padding: 1.5rem;
                display: flex;
                align-items: center;
                gap: 1rem;
            }

            .stat-icon {
                width: 48px;
                height: 48px;
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                background: var(--color-gray-100);
                color: var(--color-gray-600);
            }

            .stat-icon.active {
                background: var(--color-blue-100);
                color: var(--color-blue-600);
            }

            .stat-icon.campaigns {
                background: var(--color-purple-100);
                color: var(--color-purple-600);
            }

            .stat-icon.success {
                background: var(--color-green-100);
                color: var(--color-green-600);
            }

            .stat-icon svg {
                width: 24px;
                height: 24px;
            }

            .stat-value {
                font-size: 2rem;
                font-weight: 700;
                color: var(--color-gray-900);
                line-height: 1;
            }

            .stat-label {
                font-size: 0.875rem;
                color: var(--color-gray-600);
                margin-top: 0.25rem;
            }

            .dashboard-charts {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 2rem;
            }

            .chart-card {
                background: var(--color-white);
                border: 1px solid var(--color-gray-200);
                border-radius: 8px;
                padding: 1.5rem;
            }

            .chart-card h3 {
                margin: 0 0 1rem 0;
                color: var(--color-gray-900);
                font-size: 1.25rem;
            }

            .frequency-item {
                display: flex;
                align-items: center;
                gap: 1rem;
                margin-bottom: 1rem;
            }

            .frequency-label {
                min-width: 80px;
                font-size: 0.875rem;
                color: var(--color-gray-700);
            }

            .frequency-bar {
                flex: 1;
                height: 8px;
                background: var(--color-gray-200);
                border-radius: 4px;
                overflow: hidden;
            }

            .frequency-fill {
                height: 100%;
                background: var(--color-primary);
                transition: width 0.3s;
            }

            .frequency-value {
                min-width: 80px;
                font-size: 0.875rem;
                color: var(--color-gray-600);
                text-align: right;
            }

            .activity-item {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.75rem 0;
                border-bottom: 1px solid var(--color-gray-100);
            }

            .activity-item:last-child {
                border-bottom: none;
            }

            .activity-icon {
                width: 32px;
                height: 32px;
                border-radius: 50%;
                background: var(--color-gray-100);
                display: flex;
                align-items: center;
                justify-content: center;
                color: var(--color-gray-600);
            }

            .activity-icon svg {
                width: 16px;
                height: 16px;
            }

            .activity-text {
                font-size: 0.875rem;
                color: var(--color-gray-900);
            }

            .activity-time {
                font-size: 0.75rem;
                color: var(--color-gray-500);
            }

            .campaigns-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1.5rem;
            }

            .campaigns-header h3 {
                margin: 0;
                color: var(--color-gray-900);
                font-size: 1.5rem;
            }

            .campaign-card {
                background: var(--color-white);
                border: 1px solid var(--color-gray-200);
                border-radius: 8px;
                padding: 1.5rem;
                margin-bottom: 1rem;
            }

            .campaign-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 1rem;
            }

            .campaign-header h4 {
                margin: 0;
                color: var(--color-gray-900);
                font-size: 1.25rem;
            }

            .campaign-status {
                padding: 0.25rem 0.75rem;
                border-radius: 12px;
                font-size: 0.75rem;
                font-weight: 500;
                text-transform: uppercase;
            }

            .campaign-status.draft {
                background: var(--color-gray-100);
                color: var(--color-gray-700);
            }

            .campaign-status.sent {
                background: var(--color-green-100);
                color: var(--color-green-700);
            }

            .campaign-status.sending {
                background: var(--color-blue-100);
                color: var(--color-blue-700);
            }

            .campaign-details p {
                margin: 0.5rem 0;
                font-size: 0.875rem;
                color: var(--color-gray-600);
            }

            .campaign-actions {
                display: flex;
                gap: 0.5rem;
                margin-top: 1rem;
            }

            .btn {
                padding: 0.5rem 1rem;
                border: none;
                border-radius: 6px;
                font-size: 0.875rem;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s;
                display: inline-flex;
                align-items: center;
                gap: 0.5rem;
            }

            .btn-sm {
                padding: 0.375rem 0.75rem;
                font-size: 0.75rem;
            }

            .btn-primary {
                background: var(--color-primary);
                color: white;
            }

            .btn-primary:hover:not(:disabled) {
                background: var(--color-primary-dark);
            }

            .btn-secondary {
                background: var(--color-gray-100);
                color: var(--color-gray-700);
            }

            .btn-secondary:hover {
                background: var(--color-gray-200);
            }

            .btn-danger {
                background: var(--color-red-600);
                color: white;
            }

            .btn-danger:hover {
                background: var(--color-red-700);
            }

            .btn:disabled {
                opacity: 0.6;
                cursor: not-allowed;
            }

            .create-campaign {
                max-width: 800px;
            }

            .create-campaign h3 {
                margin: 0 0 2rem 0;
                color: var(--color-gray-900);
                font-size: 1.5rem;
            }

            .campaign-form .form-group {
                margin-bottom: 1.5rem;
            }

            .campaign-form label {
                display: block;
                margin-bottom: 0.5rem;
                color: var(--color-gray-700);
                font-weight: 500;
                font-size: 0.875rem;
            }

            .campaign-form input,
            .campaign-form textarea,
            .campaign-form select {
                width: 100%;
                padding: 0.75rem;
                border: 1px solid var(--color-gray-300);
                border-radius: 6px;
                font-size: 1rem;
                transition: border-color 0.2s, box-shadow 0.2s;
            }

            .campaign-form input:focus,
            .campaign-form textarea:focus,
            .campaign-form select:focus {
                outline: none;
                border-color: var(--color-primary);
                box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
            }

            .campaign-form textarea {
                resize: vertical;
                min-height: 200px;
            }

            .form-row {
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 1.5rem;
            }

            .checkbox-group {
                display: flex;
                flex-direction: column;
                gap: 0.75rem;
            }

            .checkbox-option {
                display: flex;
                align-items: center;
                gap: 0.5rem;
                cursor: pointer;
                font-size: 0.875rem;
                color: var(--color-gray-700);
            }

            .checkbox-option input {
                display: none;
            }

            .checkbox-custom {
                width: 18px;
                height: 18px;
                border: 2px solid var(--color-gray-300);
                border-radius: 3px;
                transition: all 0.2s;
                position: relative;
            }

            .checkbox-option input:checked + .checkbox-custom {
                border-color: var(--color-primary);
                background: var(--color-primary);
            }

            .checkbox-option input:checked + .checkbox-custom::after {
                content: '✓';
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                color: white;
                font-size: 12px;
                font-weight: bold;
            }

            .form-actions {
                display: flex;
                gap: 1rem;
                margin-top: 2rem;
            }

            .loading-spinner {
                width: 20px;
                height: 20px;
            }

            .spinner {
                width: 100%;
                height: 100%;
                color: currentColor;
            }

            .admin-message {
                padding: 1rem;
                border-radius: 6px;
                margin-top: 1rem;
                font-size: 0.875rem;
            }

            .admin-message.error-message {
                background: var(--color-red-50);
                color: var(--color-red-700);
                border: 1px solid var(--color-red-200);
            }

            .admin-message.success-message {
                background: var(--color-green-50);
                color: var(--color-green-700);
                border: 1px solid var(--color-green-200);
            }

            .no-data {
                text-align: center;
                color: var(--color-gray-500);
                font-style: italic;
                padding: 2rem;
            }

            .loading {
                text-align: center;
                color: var(--color-gray-500);
                padding: 2rem;
            }

            @media (max-width: 768px) {
                .dashboard-charts {
                    grid-template-columns: 1fr;
                }

                .form-row {
                    grid-template-columns: 1fr;
                }

                .stats-grid {
                    grid-template-columns: 1fr;
                }
            }
        `;
        
        document.head.appendChild(styles);
    }
}

export default NewsletterAdminComponent;