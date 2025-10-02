"""
Performance configuration utilities for Jaston Real Estate platform.

This module provides performance-related configuration management including
database connection pooling, caching strategies, and optimization settings.
"""

from __future__ import annotations

from typing import Any, Dict
from decouple import config


def get_performance_config() -> Dict[str, Any]:
    """
    Get performance configuration based on environment.
    
    Returns:
        Performance configuration dictionary for Django settings.
    """
    debug_mode = config('DEBUG', default=True, cast=bool)
    
    base_config = {
        # Database connection settings
        'CONN_MAX_AGE': config('CONN_MAX_AGE', default=60, cast=int),
        'CONN_HEALTH_CHECKS': config('CONN_HEALTH_CHECKS', default=True, cast=bool),
        
        # Request/Response settings
        'DATA_UPLOAD_MAX_MEMORY_SIZE': config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int),  # 5MB
        'FILE_UPLOAD_MAX_MEMORY_SIZE': config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int),  # 5MB
        'DATA_UPLOAD_MAX_NUMBER_FIELDS': config('DATA_UPLOAD_MAX_NUMBER_FIELDS', default=1000, cast=int),
        
        # Session settings
        'SESSION_COOKIE_AGE': config('SESSION_COOKIE_AGE', default=1209600, cast=int),  # 2 weeks
        'SESSION_SAVE_EVERY_REQUEST': config('SESSION_SAVE_EVERY_REQUEST', default=False, cast=bool),
        'SESSION_EXPIRE_AT_BROWSER_CLOSE': config('SESSION_EXPIRE_AT_BROWSER_CLOSE', default=False, cast=bool),
        
        # Cache settings
        'CACHE_MIDDLEWARE_SECONDS': config('CACHE_MIDDLEWARE_SECONDS', default=600, cast=int),  # 10 minutes
        'CACHE_MIDDLEWARE_KEY_PREFIX': config('CACHE_MIDDLEWARE_KEY_PREFIX', default='jaston_re'),
    }
    
    if not debug_mode:
        # Production performance optimizations
        base_config.update({
            'CONN_MAX_AGE': config('CONN_MAX_AGE', default=300, cast=int),  # 5 minutes in production
            'SESSION_COOKIE_SECURE': True,
            'SESSION_COOKIE_HTTPONLY': True,
            'SESSION_COOKIE_SAMESITE': 'Lax',
            'CSRF_COOKIE_SECURE': True,
            'CSRF_COOKIE_HTTPONLY': True,
            'CSRF_COOKIE_SAMESITE': 'Lax',
        })
    
    return base_config


def get_middleware_performance_config() -> Dict[str, Any]:
    """
    Get middleware performance configuration.
    
    Returns:
        Middleware performance configuration dictionary.
    """
    return {
        'CACHE_MIDDLEWARE_ALIAS': 'default',
        'CACHE_MIDDLEWARE_SECONDS': config('CACHE_MIDDLEWARE_SECONDS', default=600, cast=int),
        'CACHE_MIDDLEWARE_KEY_PREFIX': config('CACHE_MIDDLEWARE_KEY_PREFIX', default='jaston_re'),
    }


def get_database_performance_config() -> Dict[str, Any]:
    """
    Get database performance configuration.
    
    Returns:
        Database performance configuration dictionary.
    """
    return {
        'ATOMIC_REQUESTS': config('ATOMIC_REQUESTS', default=True, cast=bool),
        'AUTOCOMMIT': config('AUTOCOMMIT', default=True, cast=bool),
        'CONN_MAX_AGE': config('CONN_MAX_AGE', default=60, cast=int),
        'CONN_HEALTH_CHECKS': config('CONN_HEALTH_CHECKS', default=True, cast=bool),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
            'charset': 'utf8mb4',
        } if config('DATABASE_ENGINE', default='sqlite3') == 'mysql' else {},
    }