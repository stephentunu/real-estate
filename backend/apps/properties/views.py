from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from apps.properties.models import Favorite


from .models import Property, PropertyType, PropertyStatus, PropertyImage, PropertyFeature, SavedProperty, Amenity, PropertyAmenity
from .serializers import (
    PropertyListSerializer,
    PropertyDetailSerializer,
    PropertyCreateUpdateSerializer,
    PropertyTypeSerializer,
    PropertyStatusSerializer,
    PropertyImageSerializer,
    PropertyFeatureSerializer,
    SavedPropertySerializer,
    AmenitySerializer,
    PropertyAmenitySerializer
)

User = get_user_model()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        elif hasattr(obj, 'property'):
            return obj.property.owner == request.user
        elif hasattr(obj, 'reviewer'):
            return obj.reviewer == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        
        return False


class PropertyTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for PropertyType model
    Provides read-only access to property types
    """
    queryset = PropertyType.objects.filter(is_active=True)
    serializer_class = PropertyTypeSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class PropertyStatusViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for PropertyStatus model
    Provides read-only access to property statuses
    """
    queryset = PropertyStatus.objects.filter(is_active=True)
    serializer_class = PropertyStatusSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class PropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Property model
    Handles CRUD operations for properties with filtering and search
    """
    queryset = Property.objects.select_related('owner', 'property_type', 'status').prefetch_related(
        'images', 'feature_assignments__feature'
    )
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'description', 'city', 'state', 'country']
    ordering_fields = ['sale_price', 'rent_price', 'created_at', 'bedrooms', 'bathrooms', 'square_feet']
    ordering = ['-created_at']
    parser_classes = [MultiPartParser, FormParser]
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return PropertyListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return PropertyCreateUpdateSerializer
        return PropertyDetailSerializer
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        queryset = super().get_queryset()
        
        # Filter by availability for non-owners - only show published properties with available status
        if self.action == 'list' and not self.request.user.is_staff:
            queryset = queryset.filter(is_published=True, status__name='Available')
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set owner to current user when creating property
        """
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_favorite(self, request, pk=None):
        """
        Toggle favorite status for a property
        """
        property_obj = self.get_object()
        favorite, created = Favorite.objects.get_or_create(
            user=request.user,
            property=property_obj
        )
        
        if not created:
            favorite.delete()
            return Response(
                {'message': 'Property removed from favorites', 'is_favorited': False},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {'message': 'Property added to favorites', 'is_favorited': True},
            status=status.HTTP_201_CREATED
        )
    

    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def upload_images(self, request, pk=None):
        """
        Upload images for a property
        """
        property_obj = self.get_object()
        
        # Check if user is the owner
        if property_obj.owner != request.user:
            return Response(
                {'error': 'You can only upload images to your own properties'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        images_data = request.FILES.getlist('images')
        if not images_data:
            return Response(
                {'error': 'No images provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        created_images = []
        for image_data in images_data:
            image_serializer = PropertyImageSerializer(data={
                'image': image_data,
                'caption': request.data.get('caption', ''),
                'is_primary': request.data.get('is_primary', False)
            })
            
            if image_serializer.is_valid():
                image_serializer.save(property=property_obj)
                created_images.append(image_serializer.data)
        
        return Response(
            {'message': f'{len(created_images)} images uploaded successfully', 'images': created_images},
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_properties(self, request):
        """
        Get current user's properties
        """
        queryset = self.get_queryset().filter(owner=request.user)
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = PropertyListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PropertyListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def favorites(self, request):
        """
        Get current user's favorite properties
        """
        favorites = Favorite.objects.filter(user=request.user).select_related('property')
        properties = [favorite.property for favorite in favorites]
        
        page = self.paginate_queryset(properties)
        if page is not None:
            serializer = PropertyListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = PropertyListSerializer(properties, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """
        Get featured properties
        """
        #block commented out temporarily for debugging. uncomment when needed.
        #try:
        limit = request.query_params.get('limit', None)
        queryset = self.get_queryset().filter(is_featured=True)
            
        if limit:
                try:
                    limit = int(limit)
                    queryset = queryset[:limit]
                except ValueError:
                    pass
            
        serializer = PropertyListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)
        #except Exception as e:
            #return Response(
                #{'error': f'Failed to fetch featured properties: {str(e)}'}, 
                #status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    


class PropertyImageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PropertyImage model
    Handles CRUD operations for property images
    """
    queryset = PropertyImage.objects.select_related('property')
    serializer_class = PropertyImageSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """
        Filter images by property if property_id is provided
        """
        queryset = super().get_queryset()
        property_id = self.request.query_params.get('property_id')
        
        if property_id:
            queryset = queryset.filter(property_id=property_id)
        
        return queryset
    
    def perform_create(self, serializer):
        """
        Set property when creating image
        """
        property_id = self.request.data.get('property_id')
        if property_id:
            property_obj = get_object_or_404(Property, id=property_id, owner=self.request.user)
            serializer.save(property=property_obj)
        else:
            serializer.save()


class PropertyFeatureViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PropertyFeature model
    Handles CRUD operations for property features
    """
    queryset = PropertyFeature.objects.all()
    serializer_class = PropertyFeatureSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name']
    ordering = ['name']


class AmenityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Amenity model
    Handles CRUD operations for property amenities
    """
    queryset = Amenity.objects.all()
    serializer_class = AmenitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description', 'category']
    ordering_fields = ['name', 'category', 'created_at']
    ordering = ['name']
    filterset_fields = ['category', 'is_active']
    
    def get_queryset(self):
        """
        Filter queryset based on visibility and soft delete
        """
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        return queryset
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        Get only active amenities
        """
        queryset = self.get_queryset().filter(is_active=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def categories(self, request):
        """
        Get unique amenity categories
        """
        categories = self.get_queryset().values_list('category', flat=True).distinct()
        categories = [cat for cat in categories if cat]  # Filter out empty categories
        return Response({'categories': categories})


class PropertyAmenityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for PropertyAmenity model
    Handles property-amenity relationships
    """
    queryset = PropertyAmenity.objects.select_related('property', 'amenity')
    serializer_class = PropertyAmenitySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    ordering_fields = ['created_at', 'amenity__name']
    ordering = ['amenity__name']
    filterset_fields = ['property', 'amenity', 'amenity__category']
    
    def get_queryset(self):
        """
        Filter queryset based on user permissions
        """
        queryset = super().get_queryset()
        if not self.request.user.is_staff:
            queryset = queryset.filter(property__is_published=True)
        return queryset


class SavedPropertyViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SavedProperty model
    Handles user saved properties
    """
    queryset = SavedProperty.objects.all()
    serializer_class = SavedPropertySerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return only current user's saved properties
        """
        if self.request.user.is_authenticated:
            return SavedProperty.objects.filter(user=self.request.user)
        return SavedProperty.objects.none()
    
    def perform_create(self, serializer):
        """
        Set the user as the current user
        """
        serializer.save(user=self.request.user)
