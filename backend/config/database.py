"""Database configuration for Jaston Real Estate platform.

This module provides database configuration for different environments
(development, staging, production) with proper connection settings and
error handling using the centralized environment loader."""

from __future__ import annotations

from typing import Any, Dict
from .environment import get_env_loader, DatabaseConfig


def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration based on environment variables.
    
    Returns:
        Database configuration dictionary for Django settings.
        
    Raises:
        ValueError: If DB_ENGINE is not supported.
    """
    env_loader = get_env_loader()
    db_config = env_loader.get_database_config()
    
    if db_config.engine == 'django.db.backends.sqlite3':
        return {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': db_config.name,
                'OPTIONS': {
                    'timeout': 20,
                    'check_same_thread': False,
                },
            }
        }
    
    elif db_config.engine == 'django.db.backends.postgresql':
        config_dict = {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': db_config.name,
            'USER': db_config.user,
            'PASSWORD': db_config.password,
            'HOST': db_config.host or 'localhost',
            'PORT': db_config.port or 5432,
            'OPTIONS': {
                'connect_timeout': 60,
            },
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        }
        
        return {'default': config_dict}
    
    else:
        raise ValueError(f"Unsupported database engine: {db_config.engine}")


def get_test_database_config() -> Dict[str, Any]:
    """
    Get test database configuration.
    
    Returns:
        Test database configuration dictionary.
    """
    return {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:',
            'OPTIONS': {
                'timeout': 20,
                'check_same_thread': False,
            },
        }
    }