# **Jaston Real Estate Platform Architecture Document (v4.0)**

**Version:** 4.0  
**Date:** January 2025  
**Technical Stack:** Django 5.2.6+, Python 3.13+, Pyright Strict Mode  
**Prepared For:** Engineering Team, Technical Leadership  
**Prepared By:** Platform Architecture Team  

---

## **1. Executive Summary**

This architecture document defines the technical foundation for the Jaston Real Estate Platform, built on Django 5.2.6+ with Python 3.13+ and strict type safety requirements. The platform implements a modular architecture with centralized core functionality through the `apps.core` module, ensuring consistency, maintainability, and enterprise-grade capabilities.

**Key Technical Principles:**
- **Type Safety First**: All code must pass Pyright strict mode validation
- **Modular Architecture**: Apps reside in `backend/apps/` with shared functionality in `apps.core`
- **Enterprise Patterns**: Repository pattern, dependency injection, and service layer architecture
- **Data Integrity**: Soft deletion, audit trails, and visibility controls
- **Performance**: Optimized queries, caching, and database indexing

---

## **2. Technical Architecture**

### **2.1 Project Structure**
```
backend/
├── apps/                           # All Django applications
│   ├── core/                      # Core functionality and base classes
│   │   ├── models/               # Base model classes
│   │   ├── services/             # Base service interfaces and implementations
│   │   ├── repositories/         # Base repository patterns
│   │   ├── api/                  # Base API components
│   │   ├── mixins.py            # Reusable model mixins
│   │   └── permissions.py       # Core permission classes
│   ├── properties/              # Property management
│   ├── leases/                  # Lease management
│   ├── maintenance/             # Maintenance requests
│   ├── users/                   # User management
│   └── media/                   # File management
├── config/                        # Configuration files
│   ├── infrastructure/           # Infrastructure configs
│   └── automation/              # Configuration automation
├── docs/                         # Documentation
└── manage.py
```

### **2.2 Core Base Classes**

#### **Base Model with Type Safety**
```python
# apps/core/models/base.py
from typing import TYPE_CHECKING, Optional, Any, Dict
from uuid import uuid4
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()

class BaseModel(models.Model):
    """
    Base model with common fields and functionality.
    
    Provides:
    - UUID primary keys
    - Audit trail fields
    - Soft deletion capability
    - Type-safe field definitions
    """
    
    id: models.UUIDField = models.UUIDField(
        primary_key=True,
        default=uuid4,
        editable=False,
        help_text="Unique identifier"
    )
    
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True,
        help_text="Creation timestamp"
    )
    
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )
    
    created_by: models.ForeignKey['AbstractUser'] = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_created',
        help_text="User who created this record"
    )
    
    updated_by: models.ForeignKey['AbstractUser'] = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_updated',
        help_text="User who last updated this record"
    )
    
    is_active: models.BooleanField = models.BooleanField(
        default=True,
        help_text="Whether this record is active"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['is_active']),
        ]
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """Override save to handle audit fields."""
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"
```

