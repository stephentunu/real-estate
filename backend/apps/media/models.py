"""
Media models for file management in Jaston Real Estate platform.
"""

from __future__ import annotations

import os
from typing import Any, Self
from django.db import models
from django.core.files.storage import default_storage
from django.contrib.auth import get_user_model
from apps.core.models.base import BaseModel

User = get_user_model()


def upload_to_media(instance: File, filename: str) -> str:
    """
    Generate upload path for media files.
    
    Args:
        instance: The File model instance.
        filename: Original filename.
        
    Returns:
        Upload path for the file.
    """
    # Create path based on file type and date
    return f"media/{instance.file_type}/{filename}"


class File(BaseModel):
    """
    Model for managing uploaded files and media.
    """
    
    FILE_TYPES = [
        ('image', 'Image'),
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Other'),
    ]
    
    name: models.CharField = models.CharField(
        max_length=255,
        help_text="Display name for the file"
    )
    
    file: models.FileField = models.FileField(
        upload_to=upload_to_media,
        help_text="The uploaded file"
    )
    
    file_type: models.CharField = models.CharField(
        max_length=20,
        choices=FILE_TYPES,
        default='other',
        help_text="Type of file"
    )
    
    file_size: models.PositiveIntegerField = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    
    mime_type: models.CharField = models.CharField(
        max_length=100,
        blank=True,
        help_text="MIME type of the file"
    )
    
    description: models.TextField = models.TextField(
        blank=True,
        help_text="Optional description of the file"
    )
    
    is_public: models.BooleanField = models.BooleanField(
        default=False,
        help_text="Whether the file is publicly accessible"
    )
    
    class Meta:
        verbose_name = "File"
        verbose_name_plural = "Files"
        ordering = ['-created_at']
        
    def __str__(self: Self) -> str:
        """Return string representation of the file."""
        return self.name
    
    def save(self: Self, *args: Any, **kwargs: Any) -> None:
        """
        Save the file with additional metadata.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
        """
        if self.file:
            # Set file size
            self.file_size = self.file.size
            
            # Set file type based on extension if not set
            if not self.file_type or self.file_type == 'other':
                self.file_type = self._determine_file_type()
                
            # Set name from filename if not provided
            if not self.name:
                self.name = os.path.basename(self.file.name)
        
        super().save(*args, **kwargs)
    
    def _determine_file_type(self: Self) -> str:
        """
        Determine file type based on file extension.
        
        Returns:
            File type string.
        """
        if not self.file:
            return 'other'
            
        filename = self.file.name.lower()
        
        if filename.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp')):
            return 'image'
        elif filename.endswith(('.pdf', '.doc', '.docx', '.txt', '.rtf', '.odt')):
            return 'document'
        elif filename.endswith(('.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm')):
            return 'video'
        elif filename.endswith(('.mp3', '.wav', '.ogg', '.m4a', '.flac')):
            return 'audio'
        else:
            return 'other'
    
    def delete(self: Self, *args: Any, **kwargs: Any) -> tuple[int, dict[str, int]]:
        """
        Delete the file and its associated file from storage.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            Tuple of (number_of_objects_deleted, dict_of_deletions_per_type).
        """
        # Delete the file from storage
        if self.file and default_storage.exists(self.file.name):
            default_storage.delete(self.file.name)
        
        return super().delete(*args, **kwargs)
    
    @property
    def url(self: Self) -> str:
        """
        Get the URL for the file.
        
        Returns:
            URL string for accessing the file.
        """
        if self.file:
            return self.file.url
        return ""
    
    @property
    def file_extension(self: Self) -> str:
        """
        Get the file extension.
        
        Returns:
            File extension string.
        """
        if self.file:
            return os.path.splitext(self.file.name)[1].lower()
        return ""