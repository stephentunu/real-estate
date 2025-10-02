from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count
from .models import Appointment, AppointmentType, AppointmentReminder


@admin.register(AppointmentType)
class AppointmentTypeAdmin(admin.ModelAdmin):
    """
    Admin configuration for AppointmentType model
    """
    
    list_display = [
        'name', 'duration_minutes', 'color_display', 'is_active',
        'requires_property', 'appointment_count', 'created_at'
    ]
    list_filter = ['is_active', 'requires_property', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = [
        'created_at', 'updated_at',
        'appointment_count', 'active_appointment_count'
    ]
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'duration_minutes', 'color')
        }),
        ('Settings', {
            'fields': ('is_active', 'requires_property')
        }),
        ('Statistics', {
            'fields': ('appointment_count', 'active_appointment_count'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Add annotations for counts"""
        queryset = super().get_queryset(request)
        return queryset.annotate(
            appointment_count=Count('appointments'),
            active_appointment_count=Count(
                'appointments',
                filter=admin.models.Q(appointments__status__in=['pending', 'confirmed'])
            )
        )
    
    def color_display(self, obj):
        """Display color as a colored box"""
        if obj.color:
            return format_html(
                '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc; display: inline-block;"></div> {}',
                obj.color,
                obj.color
            )
        return '-'
    color_display.short_description = 'Color'
    
    def appointment_count(self, obj):
        """Display total appointment count"""
        return getattr(obj, 'appointment_count', 0)
    appointment_count.short_description = 'Total Appointments'
    appointment_count.admin_order_field = 'appointment_count'
    
    def active_appointment_count(self, obj):
        """Display active appointment count"""
        return getattr(obj, 'active_appointment_count', 0)
    active_appointment_count.short_description = 'Active Appointments'
    active_appointment_count.admin_order_field = 'active_appointment_count'
    

    
    actions = ['make_active', 'make_inactive']
    
    def make_active(self, request, queryset):
        """Mark selected appointment types as active"""
        updated = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{updated} appointment type(s) marked as active.'
        )
    make_active.short_description = 'Mark selected appointment types as active'
    
    def make_inactive(self, request, queryset):
        """Mark selected appointment types as inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{updated} appointment type(s) marked as inactive.'
        )
    make_inactive.short_description = 'Mark selected appointment types as inactive'


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Appointment model
    """
    
    list_display = [
        'title', 'client', 'agent', 'appointment_type', 'scheduled_datetime_display',
        'status_display', 'priority_display', 'is_past', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'appointment_type', 'scheduled_date',
        'created_at', 'visibility_level'
    ]
    search_fields = [
        'title', 'description', 'client__username', 'client__email',
        'agent__username', 'agent__email'
    ]
    readonly_fields = [
        'scheduled_datetime', 'end_datetime', 'is_past', 'is_today',
        'is_upcoming', 'can_be_cancelled', 'can_be_rescheduled',
        'created_at', 'updated_at',
        'cancelled_at', 'cancelled_by', 'reminder_sent_at'
    ]
    ordering = ['-scheduled_date', '-scheduled_time']
    date_hierarchy = 'scheduled_date'
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'title', 'description', 'appointment_type', 'client', 'agent'
            )
        }),
        ('Scheduling', {
            'fields': (
                'scheduled_date', 'scheduled_time', 'duration_minutes',
                'timezone', 'scheduled_datetime', 'end_datetime'
            )
        }),
        ('Property & Location', {
            'fields': ('property', 'meeting_location', 'meeting_link')
        }),
        ('Contact Information', {
            'fields': ('client_phone', 'client_email')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'status_display', 'priority_display')
        }),
        ('Notes', {
            'fields': ('agent_notes', 'client_notes', 'completion_notes')
        }),
        ('Cancellation', {
            'fields': (
                'cancelled_at', 'cancelled_by', 'cancellation_reason'
            ),
            'classes': ('collapse',)
        }),
        ('Rescheduling', {
            'fields': ('original_appointment', 'reschedule_count'),
            'classes': ('collapse',)
        }),
        ('Reminders', {
            'fields': ('reminder_sent', 'reminder_sent_at'),
            'classes': ('collapse',)
        }),
        ('Status Checks', {
            'fields': (
                'is_past', 'is_today', 'is_upcoming',
                'can_be_cancelled', 'can_be_rescheduled'
            ),
            'classes': ('collapse',)
        }),
        ('Visibility', {
            'fields': ('visibility_level', 'is_deleted')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Include related objects"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'appointment_type', 'client', 'agent', 'cancelled_by'
        )
    
    def scheduled_datetime_display(self, obj):
        """Display formatted scheduled datetime"""
        if obj.scheduled_date and obj.scheduled_time:
            return obj.scheduled_datetime.strftime('%Y-%m-%d %H:%M')
        return '-'
    scheduled_datetime_display.short_description = 'Scheduled'
    scheduled_datetime_display.admin_order_field = 'scheduled_date'
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'pending': '#fbbf24',  # yellow
            'confirmed': '#3b82f6',  # blue
            'in_progress': '#10b981',  # green
            'completed': '#059669',  # dark green
            'cancelled': '#ef4444',  # red
            'no_show': '#6b7280',  # gray
        }
        color = colors.get(obj.status, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    status_display.admin_order_field = 'status'
    
    def priority_display(self, obj):
        """Display priority with color coding"""
        colors = {
            'low': '#10b981',  # green
            'medium': '#fbbf24',  # yellow
            'high': '#f59e0b',  # orange
            'urgent': '#ef4444',  # red
        }
        color = colors.get(obj.priority, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_display.short_description = 'Priority'
    priority_display.admin_order_field = 'priority'
    
    def is_past(self, obj):
        """Check if appointment is in the past"""
        return obj.is_past
    is_past.boolean = True
    is_past.short_description = 'Past'
    

    
    actions = [
        'mark_confirmed', 'mark_completed', 'mark_cancelled',
        'send_reminders', 'make_public', 'make_private'
    ]
    
    def mark_confirmed(self, request, queryset):
        """Mark selected appointments as confirmed"""
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(
            request,
            f'{updated} appointment(s) marked as confirmed.'
        )
    mark_confirmed.short_description = 'Mark selected appointments as confirmed'
    
    def mark_completed(self, request, queryset):
        """Mark selected appointments as completed"""
        updated = queryset.filter(
            status__in=['confirmed', 'in_progress']
        ).update(status='completed')
        self.message_user(
            request,
            f'{updated} appointment(s) marked as completed.'
        )
    mark_completed.short_description = 'Mark selected appointments as completed'
    
    def mark_cancelled(self, request, queryset):
        """Mark selected appointments as cancelled"""
        updated = queryset.exclude(
            status__in=['completed', 'cancelled']
        ).update(
            status='cancelled',
            cancelled_at=timezone.now(),
            cancelled_by=request.user,
            cancellation_reason='Cancelled by admin'
        )
        self.message_user(
            request,
            f'{updated} appointment(s) marked as cancelled.'
        )
    mark_cancelled.short_description = 'Mark selected appointments as cancelled'
    
    def send_reminders(self, request, queryset):
        """Send reminders for selected appointments"""
        count = 0
        for appointment in queryset.filter(
            status__in=['pending', 'confirmed'],
            reminder_sent=False
        ):
            # Here you would implement the actual reminder sending logic
            # For now, just mark as reminder sent
            appointment.reminder_sent = True
            appointment.reminder_sent_at = timezone.now()
            appointment.save()
            count += 1
        
        self.message_user(
            request,
            f'Reminders sent for {count} appointment(s).'
        )
    send_reminders.short_description = 'Send reminders for selected appointments'
    
    def make_public(self, request, queryset):
        """Make selected appointments public"""
        updated = queryset.update(visibility_level='public')
        self.message_user(
            request,
            f'{updated} appointment(s) made public.'
        )
    make_public.short_description = 'Make selected appointments public'
    
    def make_private(self, request, queryset):
        """Make selected appointments private"""
        updated = queryset.update(visibility_level='private')
        self.message_user(
            request,
            f'{updated} appointment(s) made private.'
        )
    make_private.short_description = 'Make selected appointments private'


@admin.register(AppointmentReminder)
class AppointmentReminderAdmin(admin.ModelAdmin):
    """
    Admin configuration for AppointmentReminder model
    """
    
    list_display = [
        'appointment', 'reminder_type', 'scheduled_for',
        'is_sent', 'sent_at', 'created_at'
    ]
    list_filter = [
        'reminder_type', 'is_sent', 'scheduled_for', 'created_at'
    ]
    search_fields = [
        'appointment__title', 'subject', 'message',
        'appointment__client__username', 'appointment__agent__username'
    ]
    readonly_fields = [
        'sent_at', 'created_at', 'updated_at'
    ]
    ordering = ['-scheduled_for']
    date_hierarchy = 'scheduled_for'
    
    fieldsets = (
        ('Reminder Information', {
            'fields': ('appointment', 'reminder_type', 'scheduled_for')
        }),
        ('Content', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('is_sent', 'sent_at')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        """Include related objects"""
        queryset = super().get_queryset(request)
        return queryset.select_related('appointment', 'appointment__client', 'appointment__agent')
    

    
    actions = ['mark_as_sent', 'mark_as_pending']
    
    def mark_as_sent(self, request, queryset):
        """Mark selected reminders as sent"""
        updated = queryset.filter(is_sent=False).update(
            is_sent=True,
            sent_at=timezone.now()
        )
        self.message_user(
            request,
            f'{updated} reminder(s) marked as sent.'
        )
    mark_as_sent.short_description = 'Mark selected reminders as sent'
    
    def mark_as_pending(self, request, queryset):
        """Mark selected reminders as pending"""
        updated = queryset.filter(is_sent=True).update(
            is_sent=False,
            sent_at=None
        )
        self.message_user(
            request,
            f'{updated} reminder(s) marked as pending.'
        )
    mark_as_pending.short_description = 'Mark selected reminders as pending'


# Custom admin site configuration
admin.site.site_header = 'Jaston - Appointments Administration'
admin.site.site_title = 'Appointments Admin'
admin.site.index_title = 'Appointments Management'