#### **Visibility Control Mixin**
```python
# apps/core/mixins.py
from typing import TYPE_CHECKING, List, Optional, Dict, Any
from django.db import models
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser
    from django.db.models import QuerySet

User = get_user_model()

class VisibilityMixin(models.Model):
    """
    Mixin for implementing granular visibility controls.
    
    Provides role-based and user-specific access control
    with support for complex visibility rules.
    """
    
    class VisibilityLevel(models.TextChoices):
        PUBLIC = 'public', 'Public'
        REGISTERED = 'registered', 'Registered Users'
        AGENCY_ONLY = 'agency_only', 'Agency Staff Only'
        LANDLORD_ONLY = 'landlord_only', 'Landlord Only'
        TENANT_ONLY = 'tenant_only', 'Tenant Only'
        CLASSIFIED = 'classified', 'Classified'
        SYSTEM = 'system', 'System Only'
    
    visibility_level: models.CharField = models.CharField(
        max_length=20,
        choices=VisibilityLevel.choices,
        default=VisibilityLevel.REGISTERED,
        help_text="Base visibility level for this record"
    )
    
    visibility_groups: models.JSONField = models.JSONField(
        default=list,
        blank=True,
        help_text="Additional groups with access"
    )
    
    visibility_users: models.JSONField = models.JSONField(
        default=list,
        blank=True,
        help_text="Specific user IDs with access"
    )
    
    visibility_exceptions: models.JSONField = models.JSONField(
        default=dict,
        blank=True,
        help_text="Complex visibility rules"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['visibility_level']),
        ]
    
    def can_view(self, user: Optional['AbstractUser']) -> bool:
        """
        Check if user can view this record.
        
        Args:
            user: User to check permissions for
            
        Returns:
            bool: True if user can view this record
        """
        if not user:
            return self.visibility_level == self.VisibilityLevel.PUBLIC
        
        if not user.is_authenticated:
            return self.visibility_level == self.VisibilityLevel.PUBLIC
        
        # System users can see everything
        if user.is_staff and self.visibility_level == self.VisibilityLevel.SYSTEM:
            return True
        
        # Check specific user access
        if str(user.id) in self.visibility_users:
            return True
        
        # Check group access
        user_groups = list(user.groups.values_list('name', flat=True))
        if any(group in self.visibility_groups for group in user_groups):
            return True
        
        # Check visibility level
        if self.visibility_level == self.VisibilityLevel.REGISTERED:
            return True
        
        # Additional role-based checks would go here
        return False
    
    @classmethod
    def filter_visible(
        cls, 
        queryset: 'QuerySet', 
        user: Optional['AbstractUser']
    ) -> 'QuerySet':
        """
        Filter queryset to only include records visible to user.
        
        Args:
            queryset: Base queryset to filter
            user: User to check permissions for
            
        Returns:
            QuerySet: Filtered queryset
        """
        if not user or not user.is_authenticated:
            return queryset.filter(visibility_level=cls.VisibilityLevel.PUBLIC)
        
        # Build complex filter based on user permissions
        # This would be expanded based on specific business rules
        return queryset.filter(
            models.Q(visibility_level=cls.VisibilityLevel.PUBLIC) |
            models.Q(visibility_level=cls.VisibilityLevel.REGISTERED) |
            models.Q(visibility_users__contains=[str(user.id)])
        )
```

#### **Soft Deletion Mixin**
```python
# apps/core/mixins.py (continued)
from datetime import datetime, timedelta
from django.utils import timezone

class SoftDeleteMixin(models.Model):
    """
    Mixin for implementing soft deletion with retention policies.
    
    Provides:
    - Soft deletion capability
    - Retention policy management
    - Data recovery functionality
    """
    
    is_deleted: models.BooleanField = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this record is soft deleted"
    )
    
    deleted_at: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this record was deleted"
    )
    
    deleted_by: models.ForeignKey['AbstractUser'] = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted',
        help_text="User who deleted this record"
    )
    
    retention_until: models.DateTimeField = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this record will be permanently deleted"
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['is_deleted', 'deleted_at']),
            models.Index(fields=['retention_until']),
        ]
    
    def soft_delete(
        self, 
        user: Optional['AbstractUser'] = None,
        retention_days: int = 30
    ) -> None:
        """
        Soft delete this record.
        
        Args:
            user: User performing the deletion
            retention_days: Days to retain before permanent deletion
        """
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        self.retention_until = timezone.now() + timedelta(days=retention_days)
        self.save(update_fields=[
            'is_deleted', 'deleted_at', 'deleted_by', 'retention_until'
        ])
    
    def restore(self, user: Optional['AbstractUser'] = None) -> None:
        """
        Restore a soft-deleted record.
        
        Args:
            user: User performing the restoration
        """
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.retention_until = None
        self.updated_by = user
        self.save(update_fields=[
            'is_deleted', 'deleted_at', 'deleted_by', 
            'retention_until', 'updated_by'
        ])
    
    @property
    def days_until_permanent_deletion(self) -> Optional[int]:
        """Calculate days remaining until permanent deletion."""
        if not self.retention_until:
            return None
        
        delta = self.retention_until - timezone.now()
        return max(0, delta.days)
```

### **2.3 Service Layer Architecture**

#### **Base Service Interface**
```python
# apps/core/services/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar, Generic
from django.db.models import Model, QuerySet

ModelType = TypeVar('ModelType', bound=Model)

class IBaseService(ABC, Generic[ModelType]):
    """Base service interface defining common operations."""
    
    @abstractmethod
    def create(self, data: Dict[str, Any], **kwargs: Any) -> ModelType:
        """Create a new instance."""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get instance by ID."""
        pass
    
    @abstractmethod
    def update(
        self, 
        id: str, 
        data: Dict[str, Any], 
        **kwargs: Any
    ) -> Optional[ModelType]:
        """Update an existing instance."""
        pass
    
    @abstractmethod
    def delete(self, id: str, **kwargs: Any) -> bool:
        """Delete an instance (soft delete)."""
        pass
    
    @abstractmethod
    def list(self, **filters: Any) -> QuerySet[ModelType]:
        """List instances with optional filtering."""
        pass
```

