from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import NewsletterSubscription, NewsletterCampaign, NewsletterDelivery

@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    """
    Admin interface for managing newsletter subscriptions
    """
    list_display = [
        'email', 
        'user_link', 
        'is_active', 
        'is_confirmed', 
        'frequency', 
        'subscribed_at',
        'categories_display'
    ]
    list_filter = [
        'is_active', 
        'is_confirmed', 
        'frequency', 
        'subscribed_at',
        'categories'
    ]
    search_fields = ['email', 'user__username', 'user__email']
    readonly_fields = ['id', 'subscribed_at', 'unsubscribed_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Subscription Info', {
            'fields': ('id', 'email', 'user', 'is_active', 'is_confirmed')
        }),
        ('Preferences', {
            'fields': ('frequency', 'categories')
        }),
        ('Confirmation', {
            'fields': ('confirmation_token',)
        }),
        ('Timestamps', {
            'fields': ('subscribed_at', 'unsubscribed_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    actions = ['activate_subscriptions', 'deactivate_subscriptions', 'confirm_subscriptions']
    
    def user_link(self, obj):
        """Display user as clickable link"""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.username)
        return '-'
    user_link.short_description = 'User'
    
    def categories_display(self, obj):
        """Display categories as comma-separated string"""
        if obj.categories:
            return ', '.join(obj.categories)
        return '-'
    categories_display.short_description = 'Categories'
    
    def activate_subscriptions(self, request, queryset):
        """Bulk activate subscriptions"""
        updated = queryset.update(is_active=True, unsubscribed_at=None)
        self.message_user(request, f'{updated} subscriptions activated.')
    activate_subscriptions.short_description = 'Activate selected subscriptions'
    
    def deactivate_subscriptions(self, request, queryset):
        """Bulk deactivate subscriptions"""
        updated = queryset.update(is_active=False, unsubscribed_at=timezone.now())
        self.message_user(request, f'{updated} subscriptions deactivated.')
    deactivate_subscriptions.short_description = 'Deactivate selected subscriptions'
    
    def confirm_subscriptions(self, request, queryset):
        """Bulk confirm subscriptions"""
        updated = queryset.update(is_confirmed=True, confirmation_token=None)
        self.message_user(request, f'{updated} subscriptions confirmed.')
    confirm_subscriptions.short_description = 'Confirm selected subscriptions'

@admin.register(NewsletterCampaign)
class NewsletterCampaignAdmin(admin.ModelAdmin):
    """
    Admin interface for managing newsletter campaigns
    """
    list_display = [
        'title', 
        'status', 
        'target_frequency', 
        'total_recipients', 
        'total_sent',
        'open_rate',
        'click_rate',
        'scheduled_at',
        'created_by'
    ]
    list_filter = [
        'status', 
        'target_frequency', 
        'scheduled_at', 
        'created_at',
        'created_by'
    ]
    search_fields = ['title', 'subject', 'content']
    readonly_fields = [
        'id', 
        'total_recipients', 
        'total_sent', 
        'total_delivered', 
        'total_opened', 
        'total_clicked',
        'sent_at',
        'created_at', 
        'updated_at'
    ]
    
    fieldsets = (
        ('Campaign Info', {
            'fields': ('id', 'title', 'subject', 'status', 'created_by')
        }),
        ('Content', {
            'fields': ('content', 'html_content')
        }),
        ('Targeting', {
            'fields': ('target_frequency', 'target_categories')
        }),
        ('Scheduling', {
            'fields': ('scheduled_at', 'sent_at')
        }),
        ('Statistics', {
            'fields': (
                'total_recipients', 
                'total_sent', 
                'total_delivered', 
                'total_opened', 
                'total_clicked'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def open_rate(self, obj):
        """Calculate and display open rate"""
        if obj.total_sent > 0:
            rate = (obj.total_opened / obj.total_sent) * 100
            return f'{rate:.1f}%'
        return '0%'
    open_rate.short_description = 'Open Rate'
    
    def click_rate(self, obj):
        """Calculate and display click rate"""
        if obj.total_sent > 0:
            rate = (obj.total_clicked / obj.total_sent) * 100
            return f'{rate:.1f}%'
        return '0%'
    click_rate.short_description = 'Click Rate'
    
    def save_model(self, request, obj, form, change):
        """Set created_by to current user if not set"""
        if not change:  # Only for new objects
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(NewsletterDelivery)
class NewsletterDeliveryAdmin(admin.ModelAdmin):
    """
    Admin interface for managing newsletter deliveries
    """
    list_display = [
        'campaign_title',
        'subscription_email', 
        'status', 
        'sent_at', 
        'delivered_at',
        'opened_at',
        'clicked_at'
    ]
    list_filter = [
        'status', 
        'sent_at', 
        'delivered_at',
        'campaign__status',
        'subscription__is_active'
    ]
    search_fields = [
        'campaign__title', 
        'subscription__email',
        'error_message'
    ]
    readonly_fields = [
        'id', 
        'sent_at', 
        'delivered_at', 
        'opened_at', 
        'clicked_at',
        'created_at', 
        'updated_at'
    ]
    
    fieldsets = (
        ('Delivery Info', {
            'fields': ('id', 'campaign', 'subscription', 'status')
        }),
        ('Tracking', {
            'fields': ('sent_at', 'delivered_at', 'opened_at', 'clicked_at')
        }),
        ('Error Info', {
            'fields': ('error_message',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def campaign_title(self, obj):
        """Display campaign title as clickable link"""
        url = reverse('admin:newsletter_newslettercampaign_change', args=[obj.campaign.pk])
        return format_html('<a href="{}">{}</a>', url, obj.campaign.title)
    campaign_title.short_description = 'Campaign'
    
    def subscription_email(self, obj):
        """Display subscription email as clickable link"""
        url = reverse('admin:newsletter_newslettersubscription_change', args=[obj.subscription.pk])
        return format_html('<a href="{}">{}</a>', url, obj.subscription.email)
    subscription_email.short_description = 'Subscriber'
    
    def has_add_permission(self, request):
        """Disable manual creation of delivery records"""
        return False
