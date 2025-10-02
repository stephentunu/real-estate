"""
Deployment configuration utilities for Jaston Real Estate platform.

This module provides deployment configuration management for production,
staging, and development environments with proper security and performance settings.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List
from decouple import config


def get_static_files_config() -> Dict[str, Any]:
    """
    Get static files configuration.
    
    Returns:
        Static files configuration dictionary.
    """
    return {
        'STATIC_URL': '/static/',
        'STATIC_ROOT': config('STATIC_ROOT', default='staticfiles'),
        'STATICFILES_DIRS': [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static'),
        ],
        'STATICFILES_FINDERS': [
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        ],
        'STATICFILES_STORAGE': config(
            'STATICFILES_STORAGE',
            default='django.contrib.staticfiles.storage.StaticFilesStorage'
        ),
    }


def get_media_files_config() -> Dict[str, Any]:
    """
    Get media files configuration.
    
    Returns:
        Media files configuration dictionary.
    """
    return {
        'MEDIA_URL': '/media/',
        'MEDIA_ROOT': config('MEDIA_ROOT', default='media'),
        'FILE_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
        'DATA_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
        'FILE_UPLOAD_PERMISSIONS': 0o644,
        'FILE_UPLOAD_DIRECTORY_PERMISSIONS': 0o755,
    }


def get_email_config() -> Dict[str, Any]:
    """
    Get email configuration based on environment.
    
    Returns:
        Email configuration dictionary.
    """
    email_backend = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
    
    base_config = {
        'EMAIL_BACKEND': email_backend,
        'DEFAULT_FROM_EMAIL': config('DEFAULT_FROM_EMAIL', default='noreply@jastonrealestate.com'),
        'SERVER_EMAIL': config('SERVER_EMAIL', default='server@jastonrealestate.com'),
        'EMAIL_TIMEOUT': 60,
    }
    
    if email_backend == 'django.core.mail.backends.smtp.EmailBackend':
        base_config.update({
            'EMAIL_HOST': config('EMAIL_HOST'),
            'EMAIL_PORT': config('EMAIL_PORT', default=587, cast=int),
            'EMAIL_HOST_USER': config('EMAIL_HOST_USER'),
            'EMAIL_HOST_PASSWORD': config('EMAIL_HOST_PASSWORD'),
            'EMAIL_USE_TLS': config('EMAIL_USE_TLS', default=True, cast=bool),
            'EMAIL_USE_SSL': config('EMAIL_USE_SSL', default=False, cast=bool),
        })
    
    return base_config


def get_internationalization_config() -> Dict[str, Any]:
    """
    Get internationalization configuration.
    
    Returns:
        Internationalization configuration dictionary.
    """
    return {
        'LANGUAGE_CODE': config('LANGUAGE_CODE', default='en-us'),
        'TIME_ZONE': config('TIME_ZONE', default='UTC'),
        'USE_I18N': True,
        'USE_TZ': True,
        'LANGUAGES': [
            ('en', 'English'),
            ('es', 'Spanish'),
            ('fr', 'French'),
        ],
        'LOCALE_PATHS': [
            os.path.join(os.path.dirname(os.path.dirname(__file__)), 'locale'),
        ],
    }


def get_performance_config() -> Dict[str, Any]:
    """
    Get performance optimization configuration.
    
    Returns:
        Performance configuration dictionary.
    """
    return {
        'DATA_UPLOAD_MAX_NUMBER_FIELDS': 1000,
        'DATA_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
        'FILE_UPLOAD_MAX_MEMORY_SIZE': 5242880,  # 5MB
        'DEFAULT_AUTO_FIELD': 'django.db.models.BigAutoField',
        'USE_THOUSAND_SEPARATOR': True,
        'NUMBER_GROUPING': 3,
    }


def get_admin_config() -> Dict[str, Any]:
    """
    Get Django admin configuration.
    
    Returns:
        Admin configuration dictionary.
    """
    return {
        'ADMIN_URL': config('ADMIN_URL', default='admin/'),
        'ADMINS': [
            ('Douglas Mutethia', 'douglas@elesosolutions.com'),
        ],
        'MANAGERS': [
            ('Support Team', 'support@ifinsta.com'),
        ],
    }


def get_environment_specific_config(environment: str = None) -> Dict[str, Any]:
    """
    Get environment-specific configuration.
    
    Args:
        environment: The environment name (development, staging, production).
        
    Returns:
        Environment-specific configuration dictionary.
    """
    if environment is None:
        environment = config('ENVIRONMENT', default='development')
    
    if environment == 'production':
        return {
            'DEBUG': False,
            'TEMPLATE_DEBUG': False,
            'SECURE_SSL_REDIRECT': True,
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,
            'SECURE_HSTS_SECONDS': 31536000,  # 1 year
            'SECURE_HSTS_INCLUDE_SUBDOMAINS': True,
            'SECURE_HSTS_PRELOAD': True,
        }
    
    elif environment == 'staging':
        return {
            'DEBUG': False,
            'TEMPLATE_DEBUG': False,
            'SECURE_SSL_REDIRECT': True,
            'SESSION_COOKIE_SECURE': True,
            'CSRF_COOKIE_SECURE': True,
        }
    
    else:  # development
        return {
            'DEBUG': True,
            'TEMPLATE_DEBUG': True,
            'SECURE_SSL_REDIRECT': False,
            'SESSION_COOKIE_SECURE': False,
            'CSRF_COOKIE_SECURE': False,
        }