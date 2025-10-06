"""
Custom middleware for the Jaston Real Estate API.
This module provides middleware to handle API-specific concerns like
JSON error responses for API endpoints even when DEBUG=True.
"""
from typing import Callable, Optional
from django.http import HttpRequest, HttpResponse, JsonResponse, Http404
from django.urls import resolve, Resolver404
from rest_framework.exceptions import APIException
import logging

logger = logging.getLogger(__name__)


class APIErrorMiddleware:
    """
    Middleware to handle API errors and return JSON responses.
    
    This middleware ensures that API endpoints (paths starting with /api/)
    return JSON error responses instead of HTML, even when DEBUG=True.
    """

    
    
    def __init__(self, get_response: Callable[[HttpRequest], HttpResponse]) -> None:
        """
        Initialize the middleware.
        
        Args:
            get_response: The next middleware or view in the chain.
        """
        self.get_response = get_response
    
    def __call__(self, request: HttpRequest) -> HttpResponse:
        """
        Process the request and handle API errors.
        
        Args:
            request: The HTTP request object.
            
        Returns:
            HttpResponse object, potentially modified for API errors.
        """
        # Process the request normally first - let DRF handle versioning
        response = self.get_response(request)
        
        # Handle API responses that might be HTML errors
        if (request.path.startswith('/api/') and 
            response.status_code >= 400 and 
            response.get('Content-Type', '').startswith('text/html')):
            
            response_data = {
                'error': True,
                'message': 'Resource not found' if response.status_code == 404 else 'An error occurred',
                'details': {
                    'detail': 'The requested API endpoint was not found.' if response.status_code == 404 else 'An error occurred processing your request.',
                    'path': request.path
                },
                'status_code': response.status_code
            }
            logger.warning(f"Converting HTML {response.status_code} to JSON for API path: {request.path}")
            return JsonResponse(response_data, status=response.status_code)
        
        return response
    
    def process_exception(self, request: HttpRequest, exception: Exception) -> Optional[HttpResponse]:
        """
        Handle exceptions for API requests.
        
        Args:
            request: The HTTP request object.
            exception: The exception that was raised.
            
        Returns:
            JsonResponse for API requests, None otherwise.
        """
        if request.path.startswith('/api/'):
            if isinstance(exception, Http404):
                response_data = {
                    'error': True,
                    'message': 'Resource not found',
                    'details': {
                        'detail': 'The requested API endpoint was not found.',
                        'path': request.path
                    },
                    'status_code': 404
                }
                logger.warning(f"API 404 exception for path: {request.path}")
                return JsonResponse(response_data, status=404)
        
        return None