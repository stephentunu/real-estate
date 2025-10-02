"""
Admin configuration utilities for Jaston Real Estate platform.

This module provides Django admin interface configuration management
including customization, security, and performance settings.
"""

from __future__ import annotations

from typing import Any, Dict, List
from decouple import config


def get_admin_config() -> Dict[str, Any]:
    """
    Get Django admin configuration based on environment.
    
    Returns:
        Admin configuration dictionary for Django settings.
    """
    debug_mode = config('DEBUG', default=True, cast=bool)
    
    base_config = {
        # Admin site customization
        'ADMIN_SITE_HEADER': config('ADMIN_SITE_HEADER', default='Jaston Real Estate Administration'),
        'ADMIN_SITE_TITLE': config('ADMIN_SITE_TITLE', default='Jaston RE Admin'),
        'ADMIN_INDEX_TITLE': config('ADMIN_INDEX_TITLE', default='Welcome to Jaston Real Estate Administration'),
        
        # Admin URL configuration
        'ADMIN_URL': config('ADMIN_URL', default='admin/'),
        
        # Admin security settings
        'ADMIN_FORCE_ALLAUTH': config('ADMIN_FORCE_ALLAUTH', default=False, cast=bool),
        'ADMIN_REORDER': config('ADMIN_REORDER', default=True, cast=bool),
        
        # Admin pagination
        'ADMIN_LIST_PER_PAGE': config('ADMIN_LIST_PER_PAGE', default=25, cast=int),
        'ADMIN_LIST_MAX_SHOW_ALL': config('ADMIN_LIST_MAX_SHOW_ALL', default=200, cast=int),
        
        # Admin and manager configuration
        'ADMINS': [
            ('Admin', config('ADMIN_EMAIL', default='admin@jaston-re.com')),
        ],
        'MANAGERS': [
            ('Manager', config('MANAGER_EMAIL', default='manager@jaston-re.com')),
        ],
    }
    
    if not debug_mode:
        # Production admin security
        base_config.update({
            'ADMIN_URL': config('ADMIN_URL', default='secure-admin-panel/'),
            'ADMIN_FORCE_ALLAUTH': True,
        })
    
    return base_config


def get_admin_interface_config() -> Dict[str, Any]:
    """
    Get admin interface customization configuration.
    
    Returns:
        Admin interface configuration dictionary.
    """
    return {
        'ADMIN_INTERFACE': {
            'SHOW_THEMES': config('ADMIN_SHOW_THEMES', default=True, cast=bool),
            'SHOW_BOOKMARKS': config('ADMIN_SHOW_BOOKMARKS', default=True, cast=bool),
            'SHOW_RECENT_ACTIONS': config('ADMIN_SHOW_RECENT_ACTIONS', default=True, cast=bool),
            'CONFIRM_UNSAVED_CHANGES': config('ADMIN_CONFIRM_UNSAVED_CHANGES', default=True, cast=bool),
            'USE_GRAVATAR': config('ADMIN_USE_GRAVATAR', default=False, cast=bool),
        }
    }


def get_admin_permissions_config() -> Dict[str, Any]:
    """
    Get admin permissions and security configuration.
    
    Returns:
        Admin permissions configuration dictionary.
    """
    return {
        'ADMIN_AUTO_CREATE_SUPERUSER': config('ADMIN_AUTO_CREATE_SUPERUSER', default=False, cast=bool),
        'ADMIN_SUPERUSER_USERNAME': config('ADMIN_SUPERUSER_USERNAME', default='admin'),
        'ADMIN_SUPERUSER_EMAIL': config('ADMIN_SUPERUSER_EMAIL', default='admin@jaston-re.com'),
        'ADMIN_LOGIN_REDIRECT_URL': config('ADMIN_LOGIN_REDIRECT_URL', default='/admin/'),
        'ADMIN_LOGOUT_REDIRECT_URL': config('ADMIN_LOGOUT_REDIRECT_URL', default='/'),
    }


def get_admin_apps_order() -> List[str]:
    """
    Get the order of apps in Django admin.
    
    Returns:
        List of app names in the desired order for admin interface.
    """
    return [
        'users',
        'properties',
        'leases',
        'maintenance',
        'appointments',
        'messaging',
        'notifications',
        'blog',
        'newsletter',
        'team',
        'cities',
        'media',
        'core',
    ]