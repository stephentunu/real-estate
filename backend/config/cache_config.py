"""
Cache configuration utilities for Jaston Real Estate platform.

This module provides cache configuration management for Redis caching,
session storage, and performance optimization.
"""

from __future__ import annotations

from typing import Any, Dict
from decouple import config


def get_cache_config() -> Dict[str, Any]:
    """
    Get cache configuration based on environment.
    
    Returns:
        Cache configuration dictionary for Django settings.
    """
    redis_url = config('REDIS_URL', default='redis://localhost:6379/1')
    cache_timeout = config('CACHE_TIMEOUT', default=300, cast=int)
    
    return {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': redis_url,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 50,
                    'retry_on_timeout': True,
                },
                'SERIALIZER': 'django_redis.serializers.json.JSONSerializer',
                'COMPRESSOR': 'django_redis.compressors.zlib.ZlibCompressor',
            },
            'TIMEOUT': cache_timeout,
            'KEY_PREFIX': 'jaston_re',
            'VERSION': 1,
        },
        'sessions': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': config('REDIS_SESSION_URL', default='redis://localhost:6379/2'),
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
                'CONNECTION_POOL_KWARGS': {
                    'max_connections': 20,
                    'retry_on_timeout': True,
                },
            },
            'TIMEOUT': 86400,  # 24 hours
            'KEY_PREFIX': 'jaston_session',
        },
    }


def get_test_cache_config() -> Dict[str, Any]:
    """
    Get cache configuration for testing.
    
    Returns:
        Test cache configuration dictionary.
    """
    return {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-cache',
            'TIMEOUT': 300,
        },
        'sessions': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'test-session-cache',
            'TIMEOUT': 86400,
        },
    }


def get_session_config() -> Dict[str, Any]:
    """
    Get session configuration for Redis-backed sessions.
    
    Returns:
        Session configuration dictionary.
    """
    return {
        'SESSION_ENGINE': 'django.contrib.sessions.backends.cache',
        'SESSION_CACHE_ALIAS': 'sessions',
        'SESSION_COOKIE_AGE': 86400,  # 24 hours
        'SESSION_COOKIE_SECURE': config('SESSION_COOKIE_SECURE', default=False, cast=bool),
        'SESSION_COOKIE_HTTPONLY': True,
        'SESSION_COOKIE_SAMESITE': 'Lax',
        'SESSION_SAVE_EVERY_REQUEST': True,
    }