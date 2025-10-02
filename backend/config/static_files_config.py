"""
Static files configuration utilities for Jaston Real Estate platform.

This module provides static files and media files configuration management
for Django settings, including development and production configurations.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List
from decouple import config


def get_static_files_config() -> Dict[str, Any]:
    """
    Get static files configuration based on environment.
    
    Returns:
        Static files configuration dictionary for Django settings.
    """
    debug_mode = config('DEBUG', default=True, cast=bool)
    base_dir = config('BASE_DIR', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    static_config = {
        'STATIC_URL': '/static/',
        'STATIC_ROOT': config('STATIC_ROOT', default=os.path.join(base_dir, 'staticfiles')),
        'STATICFILES_DIRS': [
            os.path.join(base_dir, 'static'),
        ],
        'STATICFILES_FINDERS': [
            'django.contrib.staticfiles.finders.FileSystemFinder',
            'django.contrib.staticfiles.finders.AppDirectoriesFinder',
        ],
    }
    
    if not debug_mode:
        # Production static files configuration
        static_config.update({
            'STATICFILES_STORAGE': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
        })
    
    return static_config


def get_media_files_config() -> Dict[str, Any]:
    """
    Get media files configuration based on environment.
    
    Returns:
        Media files configuration dictionary for Django settings.
    """
    base_dir = config('BASE_DIR', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return {
        'MEDIA_URL': '/media/',
        'MEDIA_ROOT': config('MEDIA_ROOT', default=os.path.join(base_dir, 'media')),
        'FILE_UPLOAD_MAX_MEMORY_SIZE': config('FILE_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int),  # 5MB
        'DATA_UPLOAD_MAX_MEMORY_SIZE': config('DATA_UPLOAD_MAX_MEMORY_SIZE', default=5242880, cast=int),  # 5MB
        'FILE_UPLOAD_PERMISSIONS': 0o644,
        'FILE_UPLOAD_DIRECTORY_PERMISSIONS': 0o755,
    }


def get_staticfiles_dirs() -> List[str]:
    """
    Get static files directories list.
    
    Returns:
        List of static files directories.
    """
    base_dir = config('BASE_DIR', default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    return [
        os.path.join(base_dir, 'static'),
        os.path.join(base_dir, 'apps', 'core', 'static'),
    ]