#### **Base Service Implementation**
```python
# apps/core/services/base.py
from typing import Any, Dict, List, Optional, Type
from django.db import transaction
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .interfaces import IBaseService, ModelType

User = get_user_model()

class BaseService(IBaseService[ModelType]):
    """Base service implementation with common functionality."""
    
    def __init__(self, model_class: Type[ModelType]):
        self.model_class = model_class
    
    @transaction.atomic
    def create(self, data: Dict[str, Any], **kwargs: Any) -> ModelType:
        """Create a new instance with validation."""
        # Extract user from kwargs if provided
        user = kwargs.get('user')
        
        # Validate data
        self._validate_create_data(data)
        
        # Add audit fields if model supports them
        if hasattr(self.model_class, 'created_by') and user:
            data['created_by'] = user
        
        # Create instance
        instance = self.model_class(**data)
        instance.full_clean()  # Run model validation
        instance.save()
        
        return instance
    
    def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get instance by ID, respecting soft deletion."""
        try:
            queryset = self.model_class.objects.all()
            
            # Filter out soft-deleted items if model supports it
            if hasattr(self.model_class, 'is_deleted'):
                queryset = queryset.filter(is_deleted=False)
            
            return queryset.get(id=id)
        except self.model_class.DoesNotExist:
            return None
    
    @transaction.atomic
    def update(
        self, 
        id: str, 
        data: Dict[str, Any], 
        **kwargs: Any
    ) -> Optional[ModelType]:
        """Update an existing instance."""
        instance = self.get_by_id(id)
        if not instance:
            return None
        
        user = kwargs.get('user')
        
        # Validate update data
        self._validate_update_data(data, instance)
        
        # Update fields
        for field, value in data.items():
            if hasattr(instance, field):
                setattr(instance, field, value)
        
        # Add audit fields if model supports them
        if hasattr(instance, 'updated_by') and user:
            instance.updated_by = user
        
        instance.full_clean()
        instance.save()
        
        return instance
    
    def delete(self, id: str, **kwargs: Any) -> bool:
        """Delete an instance (soft delete if supported)."""
        instance = self.get_by_id(id)
        if not instance:
            return False
        
        user = kwargs.get('user')
        
        # Use soft delete if available
        if hasattr(instance, 'soft_delete'):
            instance.soft_delete(user=user)
        else:
            instance.delete()
        
        return True
    
    def list(self, **filters: Any) -> QuerySet[ModelType]:
        """List instances with filtering."""
        queryset = self.model_class.objects.all()
        
        # Filter out soft-deleted items if model supports it
        if hasattr(self.model_class, 'is_deleted'):
            queryset = queryset.filter(is_deleted=False)
        
        # Apply visibility filtering if model supports it
        user = filters.pop('user', None)
        if hasattr(self.model_class, 'filter_visible') and user:
            queryset = self.model_class.filter_visible(queryset, user)
        
        # Apply other filters
        return queryset.filter(**filters)
    
    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate data for creation. Override in subclasses."""
        pass
    
    def _validate_update_data(
        self, 
        data: Dict[str, Any], 
        instance: ModelType
    ) -> None:
        """Validate data for updates. Override in subclasses."""
        pass
```

### **2.4 Repository Pattern**

#### **Base Repository Interface**
```python
# apps/core/repositories/interfaces.py
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, TypeVar
from django.db.models import Model, QuerySet

ModelType = TypeVar('ModelType', bound=Model)

class IBaseRepository(ABC):
    """Base repository interface for data access operations."""
    
    @abstractmethod
    def create(self, **kwargs: Any) -> ModelType:
        """Create a new record."""
        pass
    
    @abstractmethod
    def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get record by ID."""
        pass
    
    @abstractmethod
    def update(self, id: str, **kwargs: Any) -> Optional[ModelType]:
        """Update existing record."""
        pass
    
    @abstractmethod
    def delete(self, id: str) -> bool:
        """Delete record."""
        pass
    
    @abstractmethod
    def filter(self, **kwargs: Any) -> QuerySet[ModelType]:
        """Filter records by criteria."""
        pass
    
    @abstractmethod
    def all(self) -> QuerySet[ModelType]:
        """Get all records."""
        pass
```

