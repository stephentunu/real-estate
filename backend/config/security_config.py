"""
Security configuration utilities for Jaston Real Estate platform.

This module provides security configuration management including CORS,
CSRF protection, authentication, and other security-related settings.
"""

from __future__ import annotations

from typing import Any, Dict, List
from decouple import config


def get_cors_config() -> Dict[str, Any]:
    """
    Get CORS configuration based on environment.
    
    Returns:
        CORS configuration dictionary.
    """
    debug_mode = config('DEBUG', default=True, cast=bool)
    
    if debug_mode:
        return {
            'CORS_ALLOW_ALL_ORIGINS': True,
            'CORS_ALLOW_CREDENTIALS': True,
            'CORS_ALLOWED_ORIGINS': [
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'http://localhost:5173',
                'http://127.0.0.1:5173',
            ],
        }
    
    return {
        'CORS_ALLOW_ALL_ORIGINS': False,
        'CORS_ALLOW_CREDENTIALS': True,
        'CORS_ALLOWED_ORIGINS': config(
            'CORS_ALLOWED_ORIGINS',
            default='',
            cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
        ),
        'CORS_ALLOWED_ORIGIN_REGEXES': config(
            'CORS_ALLOWED_ORIGIN_REGEXES',
            default='',
            cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
        ),
    }


def get_csrf_config() -> Dict[str, Any]:
    """
    Get CSRF configuration based on environment.
    
    Returns:
        CSRF configuration dictionary.
    """
    debug_mode = config('DEBUG', default=True, cast=bool)
    
    base_config = {
        'CSRF_COOKIE_SECURE': config('CSRF_COOKIE_SECURE', default=not debug_mode, cast=bool),
        'CSRF_COOKIE_HTTPONLY': True,
        'CSRF_COOKIE_SAMESITE': 'Lax',
        'CSRF_USE_SESSIONS': False,
        'CSRF_COOKIE_AGE': 31449600,  # 1 year
    }
    
    if debug_mode:
        base_config.update({
            'CSRF_TRUSTED_ORIGINS': [
                'http://localhost:3000',
                'http://127.0.0.1:3000',
                'http://localhost:5173',
                'http://127.0.0.1:5173',
                'http://localhost:8000',
                'http://127.0.0.1:8000',
            ],
        })
    else:
        base_config.update({
            'CSRF_TRUSTED_ORIGINS': config(
                'CSRF_TRUSTED_ORIGINS',
                default='',
                cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
            ),
        })
    
    return base_config


def get_security_headers_config() -> Dict[str, Any]:
    """
    Get security headers configuration.
    
    Returns:
        Security headers configuration dictionary.
    """
    debug_mode = config('DEBUG', default=True, cast=bool)
    
    return {
        'SECURE_BROWSER_XSS_FILTER': True,
        'SECURE_CONTENT_TYPE_NOSNIFF': True,
        'SECURE_HSTS_INCLUDE_SUBDOMAINS': not debug_mode,
        'SECURE_HSTS_PRELOAD': not debug_mode,
        'SECURE_HSTS_SECONDS': 31536000 if not debug_mode else 0,  # 1 year
        'SECURE_REFERRER_POLICY': 'strict-origin-when-cross-origin',
        'SECURE_SSL_REDIRECT': config('SECURE_SSL_REDIRECT', default=not debug_mode, cast=bool),
        'X_FRAME_OPTIONS': 'DENY',
    }


def get_auth_config() -> Dict[str, Any]:
    """
    Get authentication configuration.
    
    Returns:
        Authentication configuration dictionary.
    """
    return {
        'AUTH_USER_MODEL': 'users.User',
        'AUTHENTICATION_BACKENDS': [
            'apps.users.backends.EmailBackend',
            'django.contrib.auth.backends.ModelBackend',
        ],
        'LOGIN_URL': '/admin/login/',
        'LOGIN_REDIRECT_URL': '/admin/',
        'LOGOUT_REDIRECT_URL': '/admin/',
        'PASSWORD_RESET_TIMEOUT': 259200,  # 3 days
    }


def get_allowed_hosts() -> List[str]:
    """
    Get allowed hosts based on environment.
    
    Returns:
        List of allowed hosts.
    """
    debug_mode = config('DEBUG', default=True, cast=bool)
    
    if debug_mode:
        return ['localhost', '127.0.0.1', '0.0.0.0']
    
    return config(
        'ALLOWED_HOSTS',
        default='',
        cast=lambda v: [s.strip() for s in v.split(',') if s.strip()]
    )