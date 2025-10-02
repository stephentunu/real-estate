"""
Django app configuration for media management.
"""

from __future__ import annotations

from django.apps import AppConfig


class MediaConfig(AppConfig):
    """Configuration for the media app."""
    
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'apps.media'
    verbose_name: str = 'Media Management'
    
    def ready(self) -> None:
        """
        Initialize the app when Django starts.
        
        Import signal handlers and perform any necessary setup.
        """
        # Import signal handlers if any
        # from . import signals  # noqa: F401
        pass