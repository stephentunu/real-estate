"""
Custom exception handlers for the Jaston Real Estate API.

This module provides centralized exception handling for the Django REST Framework
to ensure consistent error responses across all API endpoints.
"""

from typing import Any, Dict, Optional, Union
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.core.exceptions import PermissionDenied, ValidationError
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


def custom_exception_handler(exc: Exception, context: Dict[str, Any]) -> Optional[Response]:
    """
    Custom exception handler that provides consistent error responses.
    
    Args:
        exc: The exception that was raised.
        context: Additional context about the exception.
        
    Returns:
        A Response object with standardized error format, or None to use default handling.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Customize the error response format
        custom_response_data = {
            'error': True,
            'message': 'An error occurred',
            'details': response.data,
            'status_code': response.status_code
        }
        
        # Handle specific error types
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['message'] = 'Invalid request data'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['message'] = 'Authentication required'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['message'] = 'Permission denied'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['message'] = 'Resource not found'
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_response_data['message'] = 'Method not allowed'
        elif response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
            custom_response_data['message'] = 'Internal server error'
            
        response.data = custom_response_data
        
    else:
        # Handle exceptions not caught by DRF
        if isinstance(exc, Http404):
            custom_response_data = {
                'error': True,
                'message': 'Resource not found',
                'details': {'detail': 'Not found'},
                'status_code': status.HTTP_404_NOT_FOUND
            }
            response = Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)
            
        elif isinstance(exc, PermissionDenied):
            custom_response_data = {
                'error': True,
                'message': 'Permission denied',
                'details': {'detail': str(exc)},
                'status_code': status.HTTP_403_FORBIDDEN
            }
            response = Response(custom_response_data, status=status.HTTP_403_FORBIDDEN)
            
        elif isinstance(exc, ValidationError):
            custom_response_data = {
                'error': True,
                'message': 'Validation error',
                'details': {'detail': exc.message_dict if hasattr(exc, 'message_dict') else str(exc)},
                'status_code': status.HTTP_400_BAD_REQUEST
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
            
        elif isinstance(exc, IntegrityError):
            custom_response_data = {
                'error': True,
                'message': 'Database integrity error',
                'details': {'detail': 'A database constraint was violated'},
                'status_code': status.HTTP_400_BAD_REQUEST
            }
            response = Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Log the exception for debugging
    if response and response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.error(f"Server error: {exc}", exc_info=True, extra={'context': context})
    elif response and response.status_code >= status.HTTP_400_BAD_REQUEST:
        logger.warning(f"Client error: {exc}", extra={'context': context})
    
    return response


def handle_api_error(
    message: str, 
    details: Optional[Union[str, Dict[str, Any]]] = None, 
    status_code: int = status.HTTP_400_BAD_REQUEST
) -> Response:
    """
    Helper function to create standardized error responses.
    
    Args:
        message: Human-readable error message.
        details: Additional error details.
        status_code: HTTP status code for the response.
        
    Returns:
        A Response object with standardized error format.
    """
    response_data = {
        'error': True,
        'message': message,
        'details': details or {},
        'status_code': status_code
    }
    
    return Response(response_data, status=status_code)


def handle_api_success(
    data: Any, 
    message: str = 'Success', 
    status_code: int = status.HTTP_200_OK
) -> Response:
    """
    Helper function to create standardized success responses.
    
    Args:
        data: The response data.
        message: Success message.
        status_code: HTTP status code for the response.
        
    Returns:
        A Response object with standardized success format.
    """
    response_data = {
        'error': False,
        'message': message,
        'data': data,
        'status_code': status_code
    }
    
    return Response(response_data, status=status_code)