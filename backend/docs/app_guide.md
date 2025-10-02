# Django App Development Guide - Jaston Real Estate Platform

This guide outlines the standards and patterns for creating new Django applications within the Jaston Real Estate platform. Follow these guidelines to ensure consistency, maintainability, and adherence to our architectural principles.

**Technical Requirements:**
- Django 5.2.6+
- Python 3.13+
- **Pyright strict mode type checking** (mandatory for all Python code)
- 3rd Normal Form (3NF) database design
- Port 8000 for backend services
- **Complete type annotations** required for all functions, methods, and class attributes
- **Google-style Python docstrings** with type information in Args/Returns sections

## 📋 Table of Contents

- [App Structure](#app-structure)
- [Architecture Patterns](#architecture-patterns)
- [Type Safety Requirements](#type-safety-requirements)
- [Cross-App Dependencies](#cross-app-dependencies)
- [Models](#models)
- [Services](#services)
- [Repositories](#repositories)
- [Serializers](#serializers)
- [Views & ViewSets](#views--viewsets)
- [URLs](#urls)
- [Tests](#tests)
- [Documentation](#documentation)
- [Best Practices](#best-practices)

## 🏗️ App Structure

Every new app should follow this standardized directory structure that leverages core base classes and follows our architectural patterns:

```
app_name/
├── __init__.py
├── apps.py                 # App configuration with DI registration
├── admin/                  # Admin configurations
│   ├── __init__.py
│   └── app_name_admin.py   # Inherits from apps.core.admin.base
├── api/                    # API-related components
│   ├── __init__.py
│   ├── serializers.py      # Uses apps.core.api.serializers base classes
│   ├── viewsets.py         # Inherits from apps.core.api.viewsets
│   ├── filters.py          # Custom filtering logic
│   └── permissions.py      # App-specific permissions
├── models/                 # Data models
│   ├── __init__.py
│   └── app_name_models.py  # Inherits from apps.core.models.BaseModel
├── mappers/               # Field transformation mappers
│   ├── __init__.py
│   └── app_name_mapper.py  # Inherits from apps.core.mappers.BaseMapper
├── repositories/           # Data access layer
│   ├── __init__.py
│   ├── interfaces.py       # Extends apps.core.repositories.interfaces
│   └── implementations.py  # Inherits from apps.core.repositories.BaseRepository
├── services/              # Business logic layer
│   ├── __init__.py
│   ├── interfaces.py       # Extends apps.core.services.interfaces
│   └── implementations.py  # Inherits from apps.core.services.BaseService
├── tests/                 # Test modules
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_services.py
│   ├── test_repositories.py
│   ├── test_mappers.py
│   └── test_views.py
├── views/                 # View components (if needed beyond API)
│   ├── __init__.py
│   └── app_name_views.py
├── urls.py               # URL routing with hierarchy support
└── migrations/           # Database migrations
    └── __init__.py
```

### Key Architectural Principles

1. **Inherit from Core Base Classes**: Always extend base classes from `apps.core` to maintain consistency
2. **Cross-App Dependencies**: Import models from other apps when needed (user, media, contact, etc.)
3. **API Hierarchy**: Structure URLs to reflect data relationships and ownership
4. **Dependency Injection**: Register services and repositories in the DI container
5. **Field Mapping**: Use mappers for consistent API field transformation
6. **Type Safety**: All code must include complete type annotations with Pyright strict mode compliance

## 🔒 Type Safety Requirements

All Python code must comply with **Pyright strict mode** requirements. This is mandatory for maintaining code quality and preventing runtime errors.

### Pyright Configuration

Ensure your project has a `pyrightconfig.json` file in the root directory:

```json
{
  "typeCheckingMode": "strict",
  "reportMissingTypeStubs": false,
  "reportUnknownMemberType": false,
  "pythonVersion": "3.13",
  "pythonPlatform": "Linux"
}
```

### Type Checking Commands

```bash
# Run Pyright type checking
npx pyright

# Run Pyright with specific files
npx pyright backend/apps/properties/

# Run Pyright in watch mode
npx pyright --watch
```

### Function and Method Signatures

All functions and methods must include complete type annotations following Google-style docstrings:

```python
from typing import Dict, List, Optional, Union, Any, Self
from django.contrib.auth import get_user_model
from django.db.models import QuerySet

User = get_user_model()

class PropertyService:
    """Service for property management operations."""
    
    def __init__(self: Self, repository: 'PropertyRepository') -> None:
        """Initialize the property service.
        
        Args:
            repository: Property data access repository.
        """
        self.repository = repository
    
    def create_property(
        self: Self,
        property_data: Dict[str, Any], 
        user: User
    ) -> 'Property':
        """Create a new property with validation.
        
        Args:
            property_data: Dictionary containing property information including
                title, description, price, and property type.
            user: User creating the property, must be authenticated.
            
        Returns:
            Property: The created property instance with all fields populated.
            
        Raises:
            ValidationError: If property data is invalid or incomplete.
            PermissionError: If user lacks permission to create properties.
        """
        # Implementation with type safety
        pass
    
    def get_properties_by_user(self: Self, user_id: int) -> QuerySet['Property']:
        """Retrieve properties owned by a specific user.
        
        Args:
            user_id: ID of the property owner, must be a valid user ID.
            
        Returns:
            QuerySet[Property]: Filtered property queryset ordered by creation date.
            
        Raises:
            User.DoesNotExist: If no user exists with the given ID.
        """
        # Implementation with type safety
        pass
```

### Model Type Annotations

All Django models must include complete type annotations for fields and methods:

```python
from typing import TYPE_CHECKING, Optional, Self
from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models.base import BaseModel

if TYPE_CHECKING:
    from apps.media.models import File
    from django.contrib.auth.models import AbstractUser

User = get_user_model()

class Property(BaseModel):
    """Property model with complete type annotations and Google-style docstrings."""
    
    class PropertyType(models.TextChoices):
        """Available property types."""
        HOUSE = 'house', 'House'
        APARTMENT = 'apartment', 'Apartment'
        CONDO = 'condo', 'Condominium'
    
    # Field type annotations are mandatory
    title: models.CharField = models.CharField(
        max_length=200,
        help_text="Property title"
    )
    description: models.TextField = models.TextField(
        blank=True,
        help_text="Detailed property description"
    )
    price: models.DecimalField = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text="Property price in USD"
    )
    property_type: models.CharField = models.CharField(
        max_length=20,
        choices=PropertyType.choices,
        default=PropertyType.HOUSE
    )
    
    # Foreign key relationships with proper type annotations
    owner: models.ForeignKey['AbstractUser'] = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='owned_properties',
        help_text="Property owner"
    )
    
    def get_formatted_price(self: Self) -> str:
        """Return formatted price string with currency symbol.
        
        Returns:
            str: Formatted price string (e.g., "$1,250,000.00").
        """
        return f"${self.price:,.2f}"
    
    def is_available(self: Self) -> bool:
        """Check if property is available for rent or sale.
        
        Returns:
            bool: True if property is available, False otherwise.
        """
        return self.status == self.Status.AVAILABLE
    
    def __str__(self: Self) -> str:
        """Return string representation of the property.
        
        Returns:
            str: Property title and price.
        """
        return f"{self.title} - {self.get_formatted_price()}"
```

## 🔗 Cross-App Dependencies

Jaston Real Estate follows a modular architecture where apps can import and use models from other apps. This promotes code reuse and maintains data consistency across the system.

### Common Cross-App Imports

#### User Models
```python
# Always use get_user_model() for user references
from typing import TYPE_CHECKING
from django.contrib.auth import get_user_model

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()

class YourModel(BaseModel):
    user: models.ForeignKey['AbstractUser'] = models.ForeignKey(
        User, 
        on_delete=models.CASCADE
    )
    created_by: models.ForeignKey['AbstractUser'] = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='%(class)s_created'
    )
```

#### Media Models
```python
# Import media models for file attachments
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.media.models import File

class YourModel(BaseModel):
    avatar: models.ForeignKey['File'] = models.ForeignKey(
        'media.File',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_avatars'
    )
    attachments: models.ManyToManyField['File'] = models.ManyToManyField(
        'media.File',
        blank=True,
        related_name='%(class)s_attachments'
    )
```

## 📊 Models

Jaston Real Estate models should inherit from core base classes to leverage built-in functionality like soft deletion, audit trails, and common fields.

### Base Model Inheritance

#### Using BaseModel (Basic)
```python
# models/property_models.py
from typing import TYPE_CHECKING, Optional
from django.db import models
from django.contrib.auth import get_user_model
from apps.core.models.base import BaseModel

if TYPE_CHECKING:
    from django.contrib.auth.models import AbstractUser

User = get_user_model()

class Property(BaseModel):
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
        ]
    
    def __str__(self) -> str:
        return f"{self.title} - {self.get_property_type_display()}"
    
    def get_formatted_price(self) -> str:
        """Return formatted price string."""
        return f"${self.price:,.2f}"
    
    @property
    def is_available(self) -> bool:
        """Check if property is available."""
        return self.status == self.Status.AVAILABLE and self.is_active
```

## 🔧 Services

Services implement business logic and coordinate between repositories, external services, and other components. All services must include complete type annotations and Google-style docstrings.

```python
# services/interfaces.py
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Self
from django.contrib.auth import get_user_model
from apps.core.services.interfaces import IBaseService

User = get_user_model()

class IPropertyService(IBaseService):
    """Service interface for property operations with complete type annotations."""
    
    @abstractmethod
    def create_property(
        self: Self,
        property_data: Dict[str, Any], 
        owner: User
    ) -> Dict[str, Any]:
        """Create a new property listing.
        
        Args:
            property_data: Dictionary containing property information including
                title, description, price, and property type.
            owner: User who will own the property, must be authenticated.
            
        Returns:
            Dict[str, Any]: Created property data with ID and metadata.
            
        Raises:
            ValidationError: If property data is invalid.
            PermissionError: If owner lacks permission to create properties.
        """
        pass
    
    @abstractmethod
    def search_properties(
        self: Self,
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search properties by criteria.
        
        Args:
            criteria: Search criteria including location, price range,
                property type, and other filters.
                
        Returns:
            List[Dict[str, Any]]: List of matching properties with metadata.
        """
        pass
```

```python
# services/implementations.py
from typing import Dict, Any, List, Optional, Self
from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.exceptions import ValidationError
from apps.core.services.base import BaseService
from apps.core.di.decorators import injectable, inject
from .interfaces import IPropertyService
from ..models import Property
from ..repositories.interfaces import IPropertyRepository

User = get_user_model()

@injectable('property_service')
class PropertyService(BaseService, IPropertyService):
    """Service implementation for property operations with complete type safety."""
    
    def __init__(
        self: Self,
        repository: IPropertyRepository = inject('property_repository')
    ) -> None:
        """Initialize the property service.
        
        Args:
            repository: Property data access repository for database operations.
        """
        super().__init__()
        self.repository = repository
    
    @transaction.atomic
    def create_property(
        self: Self,
        property_data: Dict[str, Any], 
        owner: User
    ) -> Dict[str, Any]:
        """Create a new property listing with validation and transaction safety.
        
        Args:
            property_data: Dictionary containing property information including
                title (str), description (str), price (Decimal), property_type (str),
                bedrooms (int), bathrooms (Decimal), and square_feet (Optional[int]).
            owner: User who will own the property, must be authenticated and active.
            
        Returns:
            Dict[str, Any]: Created property data containing:
                - id (str): Property UUID
                - title (str): Property title
                - status (str): Property status
                - created_at (str): ISO formatted creation timestamp
                
        Raises:
            ValidationError: If property data is invalid or incomplete.
            PermissionError: If owner lacks permission to create properties.
            IntegrityError: If database constraints are violated.
        """
        # Validate input data
        self._validate_property_data(property_data)
        self._validate_owner_permissions(owner)
        
        # Create property with owner assignment
        property_data['owner'] = owner
        property_obj = self.repository.create(**property_data)
        
        return {
            'id': str(property_obj.id),
            'title': property_obj.title,
            'status': property_obj.status,
            'created_at': property_obj.created_at.isoformat()
        }
    
    def search_properties(
        self: Self,
        criteria: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Search properties by criteria with filtering and pagination.
        
        Args:
            criteria: Search criteria dictionary containing:
                - location (Optional[str]): Location filter
                - min_price (Optional[Decimal]): Minimum price filter
                - max_price (Optional[Decimal]): Maximum price filter
                - property_type (Optional[str]): Property type filter
                - bedrooms (Optional[int]): Minimum bedrooms filter
                - limit (Optional[int]): Maximum results to return
                - offset (Optional[int]): Results offset for pagination
                
        Returns:
            List[Dict[str, Any]]: List of matching properties, each containing:
                - id (str): Property UUID
                - title (str): Property title
                - price (str): Formatted price
                - property_type (str): Property type
                - location (str): Property location
        """
        properties = self.repository.search_by_criteria(criteria)
        
        return [
            {
                'id': str(prop.id),
                'title': prop.title,
                'price': prop.get_formatted_price(),
                'property_type': prop.get_property_type_display(),
                'location': prop.address.city if prop.address else 'Unknown'
            }
            for prop in properties
        ]
    
    def _validate_property_data(self: Self, data: Dict[str, Any]) -> None:
        """Validate property data before creation.
        
        Args:
            data: Property data dictionary to validate.
            
        Raises:
            ValidationError: If required fields are missing or invalid.
        """
        required_fields = ['title', 'price', 'property_type']
        missing_fields = [field for field in required_fields if field not in data]
        
        if missing_fields:
            raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    def _validate_owner_permissions(self: Self, owner: User) -> None:
        """Validate that the owner has permission to create properties.
        
        Args:
            owner: User to validate permissions for.
            
        Raises:
            PermissionError: If owner lacks necessary permissions.
        """
        if not owner.is_active:
            raise PermissionError("Inactive users cannot create properties")
        
        if not owner.has_perm('properties.add_property'):
            raise PermissionError("User lacks permission to create properties")
```
        
        return [
            {
                'id': str(prop.id),
                'title': prop.title,
                'property_type': prop.property_type,
                'price': float(prop.price),
                'bedrooms': prop.bedrooms,
                'bathrooms': float(prop.bathrooms)
            }
            for prop in properties
        ]
    
    def _validate_property_data(self, data: Dict[str, Any]) -> None:
        """Validate property data."""
        required_fields = ['title', 'property_type', 'price']
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValidationError(f"Field '{field}' is required")
        
        if data.get('price', 0) <= 0:
            raise ValidationError("Price must be greater than 0")
```

## 🗄️ Repositories

Repositories provide a clean abstraction layer for data access operations.

```python
# repositories/interfaces.py
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet
from apps.core.repositories.interfaces import IBaseRepository

class IPropertyRepository(IBaseRepository):
    """Repository interface for property operations."""
    
    @abstractmethod
    def get_by_owner(self, owner_id: str) -> QuerySet:
        """Get properties by owner."""
        pass
    
    @abstractmethod
    def search_by_criteria(self, criteria: Dict[str, Any]) -> QuerySet:
        """Search properties by multiple criteria."""
        pass
    
    @abstractmethod
    def get_available_properties(self) -> QuerySet:
        """Get all available properties."""
        pass
```

```python
# repositories/implementations.py
from typing import Dict, Any
from django.db.models import QuerySet, Q
from apps.core.repositories.base import BaseRepository
from ..models import Property
from .interfaces import IPropertyRepository

class PropertyRepository(BaseRepository, IPropertyRepository):
    """Repository implementation for properties."""
    
    def __init__(self):
        super().__init__(Property)
    
    def get_by_owner(self, owner_id: str) -> QuerySet:
        """Get properties by owner."""
        return self.model.objects.filter(owner_id=owner_id)
    
    def search_by_criteria(self, criteria: Dict[str, Any]) -> QuerySet:
        """Search properties by multiple criteria."""
        queryset = self.model.objects.filter(is_active=True)
        
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
                Q(title__icontains=search_term) |
                Q(description__icontains=search_term)
            )
        
        return queryset.distinct()
    
    def get_available_properties(self) -> QuerySet:
        """Get all available properties."""
        return self.model.objects.filter(
            is_active=True,
            status=Property.Status.AVAILABLE
        ).order_by('-created_at')
```

## 🔧 Serializers

Create comprehensive serializers with proper validation:

```python
# api/serializers.py
from rest_framework import serializers
from drf_yasg.utils import swagger_serializer_method
from ..models import Property

class PropertySerializer(serializers.ModelSerializer):
    """Serializer for Property model."""
    
    # Custom fields
    formatted_price = serializers.SerializerMethodField()
    owner_name = serializers.CharField(source='owner.get_full_name', read_only=True)
    
    class Meta:
        model = Property
        fields = [
            'id',
            'title',
            'description',
            'property_type',
            'status',
            'price',
            'formatted_price',
            'bedrooms',
            'bathrooms',
            'square_feet',
            'owner_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        ref_name = 'PropertyDetail'
    
    @swagger_serializer_method(serializer_or_field=serializers.CharField)
    def get_formatted_price(self, obj: Property) -> str:
        """Get formatted price string."""
        return obj.get_formatted_price()
    
    def validate_price(self, value) -> float:
        """Validate price field."""
        if value <= 0:
            raise serializers.ValidationError("Price must be greater than 0")
        return value
    
    def validate(self, attrs):
        """Cross-field validation."""
        if attrs.get('bathrooms', 0) > attrs.get('bedrooms', 0) * 2:
            raise serializers.ValidationError(
                "Number of bathrooms seems unrealistic for the number of bedrooms"
            )
        return attrs

class PropertyCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating Property instances."""
    
    class Meta:
        model = Property
        fields = [
            'title',
            'description',
            'property_type',
            'price',
            'bedrooms',
            'bathrooms',
            'square_feet'
        ]
        ref_name = 'PropertyCreate'
```

## 🎮 Views & ViewSets

Create ViewSets that inherit from core base classes:

```python
# api/viewsets.py
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from apps.core.api.viewsets import BaseViewSet
from apps.core.di.decorators import inject
from ..services.interfaces import IPropertyService
from ..serializers import PropertySerializer, PropertyCreateSerializer

class PropertyViewSet(BaseViewSet):
    """ViewSet for property operations."""
    
    serializer_class = PropertySerializer
    create_serializer_class = PropertyCreateSerializer
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service: IPropertyService = inject('property_service')
    
    def create(self, request):
        """Create new property."""
        serializer = self.get_create_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            result = self.service.create_property(
                property_data=serializer.validated_data,
                owner=request.user
            )
            return Response(result, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response(
                {'errors': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @swagger_auto_schema(
        operation_description="Search properties by criteria",
        responses={200: PropertySerializer(many=True)}
    )
    @action(detail=False, methods=['get'])
    def search(self, request):
        """Search properties by criteria."""
        criteria = {
            'property_type': request.query_params.get('property_type'),
            'min_price': request.query_params.get('min_price'),
            'max_price': request.query_params.get('max_price'),
            'bedrooms': request.query_params.get('bedrooms'),
            'search_term': request.query_params.get('q')
        }
        
        # Remove None values
        criteria = {k: v for k, v in criteria.items() if v is not None}
        
        results = self.service.search_properties(criteria)
        return Response(results)
```

## 🔗 URLs

Structure URLs to reflect data relationships:

```python
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.viewsets import PropertyViewSet

app_name = 'properties'

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='properties')

urlpatterns = [
    path('api/v1/', include(router.urls)),
]
```

## 🧪 Tests

Write comprehensive tests for all components:

```python
# tests/test_services.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from ..services.implementations import PropertyService
from ..models import Property

User = get_user_model()

class PropertyServiceTest(TestCase):
    """Test cases for PropertyService."""
    
    def setUp(self):
        self.service = PropertyService()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_create_property_success(self):
        """Test successful property creation."""
        property_data = {
            'title': 'Test Property',
            'description': 'A test property',
            'property_type': Property.PropertyType.HOUSE,
            'price': 250000.00,
            'bedrooms': 3,
            'bathrooms': 2.0
        }
        
        result = self.service.create_property(property_data, self.user)
        
        self.assertIn('id', result)
        self.assertEqual(result['title'], 'Test Property')
        
        # Verify property was created in database
        property_obj = Property.objects.get(id=result['id'])
        self.assertEqual(property_obj.title, 'Test Property')
        self.assertEqual(property_obj.owner, self.user)
    
    def test_create_property_validation_error(self):
        """Test property creation with invalid data."""
        property_data = {
            'title': '',  # Invalid: empty title
            'price': -1000  # Invalid: negative price
        }
        
        with self.assertRaises(ValidationError):
            self.service.create_property(property_data, self.user)
```

## 📚 Best Practices

1. **Type Safety**: Use complete type annotations with Pyright strict mode
2. **Inheritance**: Always inherit from core base classes
3. **Dependency Injection**: Use DI for service and repository dependencies
4. **Cross-App Integration**: Import models from other apps when needed
5. **Validation**: Implement comprehensive validation at all layers
6. **Testing**: Write tests for all components
7. **Documentation**: Add docstrings and help text
8. **Error Handling**: Provide meaningful error messages
9. **Performance**: Use database indexes and query optimization
10. **Security**: Implement proper permissions and validation

### App ViewSet Implementation Examples

#### Basic CRUD ViewSet

```python
# api/viewsets.py
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from apps.core.api.viewsets import ModelViewSet, SearchableViewSet, CacheableViewSet
from apps.core.api.permissions import IsOwner, IsStaff
from apps.core.di.container import DIContainer
from .serializers import BusinessEntitySerializer, BusinessEntityCreateSerializer
from ..models import BusinessEntity
from ..services.interfaces import IBusinessEntityService

class BusinessEntityViewSet(SearchableViewSet, ModelViewSet):
    """ViewSet for BusinessEntity operations with search functionality."""
    
    queryset = BusinessEntity.objects.all()
    serializer_class = BusinessEntitySerializer
    create_serializer_class = BusinessEntityCreateSerializer
    permission_classes = [IsOwner | IsStaff]
    search_fields = ['name', 'code', 'description']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service: IBusinessEntityService = DIContainer.get('business_entity_service')
    
    def get_queryset(self):
        """Get queryset with proper filtering and optimization."""
        queryset = super().get_queryset().select_related(
            'owner', 'currency', 'primary_address'
        ).prefetch_related('managers', 'attachments')
        
        # Filter by user permissions
        if not self.request.user.is_staff:
            queryset = queryset.filter(
                models.Q(owner=self.request.user) | 
                models.Q(managers=self.request.user)
            ).distinct()
        
        # Apply query parameter filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        priority_filter = self.request.query_params.get('priority')
        if priority_filter:
            queryset = queryset.filter(priority=priority_filter)
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="Create a new business entity",
        request_body=BusinessEntityCreateSerializer,
        responses={
            201: BusinessEntitySerializer,
            400: 'Bad Request'
        }
    )
    def create(self, request, *args, **kwargs):
        """Create new business entity using service layer."""
        serializer = self.get_create_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Use service for business logic
        result = self.service.create_entity({
            **serializer.validated_data,
            'owner': request.user
        })
        
        instance = BusinessEntity.objects.get(id=result['id'])
        response_serializer = self.get_serializer(instance)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        operation_description="Assign manager to business entity",
        request_body=serializers.Serializer,  # Define proper serializer
        responses={200: BusinessEntitySerializer}
    )
    def assign_manager(self, request, pk=None):
        """Assign a manager to the business entity."""
        entity = self.get_object()
        manager_id = request.data.get('manager_id')
        
        if not manager_id:
            return Response(
                {'error': 'manager_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        result = self.service.assign_manager({
            'entity_id': str(entity.id),
            'manager_id': manager_id,
            'assigned_by': request.user.id
        })
        
        entity.refresh_from_db()
        serializer = self.get_serializer(entity)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def my_entities(self, request):
        """Get entities owned or managed by current user."""
        entities = self.service.get_user_entities(request.user.id)
        
        page = self.paginate_queryset(entities)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(entities, many=True)
        return Response(serializer.data)
```

#### Read-Only ViewSet with Caching

```python
class BusinessEntityCategoryViewSet(CacheableViewSet, ReadOnlyViewSet):
    """Read-only ViewSet for business entity categories with caching."""
    
    queryset = BusinessEntityCategory.objects.filter(is_active=True)
    serializer_class = BusinessEntityCategorySerializer
    permission_classes = [ReadOnly]
    cache_timeout = 3600  # 1 hour cache
    
    def get_queryset(self):
        """Get active categories ordered by name."""
        return super().get_queryset().order_by('name')
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular categories based on usage."""
        cache_key = 'popular_categories'
        cached_data = cache.get(cache_key)
        
        if cached_data is not None:
            return Response(cached_data)
        
        # Get categories with entity count
        categories = self.get_queryset().annotate(
            entity_count=models.Count('business_entities')
        ).filter(entity_count__gt=0).order_by('-entity_count')[:10]
        
        serializer = self.get_serializer(categories, many=True)
        cache.set(cache_key, serializer.data, self.cache_timeout)
        
        return Response(serializer.data)
```

#### Nested Resource ViewSet

```python
class BusinessEntityAttachmentViewSet(ModelViewSet):
    """ViewSet for managing business entity attachments."""
    
    serializer_class = BusinessEntityAttachmentSerializer
    permission_classes = [IsOwner | IsStaff]
    
    def get_queryset(self):
        """Get attachments for specific business entity."""
        entity_id = self.kwargs.get('entity_pk')
        return BusinessEntityAttachment.objects.filter(
            entity_id=entity_id
        ).select_related('entity', 'file')
    
    def perform_create(self, serializer):
        """Create attachment for specific entity."""
        entity_id = self.kwargs.get('entity_pk')
        entity = BusinessEntity.objects.get(id=entity_id)
        
        # Check permissions
        if not (entity.owner == self.request.user or 
                self.request.user in entity.managers.all() or
                self.request.user.is_staff):
            raise PermissionDenied("You don't have permission to add attachments to this entity")
        
        serializer.save(
            entity=entity,
            uploaded_by=self.request.user
        )
```

### ViewSet Registration and URL Patterns

```python
# api/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .viewsets import (
    BusinessEntityViewSet,
    BusinessEntityCategoryViewSet,
    BusinessEntityAttachmentViewSet
)

app_name = 'your_app'

# Main router
router = DefaultRouter()
router.register(r'entities', BusinessEntityViewSet, basename='entity')
router.register(r'categories', BusinessEntityCategoryViewSet, basename='category')

# Nested router for attachments
entities_router = routers.NestedDefaultRouter(router, r'entities', lookup='entity')
entities_router.register(r'attachments', BusinessEntityAttachmentViewSet, basename='entity-attachments')

urlpatterns = [
    path('api/v1/', include(router.urls)),
    path('api/v1/', include(entities_router.urls)),
]
```

### ViewSet Best Practices

1. **Inherit from appropriate base classes**: Choose the right combination of base ViewSets
2. **Use dependency injection**: Inject services through constructor or decorators
3. **Implement proper permissions**: Use role-based permissions and object-level permissions
4. **Optimize querysets**: Use select_related and prefetch_related for performance
5. **Add custom actions**: Implement business-specific endpoints using @action decorator
6. **Use proper serializers**: Different serializers for create, update, and read operations
7. **Handle errors gracefully**: Provide meaningful error responses
8. **Add API documentation**: Use swagger_auto_schema for comprehensive documentation
9. **Implement caching**: Use CacheableViewSet for frequently accessed read-only data
10. **Filter and search**: Implement proper filtering and search functionality
11. **Pagination**: Use appropriate pagination for large datasets
12. **Validation**: Implement proper request validation in serializers
13. **Audit trails**: Leverage built-in audit functionality from base classes
14. **Cross-app integration**: Properly handle relationships with other app models
15. **Testing**: Write comprehensive tests for all ViewSet methods and custom actions

### Advanced ViewSet Patterns

#### Multi-Model ViewSet

```python
class BusinessDashboardViewSet(BaseViewSet):
    """ViewSet for business dashboard data aggregation."""
    
    permission_classes = [IsStaff]
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get business summary data."""
        service = DIContainer.get('business_dashboard_service')
        summary_data = service.get_dashboard_summary(request.user)
        
        return Response(summary_data)
    
    @action(detail=False, methods=['get'])
    def metrics(self, request):
        """Get business metrics."""
        date_range = request.query_params.get('range', '30d')
        service = DIContainer.get('business_metrics_service')
        metrics = service.get_metrics(request.user, date_range)
        
        return Response(metrics)
```

#### Bulk Operations ViewSet

```python
class BusinessEntityBulkViewSet(BaseViewSet):
    """ViewSet for bulk operations on business entities."""
    
    permission_classes = [IsStaff]
    
    @action(detail=False, methods=['post'])
    def bulk_update_status(self, request):
        """Bulk update entity status."""
        entity_ids = request.data.get('entity_ids', [])
        new_status = request.data.get('status')
        
        if not entity_ids or not new_status:
            return Response(
                {'error': 'entity_ids and status are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        service = DIContainer.get('business_entity_service')
        result = service.bulk_update_status(entity_ids, new_status, request.user)
        
        return Response({
            'updated_count': result['updated_count'],
            'message': f'Successfully updated {result["updated_count"]} entities'
        })
```

This comprehensive ViewSet implementation ensures consistency, maintainability, and leverages all the powerful features provided by PIN's core API infrastructure.
        queryset = repository.get_all()
        
        # Apply filters
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = repository.get_by_status(status_filter)
        
        return queryset
    
    @swagger_auto_schema(
        operation_description="Create a new entity",
        request_body=YourModelCreateSerializer,
        responses={
            201: YourModelSerializer,
            400: 'Bad Request'
        }
    )
    def create(self, request, *args, **kwargs):
        """Create new entity."""
        serializer = self.get_create_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        instance = serializer.save()
        response_serializer = self.get_serializer(instance)
        
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'])
    @swagger_auto_schema(
        operation_description="Process entity with custom logic",
        responses={200: YourModelSerializer}
    )
    def process(self, request, pk=None):
        """Custom action to process entity."""
        instance = self.get_object()
        
        # Use service for business logic
        result = self.service.process_entity({
            'id': str(instance.id),
            'action': 'process'
        })
        
        # Refresh instance
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        
        return Response(serializer.data)
```

## 🛣️ URLs

Structure URLs properly:

```python
# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api.viewsets import YourModelViewSet

app_name = 'your_app'

# API URLs
router = DefaultRouter()
router.register(r'your-models', YourModelViewSet, basename='your-model')

urlpatterns = [
    path('api/', include(router.urls)),
]
```

## 🧪 Tests

Write comprehensive tests for all components:

```python
# tests/test_services.py
from django.test import TestCase
from unittest.mock import Mock, patch
from ..services.implementations import YourAppService
from ..repositories.interfaces import YourAppRepositoryInterface

class YourAppServiceTest(TestCase):
    """Test cases for YourAppService."""
    
    def setUp(self):
        self.mock_repository = Mock(spec=YourAppRepositoryInterface)
        self.service = YourAppService()
        self.service.repository = self.mock_repository
    
    def test_process_entity_success(self):
        """Test successful entity processing."""
        # Arrange
        entity_data = {'name': 'Test Entity', 'type': 'test'}
        mock_entity = Mock()
        mock_entity.id = 'test-id'
        self.mock_repository.create.return_value = mock_entity
        
        # Act
        result = self.service.process_entity(entity_data)
        
        # Assert
        self.assertEqual(result['id'], 'test-id')
        self.assertEqual(result['status'], 'processed')
        self.mock_repository.create.assert_called_once()
    
    def test_validate_entity_missing_fields(self):
        """Test validation with missing required fields."""
        # Arrange
        entity_data = {'name': 'Test Entity'}  # Missing 'type'
        
        # Act & Assert
        self.assertFalse(self.service.validate_entity(entity_data))
```

## 📚 Documentation

Document your app thoroughly:

```python
# Create docs/apps/your_app.md
```

## ✅ Best Practices

### 1. Dependency Injection

Register your services and repositories in the DI container:

```python
# apps.py
from django.apps import AppConfig
from apps.core.di.container import DIContainer

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.your_app'
    
    def ready(self):
        # Register dependencies
        from .repositories.implementations import YourAppRepository
        from .services.implementations import YourAppService
        
        DIContainer.register('your_app_repository', YourAppRepository())
        DIContainer.register('your_app_service', YourAppService())
```

### 2. Error Handling

Implement proper error handling:

```python
from apps.core.exceptions import BusinessLogicError

class YourAppService:
    def process_entity(self, entity_data):
        try:
            # Business logic here
            pass
        except ValueError as e:
            raise BusinessLogicError(f"Invalid data: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise BusinessLogicError("Processing failed")
```

### 3. Logging

Use structured logging:

```python
import logging

logger = logging.getLogger(__name__)

class YourAppService:
    def process_entity(self, entity_data):
        logger.info(
            "Processing entity",
            extra={
                'entity_type': entity_data.get('type'),
                'user_id': self.get_current_user_id()
            }
        )
```

### 4. Performance

- Use `select_related()` and `prefetch_related()` for database optimization
- Implement caching where appropriate
- Use database indexes for frequently queried fields
- Implement pagination for list views

### 5. Security

- Validate all input data
- Use proper permissions and authentication
- Sanitize data before database operations
- Follow OWASP guidelines

### 6. Field Transformers

- **Create mapper.py files** in each app to define field mappings
- **Use auto-discovery** by calling `auto_discover_transformers()` in app configuration
- **Integrate with services** to handle automatic field transformation
- **Test transformations** thoroughly with both directions (model-to-API and API-to-model)
- **Document custom transformers** with clear business logic explanations
- **Cache transformer instances** to avoid repeated instantiation
- **Use consistent naming** conventions across all field mappings

## 🔄 Complete App Lifecycle

This section outlines the complete lifecycle of creating a new app in PIN, following the "No Broken Windows" policy - ensuring every step maintains code quality and system integrity.

### Phase 1: Planning and Design

#### 1.1 Requirements Analysis
```python
# Create a requirements document: docs/apps/your_app/requirements.md
"""
# Your App Requirements

## Business Requirements
- [ ] Define core business functionality
- [ ] Identify user personas and use cases
- [ ] Define success metrics

## Technical Requirements
- [ ] Database schema design (3NF)
- [ ] API endpoints specification
- [ ] Integration points with other apps
- [ ] Performance requirements
- [ ] Security considerations

## Dependencies
- [ ] Core app dependencies (BaseModel, BaseService, etc.)
- [ ] Cross-app dependencies (User, Contact, Media, etc.)
- [ ] External service dependencies
"""
```

#### 1.2 Database Design
```python
# Create database design document: docs/apps/your_app/database_design.md
"""
# Database Design - Your App

## Entity Relationship Diagram
[Include ERD here]

## Tables

### your_app_yourmodel
- id (UUID, PK)
- name (VARCHAR(255), NOT NULL)
- description (TEXT)
- user_id (UUID, FK to auth_user)
- contact_id (UUID, FK to contact_contact)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
- is_active (BOOLEAN)

## Indexes
- idx_yourmodel_user_id
- idx_yourmodel_created_at
- idx_yourmodel_is_active

## Constraints
- fk_yourmodel_user
- fk_yourmodel_contact
- unique_yourmodel_name_user
"""
```

### Phase 2: Implementation

#### 2.1 App Creation and Structure
```bash
# Step 1: Create the Django app
python manage.py startapp your_app apps/your_app

# Step 2: Create the complete directory structure
mkdir -p apps/your_app/{admin,api,managers,mappers,migrations,repositories,services,strategies,tests}
mkdir -p apps/your_app/api/{serializers,viewsets}
mkdir -p apps/your_app/tests/{unit,integration}
mkdir -p docs/apps/your_app
```

#### 2.2 Core Implementation Checklist
```python
# Implementation checklist - follow this order strictly

CHECKLIST = {
    'models': [
        '✓ Create models inheriting from BaseModel/AuditableModel',
        '✓ Add proper field validations and constraints',
        '✓ Define relationships with proper related_names',
        '✓ Add Meta class with ordering and verbose names',
        '✓ Create custom managers if needed'
    ],
    'repositories': [
        '✓ Create repository interface',
        '✓ Implement repository inheriting from BaseRepository',
        '✓ Add custom query methods',
        '✓ Implement soft delete and filtering logic'
    ],
    'services': [
        '✓ Create service interface',
        '✓ Implement service inheriting from BaseService',
        '✓ Add business logic methods',
        '✓ Integrate with cross-app services via DI',
        '✓ Add proper error handling and logging'
    ],
    'mappers': [
        '✓ Create mapper inheriting from BaseMapper',
        '✓ Define field transformations',
        '✓ Add custom transformation logic',
        '✓ Register auto-discovery in apps.py'
    ],
    'serializers': [
        '✓ Create serializers with cross-app field integration',
        '✓ Add validation logic',
        '✓ Implement create/update methods',
        '✓ Add nested serializers for related objects'
    ],
    'viewsets': [
        '✓ Create viewsets inheriting from BaseViewSet',
        '✓ Add proper permissions and authentication',
        '✓ Implement custom actions if needed',
        '✓ Add filtering and search capabilities'
    ],
    'urls': [
        '✓ Create hierarchical URL patterns',
        '✓ Register with main URL configuration',
        '✓ Add API versioning if needed'
    ]
}
```

#### 2.3 Quality Gates
```python
# Quality gates that must pass before proceeding

QUALITY_GATES = {
    'code_quality': [
        'All code follows PEP 8 standards',
        'No pylint warnings or errors',
        'All imports are properly organized',
        'Docstrings are present for all classes and methods',
        'Type hints are used consistently'
    ],
    'testing': [
        'Unit tests cover all business logic (>90% coverage)',
        'Integration tests cover API endpoints',
        'All tests pass without warnings',
        'Test data is properly isolated',
        'Mock external dependencies appropriately'
    ],
    'security': [
        'All inputs are validated and sanitized',
        'Proper permissions are implemented',
        'No sensitive data in logs or responses',
        'SQL injection prevention is in place',
        'CSRF protection is enabled'
    ],
    'performance': [
        'Database queries are optimized',
        'Proper indexing is implemented',
        'N+1 query problems are avoided',
        'Caching is implemented where appropriate',
        'API response times are acceptable (<200ms)'
    ]
}
```

### Phase 3: Testing and Validation

#### 3.1 Comprehensive Testing Strategy
```python
# tests/test_lifecycle.py
from django.test import TestCase, TransactionTestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from apps.core.tests.base import BaseTestCase

User = get_user_model()

class YourAppLifecycleTest(BaseTestCase):
    """Complete lifecycle testing for your app."""
    
    def setUp(self):
        super().setUp()
        self.user = self.create_test_user()
        self.contact = self.create_test_contact()
    
    def test_complete_crud_lifecycle(self):
        """Test complete CRUD lifecycle."""
        # Create
        entity_data = {
            'name': 'Test Entity',
            'description': 'Test Description',
            'user': self.user,
            'contact': self.contact
        }
        entity = self.service.create(entity_data, self.user)
        self.assertIsNotNone(entity.id)
        
        # Read
        retrieved = self.service.get_by_id(entity.id)
        self.assertEqual(retrieved.name, 'Test Entity')
        
        # Update
        update_data = {'name': 'Updated Entity'}
        updated = self.service.update(entity.id, update_data, self.user)
        self.assertEqual(updated.name, 'Updated Entity')
        
        # Soft Delete
        self.service.delete(entity.id, self.user)
        with self.assertRaises(ObjectDoesNotExist):
            self.service.get_by_id(entity.id)
    
    def test_cross_app_integration(self):
        """Test integration with other apps."""
        # Test user relationship
        entity = self.service.create({
            'name': 'User Entity',
            'user': self.user
        }, self.user)
        self.assertEqual(entity.user, self.user)
        
        # Test contact relationship
        entity_with_contact = self.service.create({
            'name': 'Contact Entity',
            'contact': self.contact
        }, self.user)
        self.assertEqual(entity_with_contact.contact, self.contact)
    
    def test_api_hierarchy(self):
        """Test hierarchical API access."""
        url = f'/api/users/{self.user.id}/your-entities/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # Test nested creation
        create_data = {
            'name': 'Hierarchical Entity',
            'description': 'Created via hierarchy'
        }
        response = self.client.post(url, create_data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user'], str(self.user.id))
```

#### 3.2 Performance Testing
```python
# tests/test_performance.py
from django.test import TestCase
from django.test.utils import override_settings
from django.db import connection
from django.test.utils import override_settings
import time

class PerformanceTest(TestCase):
    """Performance testing for your app."""
    
    def test_query_performance(self):
        """Test database query performance."""
        # Create test data
        self.create_bulk_test_data(1000)
        
        # Test query performance
        start_time = time.time()
        with self.assertNumQueries(1):  # Should use only 1 query
            entities = list(self.service.get_all_active())
        end_time = time.time()
        
        # Assert performance requirements
        self.assertLess(end_time - start_time, 0.1)  # < 100ms
        self.assertEqual(len(entities), 1000)
    
    def test_api_response_time(self):
        """Test API response time."""
        url = '/api/your-entities/'
        
        start_time = time.time()
        response = self.client.get(url)
        end_time = time.time()
        
        self.assertEqual(response.status_code, 200)
        self.assertLess(end_time - start_time, 0.2)  # < 200ms
```

### Phase 4: Documentation and Deployment

#### 4.1 Documentation Requirements
```markdown
# docs/apps/your_app/README.md

# Your App Documentation

## Overview
Brief description of the app's purpose and functionality.

## Models
- YourModel: Description and relationships

## API Endpoints
- GET /api/your-entities/ - List entities
- POST /api/your-entities/ - Create entity
- GET /api/your-entities/{id}/ - Get entity
- PUT /api/your-entities/{id}/ - Update entity
- DELETE /api/your-entities/{id}/ - Delete entity

## Business Logic
Description of key business rules and processes.

## Integration Points
- User management integration
- Contact management integration
- Media file handling

## Configuration
Required settings and environment variables.

## Troubleshooting
Common issues and solutions.
```

#### 4.2 Deployment Checklist
```python
DEPLOYMENT_CHECKLIST = {
    'pre_deployment': [
        '✓ All tests pass in CI/CD pipeline',
        '✓ Code review completed and approved',
        '✓ Database migrations are ready',
        '✓ Environment variables are configured',
        '✓ Documentation is updated',
        '✓ Performance benchmarks are met'
    ],
    'deployment': [
        '✓ Run database migrations',
        '✓ Update static files',
        '✓ Restart application servers',
        '✓ Clear application caches',
        '✓ Verify health checks pass'
    ],
    'post_deployment': [
        '✓ Monitor application logs',
        '✓ Verify API endpoints respond correctly',
        '✓ Check database performance',
        '✓ Validate cross-app integrations',
        '✓ Update monitoring dashboards'
    ]
}
```

### Phase 5: Maintenance and Evolution

#### 5.1 No Broken Windows Policy
```python
# Continuous maintenance checklist

NO_BROKEN_WINDOWS = {
    'daily': [
        'Monitor error logs and fix issues immediately',
        'Review and address any TODO comments',
        'Update dependencies if security patches available',
        'Ensure all new code follows established patterns'
    ],
    'weekly': [
        'Review code quality metrics',
        'Update documentation for any changes',
        'Refactor any code that violates DRY principle',
        'Review and optimize database queries'
    ],
    'monthly': [
        'Conduct security audit',
        'Review and update API documentation',
        'Analyze performance metrics and optimize',
        'Update integration tests for new scenarios'
    ],
    'quarterly': [
        'Major dependency updates',
        'Architecture review and improvements',
        'Performance benchmarking',
        'Security penetration testing'
    ]
}
```

#### 5.2 Evolution Guidelines
```python
# When modifying existing apps

EVOLUTION_RULES = {
    'backward_compatibility': [
        'Never break existing API contracts',
        'Use API versioning for breaking changes',
        'Maintain database migration compatibility',
        'Deprecate features gracefully'
    ],
    'code_quality': [
        'Refactor before adding new features',
        'Maintain or improve test coverage',
        'Update documentation with changes',
        'Follow established architectural patterns'
    ],
    'performance': [
        'Profile before optimizing',
        'Measure impact of changes',
        'Maintain response time SLAs',
        'Monitor resource usage'
    ]
}
```

## 🚀 Getting Started

Follow this streamlined process to create a new app:

1. **Complete Phase 1**: Requirements analysis and database design
2. **Create app structure**: Use the provided commands and checklist
3. **Implement core components**: Follow the implementation order
4. **Pass quality gates**: Ensure all quality requirements are met
5. **Write comprehensive tests**: Unit, integration, and performance tests
6. **Document thoroughly**: API docs, business logic, and troubleshooting
7. **Deploy safely**: Follow the deployment checklist
8. **Maintain continuously**: Apply the "No Broken Windows" policy

## 📖 Additional Resources

- [Django Best Practices](../STYLE_GUIDE.md)
- [API Documentation Guide](../api/README.md)
- [Testing Guidelines](../testing/README.md)
- [Architecture Overview](../architecture/README.md)
- [Field Transformers Documentation](../apps/core/transformers/README.md)
- [Transformer Setup Guide](../apps/core/transformers/setup_guide.md)
- [Transformer Examples](../apps/core/transformers/examples.py)

## Troubleshooting & Broken Windows Prevention

### Common Issues and Solutions

#### 1. Import Errors

**Problem**: `ImportError: cannot import name 'BaseModel' from 'apps.core.models'`

**Solution**:
```python
# ❌ Wrong
from apps.core.models import BaseModel

# ✅ Correct
from apps.core.models.base import BaseModel
```

**Prevention**: Always check the exact import path in the core module's `__init__.py`

#### 2. Circular Import Issues

**Problem**: Circular imports between apps

**Solution**:
```python
# ❌ Wrong - Direct import in models.py
from apps.users.models import User

# ✅ Correct - Use string reference
class BusinessEntity(BaseModel):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE)
    
# ✅ Or import in method when needed
def get_user_entities(self):
    from apps.users.models import User
    return User.objects.filter(business_entities=self)
```

#### 3. Migration Conflicts

**Problem**: Migration dependencies between apps

**Solution**:
```python
# In migration file
class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # Ensure proper dependency order
        ('core', '0001_initial'),
    ]
```

**Prevention**: Always run `python manage.py makemigrations --check` before committing

#### 4. Service Layer Issues

**Problem**: Services not properly injected or configured

**Solution**:
```python
# ❌ Wrong - Direct instantiation
class YourModelViewSet(BaseViewSet):
    def list(self, request):
        service = YourModelService()  # Wrong!
        
# ✅ Correct - Proper injection
class YourModelViewSet(BaseViewSet):
    service_class = YourModelService
    
    def list(self, request):
        service = self.get_service()
```

#### 5. Repository Pattern Violations

**Problem**: Direct ORM usage in services

**Solution**:
```python
# ❌ Wrong - Direct ORM in service
class YourModelService(BaseService):
    def get_active_items(self):
        return YourModel.objects.filter(is_active=True)
        
# ✅ Correct - Use repository
class YourModelService(BaseService):
    def get_active_items(self):
        return self.repository.get_active()
```

### Broken Windows Prevention

#### Code Quality Checklist

**Before Every Commit:**
- [ ] All imports follow the established patterns
- [ ] Services inherit from `BaseService`
- [ ] ViewSets inherit from appropriate base classes
- [ ] Models inherit from `BaseModel` or `AuditableModel`
- [ ] Repositories implement proper interfaces
- [ ] Tests are written and passing
- [ ] No direct ORM usage in services
- [ ] Proper dependency injection is used

#### Architecture Violations to Avoid

1. **Skipping the Service Layer**
   ```python
   # ❌ Wrong - Direct repository usage in ViewSet
   class YourModelViewSet(BaseViewSet):
       def create(self, request):
           repository = YourModelRepository()
           return repository.create(request.data)
   
   # ✅ Correct - Use service layer
   class YourModelViewSet(BaseViewSet):
       def create(self, request):
           service = self.get_service()
           return service.create(request.data)
   ```

2. **Bypassing Serializers**
   ```python
   # ❌ Wrong - Direct data manipulation
   def create(self, request):
       data = request.data
       instance = YourModel.objects.create(**data)
   
   # ✅ Correct - Use serializers
   def create(self, request):
       serializer = self.get_serializer(data=request.data)
       serializer.is_valid(raise_exception=True)
       return self.perform_create(serializer)
   ```

3. **Inconsistent Error Handling**
   ```python
   # ❌ Wrong - Inconsistent error responses
   try:
       result = self.service.process(data)
   except Exception as e:
       return Response({'error': str(e)}, status=400)
   
   # ✅ Correct - Use base class error handling
   try:
       result = self.service.process(data)
   except ValidationError as e:
       return self.handle_validation_error(e)
   except ServiceError as e:
       return self.handle_service_error(e)
   ```

#### Performance Anti-Patterns

1. **N+1 Query Problems**
   ```python
   # ❌ Wrong - Causes N+1 queries
   def get_entities_with_owners(self):
       entities = BusinessEntity.objects.all()
       return [(e, e.owner.username) for e in entities]
   
   # ✅ Correct - Use select_related
   def get_entities_with_owners(self):
       entities = BusinessEntity.objects.select_related('owner').all()
       return [(e, e.owner.username) for e in entities]
   ```

2. **Missing Database Indexes**
   ```python
   # ✅ Always add indexes for frequently queried fields
   class YourModel(BaseModel):
       status = models.CharField(max_length=20, db_index=True)
       created_by = models.ForeignKey(User, on_delete=models.CASCADE, db_index=True)
       
       class Meta:
           indexes = [
               models.Index(fields=['status', 'created_at']),
               models.Index(fields=['created_by', 'status']),
           ]
   ```

#### Security Checklist

- [ ] No sensitive data in logs
- [ ] Proper permission classes on ViewSets
- [ ] Input validation in serializers
- [ ] SQL injection prevention (use ORM)
- [ ] CSRF protection enabled
- [ ] Proper authentication on all endpoints

#### Monitoring and Debugging

**Enable Debug Logging:**
```python
# settings/development.py
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'apps': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

**Common Debug Commands:**
```bash
# Check for migration issues
python manage.py makemigrations --dry-run
python manage.py migrate --plan

# Validate models
python manage.py check

# Test specific app
python manage.py test apps.your_app

# Check for unused imports
flake8 --select=F401 apps/
```

### Emergency Fixes

#### Quick Rollback Procedures

1. **Database Migration Rollback**
   ```bash
   python manage.py migrate your_app 0001  # Rollback to specific migration
   ```

2. **Service Downtime Recovery**
   ```bash
   # Check service status
   python manage.py check --deploy
   
   # Restart with safe defaults
   python manage.py runserver --settings=settings.production
   ```

3. **Cache Issues**
   ```bash
   # Clear all cache
   python manage.py shell -c "from django.core.cache import cache; cache.clear()"
   ```

---

**Remember**: Consistency is key. Follow these patterns religiously to maintain code quality and team productivity.