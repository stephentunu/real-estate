"""
Core models package for Jaston Real Estate platform.

This package provides base model classes and common model utilities
following Django 5.2.6+ best practices with strict type checking.
"""

from __future__ import annotations

# Import base models for easy access
from .base import BaseModel

__all__ = [
    'BaseModel',
]