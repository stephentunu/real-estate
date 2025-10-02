"""
Core application views for system health and status monitoring.

This module provides essential system monitoring endpoints that ensure
the backend is healthy and ready to serve requests.
"""

from typing import Dict, Any
from django.http import JsonResponse
from django.db import connection
from django.utils import timezone
from django.conf import settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
import logging

logger = logging.getLogger(__name__)


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request) -> JsonResponse:
    """
    System health check endpoint.
    
    Provides comprehensive health status including database connectivity,
    system timestamp, and service availability. This endpoint is used by
    the frontend to verify backend availability before making API calls.
    
    Returns:
        JsonResponse: Health status with the following structure:
            {
                "status": "healthy" | "unhealthy",
                "timestamp": "2024-01-01T12:00:00Z",
                "database": "connected" | "disconnected",
                "version": "1.0.0",
                "environment": "development" | "production"
            }
    
    Raises:
        Exception: Any database or system-level errors are caught and logged.
    """
    health_data: Dict[str, Any] = {
        "status": "healthy",
        "timestamp": timezone.now().isoformat(),
        "version": "1.0.0",
        "environment": getattr(settings, 'ENVIRONMENT', 'development')
    }
    
    # Check database connectivity
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            health_data["database"] = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        health_data["database"] = "disconnected"
        health_data["status"] = "unhealthy"
    
    # Determine HTTP status code based on health
    http_status = status.HTTP_200_OK if health_data["status"] == "healthy" else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return JsonResponse(health_data, status=http_status)


@api_view(['GET'])
@permission_classes([AllowAny])
def system_status(request) -> Response:
    """
    Detailed system status endpoint.
    
    Provides extended system information including service dependencies,
    cache status, and performance metrics.
    
    Returns:
        Response: Detailed system status information.
    """
    status_data: Dict[str, Any] = {
        "system": "jaston-property-management",
        "timestamp": timezone.now().isoformat(),
        "uptime": "Available",
        "services": {
            "database": _check_database_status(),
            "cache": _check_cache_status(),
            "storage": _check_storage_status()
        }
    }
    
    return Response(status_data, status=status.HTTP_200_OK)


def _check_database_status() -> Dict[str, str]:
    """
    Check database connectivity and performance.
    
    Returns:
        Dict containing database status information.
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            return {"status": "connected", "type": "sqlite"}
    except Exception as e:
        logger.error(f"Database status check failed: {str(e)}")
        return {"status": "disconnected", "error": str(e)}


def _check_cache_status() -> Dict[str, str]:
    """
    Check cache system availability.
    
    Returns:
        Dict containing cache status information.
    """
    try:
        from django.core.cache import cache
        cache.set('health_check', 'ok', 30)
        if cache.get('health_check') == 'ok':
            return {"status": "connected"}
        else:
            return {"status": "disconnected"}
    except Exception as e:
        logger.error(f"Cache status check failed: {str(e)}")
        return {"status": "unavailable", "error": str(e)}


def _check_storage_status() -> Dict[str, str]:
    """
    Check file storage system availability.
    
    Returns:
        Dict containing storage status information.
    """
    try:
        import os
        media_root = getattr(settings, 'MEDIA_ROOT', None)
        if media_root and os.path.exists(media_root):
            return {"status": "available", "path": media_root}
        else:
            return {"status": "unavailable"}
    except Exception as e:
        logger.error(f"Storage status check failed: {str(e)}")
        return {"status": "error", "error": str(e)}