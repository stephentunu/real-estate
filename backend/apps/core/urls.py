"""
URL configuration for core application endpoints.

This module defines URL patterns for system health monitoring
and status endpoints that are essential for frontend-backend
integration validation.
"""

from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Health check endpoint for frontend validation
    path('health/', views.health_check, name='health-check'),
    
    # Detailed system status endpoint
    path('status/', views.system_status, name='system-status'),
]