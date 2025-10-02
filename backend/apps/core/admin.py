from django.contrib import admin
from django.contrib.admin import AdminSite
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count
from django.contrib.auth.models import Group
from django.conf import settings
from django.apps import apps
from apps.core.mixins import SoftDeleteMixin
from datetime import timedelta
from django.utils import timezone
import json


class JastonAdminSite(AdminSite):
    """
    Custom Django Admin Site for Jaston
    """
    site_header = 'Jaston Administration'
    site_title = 'Jaston Admin'
    index_title = 'Welcome to Jaston Administration'
    site_url = '/'
    
    def index(self, request, extra_context=None):
        """
        Custom admin index with dashboard statistics
        """
        extra_context = extra_context or {}
        
        # Import models here to avoid circular imports
        from users.models import User
        from properties.models import Property
        from messaging.models import Conversation, Message
        from notifications.models import Notification
        
        # Dashboard statistics
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'total_properties': Property.objects.count(),
            'published_properties': Property.objects.filter(status__name='Available').count(),
            'total_conversations': Conversation.objects.count(),
            'active_conversations': Conversation.objects.filter(is_active=True).count(),
            'total_messages': Message.objects.count(),
            'unread_notifications': Notification.objects.filter(is_read=False).count(),
        }
        
        # Recent activity
        recent_users = User.objects.order_by('-date_joined')[:5]
        recent_properties = Property.objects.order_by('-created_at')[:5]
        recent_messages = Message.objects.select_related('sender', 'conversation').order_by('-created_at')[:5]
        
        extra_context.update({
            'stats': stats,
            'recent_users': recent_users,
            'recent_properties': recent_properties,
            'recent_messages': recent_messages,
        })
        
        return super().index(request, extra_context)


# Create custom admin site instance
admin_site = JastonAdminSite(name='jaston_admin')


# Unregister default Group model if not needed
try:
    admin.site.unregister(Group)
except admin.sites.NotRegistered:
    pass


class BaseModelAdmin(admin.ModelAdmin):
    """
    Base admin class with common functionality
    """
    save_on_top = True
    list_per_page = 25
    
    def get_readonly_fields(self, request, obj=None):
        """
        Make timestamp fields readonly by default
        """
        readonly_fields = list(super().get_readonly_fields(request, obj))
        timestamp_fields = ['created_at', 'updated_at', 'date_joined', 'last_login']
        
        for field in timestamp_fields:
            if hasattr(self.model, field) and field not in readonly_fields:
                readonly_fields.append(field)
                
        return readonly_fields
    
    def get_list_display(self, request):
        """
        Add common fields to list display
        """
        list_display = list(super().get_list_display(request))
        
        # Add created_at if model has it and it's not already in list_display
        if hasattr(self.model, 'created_at') and 'created_at' not in list_display:
            list_display.append('created_at')
            
        return list_display


class TimestampedModelAdmin(BaseModelAdmin):
    """
    Admin class for models with timestamp fields
    """
    readonly_fields = ('created_at', 'updated_at')
    
    def get_fieldsets(self, request, obj=None):
        """
        Add timestamp fieldset if not already defined
        """
        fieldsets = super().get_fieldsets(request, obj)
        
        # Check if timestamps fieldset already exists
        has_timestamps = any(
            'Timestamps' in fieldset[0] or 'timestamps' in fieldset[0].lower()
            for fieldset in fieldsets
        )
        
        if not has_timestamps and hasattr(self.model, 'created_at'):
            fieldsets = list(fieldsets) + [
                ('Timestamps', {
                    'fields': ('created_at', 'updated_at'),
                    'classes': ('collapse',)
                })
            ]
            
        return fieldsets