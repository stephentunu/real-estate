"""Celery configuration for jaston project.

This module configures Celery for handling background tasks including:
- Automated soft delete cleanup
- Scheduled maintenance tasks
- Report generation
"""

import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jaston.settings')

app = Celery('jaston')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

# Celery Beat Schedule for periodic tasks
# If a CELERY_CONFIG dict is provided in settings, update app.conf from it.
celery_cfg = getattr(settings, 'CELERY_CONFIG', None)
if isinstance(celery_cfg, dict):
    # map common keys directly; keep Celery's namespace usage too
    app.conf.update(celery_cfg)

# Celery configuration
# Note: avoid duplicating settings here — prefer configuring in `settings.CELERY_CONFIG`.

@app.task(bind=True)
def debug_task(self):
    """Debug task for testing Celery configuration."""
    print(f'Request: {self.request!r}')
    return 'Debug task completed successfully'

# Health check task
@app.task
def health_check():
    """Simple health check task for monitoring."""
    from django.db import connection
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')

        # Use Django timezone for consistent timestamps
        from django.utils import timezone
        return {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'worker_id': None,
        }
    except Exception as e:
        from django.utils import timezone
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': timezone.now().isoformat(),
        }