#### **Base Repository Implementation**
```python
# apps/core/repositories/base.py
from typing import Any, Optional, Type
from django.db.models import Model, QuerySet
from .interfaces import IBaseRepository, ModelType

class BaseRepository(IBaseRepository):
    """Base repository implementation."""
    
    def __init__(self, model_class: Type[ModelType]):
        self.model = model_class
    
    def create(self, **kwargs: Any) -> ModelType:
        """Create a new record."""
        return self.model.objects.create(**kwargs)
    
    def get_by_id(self, id: str) -> Optional[ModelType]:
        """Get record by ID."""
        try:
            return self.model.objects.get(id=id)
        except self.model.DoesNotExist:
            return None
    
    def update(self, id: str, **kwargs: Any) -> Optional[ModelType]:
        """Update existing record."""
        try:
            instance = self.model.objects.get(id=id)
            for field, value in kwargs.items():
                setattr(instance, field, value)
            instance.save()
            return instance
        except self.model.DoesNotExist:
            return None
    
    def delete(self, id: str) -> bool:
        """Delete record."""
        try:
            instance = self.model.objects.get(id=id)
            instance.delete()
            return True
        except self.model.DoesNotExist:
            return False
    
    def filter(self, **kwargs: Any) -> QuerySet[ModelType]:
        """Filter records by criteria."""
        return self.model.objects.filter(**kwargs)
    
    def all(self) -> QuerySet[ModelType]:
        """Get all records."""
        return self.model.objects.all()
```

---

## **3. Implementation Examples**

### **3.1 Property Model Implementation**
```python
# apps/properties/models/property_models.py
from typing import TYPE_CHECKING, Optional
from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models.base import BaseModel
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()

class Property(BaseModel, VisibilityMixin, SoftDeleteMixin):
    """Property model for real estate listings."""
    
    class PropertyType(models.TextChoices):
        HOUSE = 'house', 'House'
        APARTMENT = 'apartment', 'Apartment'
        CONDO = 'condo', 'Condominium'
        TOWNHOUSE = 'townhouse', 'Townhouse'
        COMMERCIAL = 'commercial', 'Commercial'
    
    class Status(models.TextChoices):
        AVAILABLE = 'available', 'Available'
        RENTED = 'rented', 'Rented'
        SOLD = 'sold', 'Sold'
        MAINTENANCE = 'maintenance', 'Under Maintenance'
    
    title: models.CharField = models.CharField(
        max_length=200,
        help_text="Property title"
    )
    
    description: models.TextField = models.TextField(
        blank=True,
        help_text="Detailed property description"
    )
    
    property_type: models.CharField = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.HOUSE
    )
    
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.AVAILABLE
    )
    
    price: models.DecimalField = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="Property price or rent amount"
    )
    
    bedrooms: models.PositiveIntegerField = models.PositiveIntegerField(
        default=1,
        help_text="Number of bedrooms"
    )
    
    bathrooms: models.DecimalField = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=1.0,
        help_text="Number of bathrooms"
    )
    
    square_feet: models.PositiveIntegerField = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Property size in square feet"
    )
    
    address: models.TextField = models.TextField(
        help_text="Property address"
    )
    
    # Relationships
    owner: models.ForeignKey['AbstractUser'] = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_properties',
        help_text="Property owner"
    )
    
    class Meta:
        db_table = 'properties_property'
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property_type', 'status']),
            models.Index(fields=['owner', 'status']),
            models.Index(fields=['price']),
            models.Index(fields=['is_active', 'status']),
            models.Index(fields=['is_deleted', 'status']),
        ]
    
    def __str__(self) -> str:
        return f"{self.title} - {self.get_property_type_display()}"
    
    def get_formatted_price(self) -> str:
        """Return formatted price string."""
        return f"${self.price:,.2f}"
    
    @property
    def is_available(self) -> bool:
        """Check if property is available."""
        return (
            self.status == self.Status.AVAILABLE 
            and self.is_active 
            and not self.is_deleted
        )
```

