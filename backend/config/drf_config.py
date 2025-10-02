"""
Django REST Framework configuration utilities for Jaston Real Estate platform.

This module provides DRF configuration management for API settings,
authentication, permissions, and serialization.
"""

from __future__ import annotations

from typing import Any, Dict, List


def get_drf_config() -> Dict[str, Any]:
    """
    Get Django REST Framework configuration.
    
    Returns:
        DRF configuration dictionary.
    """
    return {
        'DEFAULT_AUTHENTICATION_CLASSES': [
            'rest_framework.authentication.TokenAuthentication',
            'rest_framework.authentication.SessionAuthentication',
        ],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.IsAuthenticated',
        ],
        'DEFAULT_RENDERER_CLASSES': [
            'rest_framework.renderers.JSONRenderer',
        ],
        'DEFAULT_PARSER_CLASSES': [
            'rest_framework.parsers.JSONParser',
            'rest_framework.parsers.MultiPartParser',
            'rest_framework.parsers.FormParser',
        ],
        'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
        'PAGE_SIZE': 20,
        'DEFAULT_FILTER_BACKENDS': [
            'django_filters.rest_framework.DjangoFilterBackend',
            'rest_framework.filters.SearchFilter',
            'rest_framework.filters.OrderingFilter',
        ],
        'DEFAULT_THROTTLE_CLASSES': [
            'rest_framework.throttling.AnonRateThrottle',
            'rest_framework.throttling.UserRateThrottle',
        ],
        'DEFAULT_THROTTLE_RATES': {
            'anon': '100/hour',
            'user': '1000/hour',
        },
        'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.NamespaceVersioning',
        'DEFAULT_VERSION': 'v1',
        'ALLOWED_VERSIONS': ['v1'],
        'VERSION_PARAM': 'version',
        'EXCEPTION_HANDLER': 'apps.core.exceptions.custom_exception_handler',
        'TEST_REQUEST_DEFAULT_FORMAT': 'json',
        'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S.%fZ',
        'DATE_FORMAT': '%Y-%m-%d',
        'TIME_FORMAT': '%H:%M:%S',
    }


def get_swagger_config() -> Dict[str, Any]:
    """
    Get Swagger/OpenAPI configuration.
    
    Returns:
        Swagger configuration dictionary.
    """
    return {
        'SWAGGER_SETTINGS': {
            'SECURITY_DEFINITIONS': {
                'Token': {
                    'type': 'apiKey',
                    'name': 'Authorization',
                    'in': 'header',
                    'description': 'Token-based authentication with required prefix "Token"',
                },
            },
            'USE_SESSION_AUTH': True,
            'JSON_EDITOR': True,
            'SUPPORTED_SUBMIT_METHODS': [
                'get',
                'post',
                'put',
                'delete',
                'patch',
            ],
            'OPERATIONS_SORTER': 'alpha',
            'TAGS_SORTER': 'alpha',
            'DOC_EXPANSION': 'none',
            'DEEP_LINKING': True,
            'SHOW_EXTENSIONS': True,
            'DEFAULT_MODEL_RENDERING': 'model',
        },
        'REDOC_SETTINGS': {
            'LAZY_RENDERING': False,
            'HIDE_HOSTNAME': False,
            'EXPAND_RESPONSES': 'all',
            'PATH_IN_MIDDLE': True,
        },
    }


def get_api_documentation_config() -> Dict[str, Any]:
    """
    Get API documentation configuration.
    
    Returns:
        API documentation configuration dictionary.
    """
    return {
        'TITLE': 'Jaston Real Estate API',
        'DESCRIPTION': 'RESTful API for Jaston Real Estate platform',
        'VERSION': 'v1.0.0',
        'TERMS_OF_SERVICE': 'https://jastonrealestate.com/terms/',
        'CONTACT': {
            'name': 'Eleso Solutions',
            'email': 'support@ifinsta.com',
            'url': 'https://elesosolutions.com',
        },
        'LICENSE': {
            'name': 'Proprietary',
        },
        'SERVERS': [
            {
                'url': 'http://localhost:8000/api/v1/',
                'description': 'Development server',
            },
        ],
    }