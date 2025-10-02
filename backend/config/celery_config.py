"""
Celery configuration utilities for Jaston Real Estate platform.

This module provides Celery configuration management for background tasks,
periodic tasks, and distributed task processing.
"""

from __future__ import annotations

from typing import Any, Dict
from decouple import config


def get_celery_config() -> Dict[str, Any]:
    """
    Get Celery configuration based on environment.
    
    Returns:
        Celery configuration dictionary.
    """
    redis_url = config('REDIS_URL', default='redis://localhost:6379/0')
    
    return {
        'broker_url': redis_url,
        'result_backend': redis_url,
        'accept_content': ['json'],
        'task_serializer': 'json',
        'result_serializer': 'json',
        'timezone': 'UTC',
        'enable_utc': True,
        'task_track_started': True,
        'task_time_limit': 30 * 60,  # 30 minutes
        'task_soft_time_limit': 25 * 60,  # 25 minutes
        'worker_prefetch_multiplier': 1,
        'worker_max_tasks_per_child': 1000,
        'beat_schedule': {
            'cleanup-soft-deleted-records': {
                'task': 'apps.core.tasks.cleanup_soft_deleted_records',
                'schedule': 86400.0,  # Daily at midnight
            },
            'generate-retention-reports': {
                'task': 'apps.core.tasks.generate_cleanup_report',
                'schedule': 604800.0,  # Weekly
            },
        },
    }


def get_test_celery_config() -> Dict[str, Any]:
    """
    Get Celery configuration for testing.
    
    Returns:
        Test Celery configuration dictionary.
    """
    return {
        'task_always_eager': True,
        'task_eager_propagates': True,
        'broker_url': 'memory://',
        'result_backend': 'cache+memory://',
    }