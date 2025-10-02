"""
Django admin configuration for media models.
"""

from __future__ import annotations

from django.contrib import admin
from .models import File


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    """Admin configuration for File model."""
    
    list_display = [
        'name',
        'file_type',
        'file_size',
        'is_public',
        'created_at',
        'created_by',
    ]
    
    list_filter = [
        'file_type',
        'is_public',
        'created_at',
    ]
    
    search_fields = [
        'name',
        'description',
    ]
    
    readonly_fields = [
        'id',
        'file_size',
        'mime_type',
        'created_at',
        'updated_at',
        'created_by',
        'updated_by',
    ]
    
    fieldsets = [
        ('File Information', {
            'fields': [
                'name',
                'file',
                'file_type',
                'description',
                'is_public',
            ]
        }),
        ('Metadata', {
            'fields': [
                'file_size',
                'mime_type',
            ],
            'classes': ['collapse'],
        }),
        ('Audit Trail', {
            'fields': [
                'id',
                'created_at',
                'updated_at',
                'created_by',
                'updated_by',
            ],
            'classes': ['collapse'],
        }),
    ]