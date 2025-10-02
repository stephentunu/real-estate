"""
Custom HTTP error handlers for the Jaston Real Estate API.

This module provides custom error handlers to ensure all HTTP errors
return JSON responses instead of HTML, maintaining API consistency.
"""

from typing import Any, Dict
from django.http import JsonResponse, HttpRequest
from django.views.defaults import page_not_found, server_error, bad_request, permission_denied
import logging

logger = logging.getLogger(__name__)


def handler404(request: HttpRequest, exception: Exception) -> JsonResponse:
    """
    Custom 404 error handler that returns JSON response.
    
    Args:
        request: The HTTP request object.
        exception: The exception that caused the 404 error.
        
    Returns:
        JsonResponse with standardized 404 error format.
    """
    response_data = {
        'error': True,
        'message': 'Resource not found',
        'details': {
            'detail': 'The requested resource was not found on this server.',
            'path': request.path
        },
        'status_code': 404
    }
    
    logger.warning(f"404 error for path: {request.path}")
    return JsonResponse(response_data, status=404)


def handler400(request: HttpRequest, exception: Exception) -> JsonResponse:
    """
    Custom 400 error handler that returns JSON response.
    
    Args:
        request: The HTTP request object.
        exception: The exception that caused the 400 error.
        
    Returns:
        JsonResponse with standardized 400 error format.
    """
    response_data = {
        'error': True,
        'message': 'Bad request',
        'details': {
            'detail': 'The request could not be understood by the server.',
            'path': request.path
        },
        'status_code': 400
    }
    
    logger.warning(f"400 error for path: {request.path}")
    return JsonResponse(response_data, status=400)


def handler403(request: HttpRequest, exception: Exception) -> JsonResponse:
    """
    Custom 403 error handler that returns JSON response.
    
    Args:
        request: The HTTP request object.
        exception: The exception that caused the 403 error.
        
    Returns:
        JsonResponse with standardized 403 error format.
    """
    response_data = {
        'error': True,
        'message': 'Permission denied',
        'details': {
            'detail': 'You do not have permission to access this resource.',
            'path': request.path
        },
        'status_code': 403
    }
    
    logger.warning(f"403 error for path: {request.path}")
    return JsonResponse(response_data, status=403)


def handler500(request: HttpRequest) -> JsonResponse:
    """
    Custom 500 error handler that returns JSON response.
    
    Args:
        request: The HTTP request object.
        
    Returns:
        JsonResponse with standardized 500 error format.
    """
    response_data = {
        'error': True,
        'message': 'Internal server error',
        'details': {
            'detail': 'An internal server error occurred. Please try again later.',
            'path': request.path
        },
        'status_code': 500
    }
    
    logger.error(f"500 error for path: {request.path}")
    return JsonResponse(response_data, status=500)