from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import NotificationType, Notification, NotificationPreference


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    """
    Admin for NotificationType
    """
    list_display = ('name', 'description', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_types', 'deactivate_types']
    
    def activate_types(self, request, queryset):
        """
        Activate selected notification types
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} notification types activated.')
    activate_types.short_description = "Activate selected notification types"
    
    def deactivate_types(self, request, queryset):
        """
        Deactivate selected notification types
        """
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} notification types deactivated.')
    deactivate_types.short_description = "Deactivate selected notification types"


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """
    Comprehensive Notification admin
    """
    list_display = (
        'get_notification_preview', 'recipient', 'notification_type',
        'priority', 'is_read', 'email_sent', 'push_sent', 'created_at'
    )
    
    list_filter = (
        'notification_type', 'priority', 'is_read',
        'email_sent', 'push_sent', 'created_at', 'read_at'
    )
    
    search_fields = (
        'title', 'message', 'recipient__email',
        'recipient__first_name', 'recipient__last_name'
    )
    
    readonly_fields = (
        'created_at', 'updated_at', 'read_at',
        'email_sent_at', 'push_sent_at'
    )
    
    fieldsets = (
        ('Notification Content', {
            'fields': ('recipient', 'notification_type', 'title', 'message')
        }),
        ('Priority & Status', {
            'fields': ('priority', 'is_read', 'delivery_status')
        }),
        ('Additional Data', {
            'fields': ('data',),
            'classes': ('collapse',)
        }),
        ('Email/Push Tracking', {
            'fields': ('email_sent', 'email_sent_at', 'push_sent', 'push_sent_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'read_at', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_read', 'mark_as_unread', 'mark_email_sent',
        'mark_push_sent', 'reset_delivery_status'
    ]
    
    def get_notification_preview(self, obj):
        """
        Display notification preview with status indicators
        """
        read_indicator = '📖' if obj.is_read else '📩'
        priority_indicator = {
            'low': '🔵',
            'medium': '🟡',
            'high': '🔴',
            'urgent': '🚨'
        }.get(obj.priority, '')
        
        email_indicator = '📧' if obj.email_sent else ''
        push_indicator = '📱' if obj.push_sent else ''
        
        preview = obj.title[:30]
        if len(obj.title) > 30:
            preview += '...'
            
        return format_html(
            '{} {} {} {} {}',
            preview, read_indicator, priority_indicator, email_indicator, push_indicator
        )
    get_notification_preview.short_description = 'Notification'
    
    def mark_as_read(self, request, queryset):
        """
        Mark selected notifications as read
        """
        updated = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                updated += 1
        self.message_user(request, f'{updated} notifications marked as read.')
    mark_as_read.short_description = "Mark selected notifications as read"
    
    def mark_as_unread(self, request, queryset):
        """
        Mark selected notifications as unread
        """
        updated = queryset.filter(is_read=True).update(is_read=False, read_at=None)
        self.message_user(request, f'{updated} notifications marked as unread.')
    mark_as_unread.short_description = "Mark selected notifications as unread"
    
    def mark_email_sent(self, request, queryset):
        """
        Mark selected notifications as email sent
        """
        from django.utils import timezone
        updated = queryset.update(email_sent=True, email_sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as email sent.')
    mark_email_sent.short_description = "Mark selected notifications as email sent"
    
    def mark_push_sent(self, request, queryset):
        """
        Mark selected notifications as push sent
        """
        from django.utils import timezone
        updated = queryset.update(push_sent=True, push_sent_at=timezone.now())
        self.message_user(request, f'{updated} notifications marked as push sent.')
    mark_push_sent.short_description = "Mark selected notifications as push sent"
    
    def reset_delivery_status(self, request, queryset):
        """
        Reset delivery status for resending
        """
        updated = queryset.update(
            email_sent=False,
            email_sent_at=None,
            push_sent=False,
            push_sent_at=None
        )
        self.message_user(request, f'{updated} notifications reset for resending.')
    reset_delivery_status.short_description = "Reset delivery status for resending"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('recipient', 'notification_type')


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """
    Admin for NotificationPreference
    """
    list_display = (
        'user', 'notification_type', 'email_enabled',
        'push_enabled', 'in_app_enabled', 'frequency'
    )
    
    list_filter = (
        'notification_type', 'email_enabled', 'push_enabled',
        'in_app_enabled', 'frequency'
    )
    
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'notification_type__name'
    )
    
    fieldsets = (
        ('User & Type', {
            'fields': ('user', 'notification_type')
        }),
        ('Delivery Preferences', {
            'fields': (
                'email_enabled', 'push_enabled', 'in_app_enabled', 'frequency'
            )
        }),
        ('Quiet Hours', {
            'fields': ('quiet_hours_start', 'quiet_hours_end'),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'enable_all_channels', 'disable_all_channels',
        'enable_email_only', 'enable_push_only', 'set_immediate_frequency'
    ]
    
    def enable_all_channels(self, request, queryset):
        """
        Enable all notification channels
        """
        updated = queryset.update(
            email_enabled=True,
            push_enabled=True,
            in_app_enabled=True
        )
        self.message_user(request, f'{updated} preferences updated to enable all channels.')
    enable_all_channels.short_description = "Enable all notification channels"
    
    def disable_all_channels(self, request, queryset):
        """
        Disable all notification channels
        """
        updated = queryset.update(
            email_enabled=False,
            push_enabled=False,
            in_app_enabled=False
        )
        self.message_user(request, f'{updated} preferences updated to disable all channels.')
    disable_all_channels.short_description = "Disable all notification channels"
    
    def enable_email_only(self, request, queryset):
        """
        Enable email notifications only
        """
        updated = queryset.update(
            email_enabled=True,
            push_enabled=False,
            in_app_enabled=False
        )
        self.message_user(request, f'{updated} preferences updated to email only.')
    enable_email_only.short_description = "Enable email notifications only"
    
    def enable_push_only(self, request, queryset):
        """
        Enable push notifications only
        """
        updated = queryset.update(
            email_enabled=False,
            push_enabled=True,
            in_app_enabled=False
        )
        self.message_user(request, f'{updated} preferences updated to push only.')
    enable_push_only.short_description = "Enable push notifications only"
    
    def set_immediate_frequency(self, request, queryset):
        """
        Set frequency to immediate for selected preferences
        """
        updated = queryset.update(frequency='immediate')
        self.message_user(request, f'{updated} preferences set to immediate frequency.')
    set_immediate_frequency.short_description = "Set frequency to immediate"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'notification_type')
