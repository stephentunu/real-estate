"""
Django app configuration for core functionality.
"""

from __future__ import annotations

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Configuration for the core app."""
    
    default_auto_field: str = 'django.db.models.BigAutoField'
    name: str = 'apps.core'
    verbose_name: str = 'Core Functionality'
    
    def ready(self) -> None:
        """
        Initialize the app when Django starts.
        
        Import signal handlers and perform any necessary setup.
        """
        # Import signal handlers if any
        # from . import signals  # noqa: F401
        pass