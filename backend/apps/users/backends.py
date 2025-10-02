"""
Custom authentication backends for the users app.

This module provides email-based authentication backend for the custom User model.
"""

from __future__ import annotations

from typing import Optional
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()


class EmailBackend(ModelBackend):
    """
    Custom authentication backend that allows users to log in using their email address.
    
    This backend supports authentication with email and password, falling back to
    username-based authentication if email authentication fails.
    """
    
    def authenticate(
        self, 
        request, 
        username: Optional[str] = None, 
        password: Optional[str] = None, 
        email: Optional[str] = None,
        **kwargs
    ) -> Optional[User]:
        """
        Authenticate a user using email or username and password.
        
        Args:
            request: The HTTP request object.
            username: The username (can be email or actual username).
            password: The user's password.
            email: The user's email address.
            **kwargs: Additional keyword arguments.
            
        Returns:
            User instance if authentication succeeds, None otherwise.
        """
        if not password:
            return None
            
        # Use email parameter if provided, otherwise use username as email
        email_to_check = email or username
        
        if not email_to_check:
            return None
            
        try:
            # Try to find user by email first
            user = User.objects.get(
                Q(email__iexact=email_to_check) | Q(username__iexact=email_to_check)
            )
            
            # Check password and user status
            if user.check_password(password) and self.user_can_authenticate(user):
                return user
                
        except User.DoesNotExist:
            # Run the default password hasher once to reduce the timing
            # difference between an existing and a nonexistent user
            User().set_password(password)
            return None
            
        return None
    
    def get_user(self, user_id: int) -> Optional[User]:
        """
        Get user by ID.
        
        Args:
            user_id: The user's primary key.
            
        Returns:
            User instance if found, None otherwise.
        """
        try:
            user = User.objects.get(pk=user_id)
            return user if self.user_can_authenticate(user) else None
        except User.DoesNotExist:
            return None