### **3.2 Property Service Implementation**
```python
# apps/properties/services/implementations.py
from typing import Dict, Any, List, Optional
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.core.services.base import BaseService
from apps.core.di.decorators import injectable
from ..models import Property
from .interfaces import IPropertyService

User = get_user_model()

@injectable('property_service')
class PropertyService(BaseService[Property], IPropertyService):
    """Service implementation for property operations."""
    
    def __init__(self):
        super().__init__(Property)
    
    @transaction.atomic
    def create_property(
        self, 
        property_data: Dict[str, Any], 
        owner: User
    ) -> Property:
        """Create a new property listing."""
        # Set owner
        property_data['owner'] = owner
        
        # Set default visibility for properties
        if 'visibility_level' not in property_data:
            property_data['visibility_level'] = Property.VisibilityLevel.REGISTERED
        
        return self.create(property_data, user=owner)
    
    def search_properties(
        self, 
        criteria: Dict[str, Any],
        user: Optional[User] = None
    ) -> List[Property]:
        """Search properties by criteria."""
        queryset = self.list(user=user)
        
        # Apply search criteria
        if 'property_type' in criteria:
            queryset = queryset.filter(property_type=criteria['property_type'])
        
        if 'min_price' in criteria:
            queryset = queryset.filter(price__gte=criteria['min_price'])
        
        if 'max_price' in criteria:
            queryset = queryset.filter(price__lte=criteria['max_price'])
        
        if 'bedrooms' in criteria:
            queryset = queryset.filter(bedrooms=criteria['bedrooms'])
        
        if 'search_term' in criteria:
            search_term = criteria['search_term']
            queryset = queryset.filter(
                models.Q(title__icontains=search_term) |
                models.Q(description__icontains=search_term) |
                models.Q(address__icontains=search_term)
            )
        
        return list(queryset.distinct())
    
    def _validate_create_data(self, data: Dict[str, Any]) -> None:
        """Validate property creation data."""
        required_fields = ['title', 'property_type', 'price', 'address']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Field '{field}' is required")
        
        if data.get('price', 0) <= 0:
            raise ValidationError("Price must be greater than 0")
        
        if data.get('bedrooms', 0) < 0:
            raise ValidationError("Bedrooms cannot be negative")
        
        if data.get('bathrooms', 0) < 0:
            raise ValidationError("Bathrooms cannot be negative")
```

---

## **4. Configuration Management**

### **4.1 Configuration Structure**
```
config/
├── infrastructure/
│   ├── docker/
│   │   ├── Dockerfile
│   │   └── docker-compose.yml
│   ├── kubernetes/
│   │   ├── deployment.yaml
│   │   └── service.yaml
│   └── terraform/
│       ├── main.tf
│       └── variables.tf
└── automation/
    ├── deployment/
    │   ├── deploy.py
    │   └── rollback.py
    ├── monitoring/
    │   ├── health_checks.py
    │   └── metrics.py
    └── backup/
        ├── backup_strategy.py
        └── restore_procedures.py
```

### **4.2 Django Settings Configuration**
```python
# config/settings/base.py
from typing import List, Dict, Any
import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Application definition
DJANGO_APPS: List[str] = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS: List[str] = [
    'rest_framework',
    'drf_yasg',
    'corsheaders',
    'django_filters',
]

LOCAL_APPS: List[str] = [
    'apps.core',
    'apps.users',
    'apps.properties',
    'apps.leases',
    'apps.maintenance',
    'apps.media',
]

INSTALLED_APPS: List[str] = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# Database configuration with type safety
DATABASES: Dict[str, Dict[str, Any]] = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# REST Framework configuration
REST_FRAMEWORK: Dict[str, Any] = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
}

# Logging configuration
LOGGING: Dict[str, Any] = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'django.log',
            'formatter': 'verbose',
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
}
```

---

## **5. Compliance and Security**

### **5.1 Data Protection**
- **GDPR/CCPA Compliance**: Soft deletion framework enables "right to be forgotten"
- **Data Minimization**: Visibility levels ensure users only see necessary information
- **Access Controls**: Role-based permissions with granular visibility settings
- **Audit Trails**: Complete audit logging for all data modifications

### **5.2 Security Measures**
- **Type Safety**: Pyright strict mode prevents type-related vulnerabilities
- **Input Validation**: Comprehensive validation at model and service layers
- **SQL Injection Prevention**: Django ORM with parameterized queries
- **Authentication**: JWT-based authentication with refresh token rotation
- **Authorization**: Role-based access control with visibility mixins

---

## **6. Performance Optimization**

### **6.1 Database Optimization**
- **Indexing Strategy**: Comprehensive indexes on frequently queried fields
- **Query Optimization**: Repository pattern with optimized querysets
- **Connection Pooling**: Database connection pooling for high concurrency
- **Read Replicas**: Separate read/write database connections

### **6.2 Caching Strategy**
- **Model Caching**: Cache frequently accessed model instances
- **Query Caching**: Cache expensive database queries
- **API Response Caching**: Cache API responses with appropriate TTL
- **Static Asset Caching**: CDN integration for static assets

---

**Document Approved By:**  
[CTO], [Lead Architect], [Senior Backend Engineer], [DevOps Lead]  

**Next Steps:**  
1. Implement core base classes and mixins
2. Set up dependency injection container
3. Create property management app following patterns
4. Implement comprehensive test suite
5. Deploy to staging environment for integration testing