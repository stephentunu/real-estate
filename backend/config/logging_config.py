"""
Logging configuration utilities for Jaston Real Estate platform.

This module provides logging configuration management following Django 5.2.6+
best practices with structured logging and proper log levels.
"""

from __future__ import annotations

import os
from typing import Any, Dict
from decouple import config


def get_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration based on environment.
    
    Returns:
        Logging configuration dictionary for Django settings.
    """
    log_level = config('LOG_LEVEL', default='INFO')
    log_dir = config('LOG_DIR', default='logs')
    
    # Ensure log directory exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir, exist_ok=True)
    
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
            'json': {
                'format': '{"level": "%(levelname)s", "time": "%(asctime)s", "module": "%(module)s", "message": "%(message)s"}',
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': log_level,
            },
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'django.log'),
                'maxBytes': 1024 * 1024 * 15,  # 15MB
                'backupCount': 10,
                'formatter': 'verbose',
                'level': log_level,
            },
            'error_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'django_error.log'),
                'maxBytes': 1024 * 1024 * 15,  # 15MB
                'backupCount': 10,
                'formatter': 'verbose',
                'level': 'ERROR',
            },
            'celery_file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': os.path.join(log_dir, 'celery.log'),
                'maxBytes': 1024 * 1024 * 15,  # 15MB
                'backupCount': 10,
                'formatter': 'verbose',
                'level': log_level,
            },
        },
        'root': {
            'handlers': ['console', 'file'],
            'level': log_level,
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file', 'error_file'],
                'level': log_level,
                'propagate': False,
            },
            'django.request': {
                'handlers': ['error_file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'celery': {
                'handlers': ['console', 'celery_file'],
                'level': log_level,
                'propagate': False,
            },
            'apps': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
        },
    }


def get_test_logging_config() -> Dict[str, Any]:
    """
    Get logging configuration for testing.
    
    Returns:
        Test logging configuration dictionary.
    """
    return {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'formatter': 'simple',
                'level': 'WARNING',
            },
        },
        'formatters': {
            'simple': {
                'format': '{levelname} {message}',
                'style': '{',
            },
        },
        'root': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    }