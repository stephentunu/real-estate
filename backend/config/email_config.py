"""
Email configuration utilities for Jaston Real Estate platform.

This module provides email configuration management for Django settings,
including SMTP, console backend, and email templates configuration.
"""

from __future__ import annotations

from typing import Any, Dict
from decouple import config


def get_email_config() -> Dict[str, Any]:
    """
    Get email configuration based on environment.
    
    Returns:
        Email configuration dictionary for Django settings.
    """
    debug_mode = config('DEBUG', default=True, cast=bool)
    
    if debug_mode:
        # Development email configuration - use console backend
        return {
            'EMAIL_BACKEND': 'django.core.mail.backends.console.EmailBackend',
            'DEFAULT_FROM_EMAIL': config('DEFAULT_FROM_EMAIL', default='noreply@jaston-re.local'),
            'SERVER_EMAIL': config('SERVER_EMAIL', default='server@jaston-re.local'),
        }
    
    # Production email configuration - use SMTP
    return {
        'EMAIL_BACKEND': 'django.core.mail.backends.smtp.EmailBackend',
        'EMAIL_HOST': config('EMAIL_HOST', default='localhost'),
        'EMAIL_PORT': config('EMAIL_PORT', default=587, cast=int),
        'EMAIL_USE_TLS': config('EMAIL_USE_TLS', default=True, cast=bool),
        'EMAIL_USE_SSL': config('EMAIL_USE_SSL', default=False, cast=bool),
        'EMAIL_HOST_USER': config('EMAIL_HOST_USER', default=''),
        'EMAIL_HOST_PASSWORD': config('EMAIL_HOST_PASSWORD', default=''),
        'DEFAULT_FROM_EMAIL': config('DEFAULT_FROM_EMAIL', default='noreply@jaston-re.com'),
        'SERVER_EMAIL': config('SERVER_EMAIL', default='server@jaston-re.com'),
        'EMAIL_TIMEOUT': config('EMAIL_TIMEOUT', default=60, cast=int),
    }


def get_email_templates_config() -> Dict[str, Any]:
    """
    Get email templates configuration.
    
    Returns:
        Email templates configuration dictionary.
    """
    return {
        'EMAIL_SUBJECT_PREFIX': config('EMAIL_SUBJECT_PREFIX', default='[Jaston RE] '),
        'ADMINS': [
            ('Admin', config('ADMIN_EMAIL', default='admin@jaston-re.com')),
        ],
        'MANAGERS': [
            ('Manager', config('MANAGER_EMAIL', default='manager@jaston-re.com')),
        ],
    }


def get_test_email_config() -> Dict[str, Any]:
    """
    Get email configuration for testing.
    
    Returns:
        Test email configuration dictionary.
    """
    return {
        'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
        'DEFAULT_FROM_EMAIL': 'test@jaston-re.local',
        'SERVER_EMAIL': 'test-server@jaston-re.local',
    }