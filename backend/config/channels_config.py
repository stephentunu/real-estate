"""
Django Channels configuration utilities for Jaston Real Estate platform.

This module provides Channels configuration management for WebSocket
connections, real-time messaging, and asynchronous features.
"""

from __future__ import annotations

from typing import Any, Dict
from decouple import config


def get_channels_config() -> Dict[str, Any]:
    """
    Get Django Channels configuration.
    
    Returns:
        Channels configuration dictionary.
    """
    redis_url = config('REDIS_URL', default='redis://localhost:6379/3')
    
    return {
        'CHANNEL_LAYERS': {
            'default': {
                'BACKEND': 'channels_redis.core.RedisChannelLayer',
                'CONFIG': {
                    'hosts': [redis_url],
                    'capacity': 1500,
                    'expiry': 60,
                    'group_expiry': 86400,  # 24 hours
                    'symmetric_encryption_keys': [
                        config('CHANNELS_ENCRYPTION_KEY', default='test-key-change-in-production')
                    ],
                },
            },
        },
        'ASGI_APPLICATION': 'jaston.asgi.application',
    }


def get_test_channels_config() -> Dict[str, Any]:
    """
    Get Channels configuration for testing.
    
    Returns:
        Test Channels configuration dictionary.
    """
    return {
        'CHANNEL_LAYERS': {
            'default': {
                'BACKEND': 'channels.layers.InMemoryChannelLayer',
            },
        },
        'ASGI_APPLICATION': 'jaston.asgi.application',
    }


def get_websocket_config() -> Dict[str, Any]:
    """
    Get WebSocket-specific configuration.
    
    Returns:
        WebSocket configuration dictionary.
    """
    return {
        'WEBSOCKET_ACCEPT_ALL': config('WEBSOCKET_ACCEPT_ALL', default=True, cast=bool),
        'WEBSOCKET_TIMEOUT': config('WEBSOCKET_TIMEOUT', default=300, cast=int),  # 5 minutes
        'WEBSOCKET_HEARTBEAT_INTERVAL': config('WEBSOCKET_HEARTBEAT_INTERVAL', default=30, cast=int),
        'WEBSOCKET_MAX_CONNECTIONS_PER_USER': config('WEBSOCKET_MAX_CONNECTIONS_PER_USER', default=5, cast=int),
    }