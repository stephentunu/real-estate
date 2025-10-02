"""
Base model classes for Jaston Real Estate platform.

This module provides base model classes with common functionality
including soft deletion, audit trails, and visibility controls.
"""

from __future__ import annotations

import uuid
from typing import Any, Self
from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.core.mixins import SoftDeleteMixin, VisibilityMixin

User = get_user_model()


class BaseModel(SoftDeleteMixin, VisibilityMixin, models.Model):
    """
    Base model class providing common functionality for all models.
    
    Includes:
    - UUID primary key
    - Soft deletion capability
    - Visibility/tenancy controls
    - Audit trail fields
    - Common timestamps
    """
    
    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for this record"
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created"
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated"
    )
    
    created_by: models.ForeignKey[User] = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    
    updated_by: models.ForeignKey[User] = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last updated this record"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
        
    def __str__(self: Self) -> str:
        """Return string representation of the model."""
        return f"{self.__class__.__name__}({self.id})"
    
    def save(self: Self, *args: Any, **kwargs: Any) -> None:
        """
        Save the model instance with audit trail updates.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        # Update timestamp
        self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def soft_delete(self: Self, user: User | None = None) -> None:
        """
        Perform soft deletion of the record.
        
        Args:
            user: User performing the deletion for audit trail.
        """
        self.deleted_at = timezone.now()
        if user:
            self.updated_by = user
        self.save(update_fields=['deleted_at', 'updated_at', 'updated_by'])
    
    def restore(self: Self, user: User | None = None) -> None:
        """
        Restore a soft-deleted record.
        
        Args:
            user: User performing the restoration for audit trail.
        """
        self.deleted_at = None
        if user:
            self.updated_by = user
        self.save(update_fields=['deleted_at', 'updated_at', 'updated_by'])


class TimestampedModel(models.Model):
    """
    Abstract model providing timestamp fields only.
    
    Use this for models that need timestamps but not the full BaseModel functionality.
    """
    
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when this record was created"
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when this record was last updated"
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']