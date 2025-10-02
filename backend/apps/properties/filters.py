import django_filters
from django.db.models import Q
from .models import Property, PropertyFeature, PropertyType


class PropertyFilter(django_filters.FilterSet):
    """
    Filter class for Property model
    Provides advanced filtering capabilities for property searches
    """
    
    # Price range filters for sale
    min_sale_price = django_filters.NumberFilter(
        field_name='sale_price',
        lookup_expr='gte',
        help_text='Minimum sale price'
    )
    max_sale_price = django_filters.NumberFilter(
        field_name='sale_price',
        lookup_expr='lte',
        help_text='Maximum sale price'
    )
    
    # Price range filters for rent
    min_rent_price = django_filters.NumberFilter(
        field_name='rent_price',
        lookup_expr='gte',
        help_text='Minimum rent price'
    )
    max_rent_price = django_filters.NumberFilter(
        field_name='rent_price',
        lookup_expr='lte',
        help_text='Maximum rent price'
    )
    
    # Area range filters
    min_square_feet = django_filters.NumberFilter(
        field_name='square_feet',
        lookup_expr='gte',
        help_text='Minimum square feet'
    )
    max_square_feet = django_filters.NumberFilter(
        field_name='square_feet',
        lookup_expr='lte',
        help_text='Maximum square feet'
    )
    
    # Lot size filters
    min_lot_size = django_filters.NumberFilter(
        field_name='lot_size',
        lookup_expr='gte',
        help_text='Minimum lot size in acres'
    )
    max_lot_size = django_filters.NumberFilter(
        field_name='lot_size',
        lookup_expr='lte',
        help_text='Maximum lot size in acres'
    )
    
    # Bedroom and bathroom filters
    min_bedrooms = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='gte')
    max_bedrooms = django_filters.NumberFilter(field_name='bedrooms', lookup_expr='lte')
    min_bathrooms = django_filters.NumberFilter(field_name='bathrooms', lookup_expr='gte')
    max_bathrooms = django_filters.NumberFilter(field_name='bathrooms', lookup_expr='lte')
    
    # Location filters
    city = django_filters.CharFilter(field_name='city', lookup_expr='icontains')
    state = django_filters.CharFilter(field_name='state', lookup_expr='icontains')
    country = django_filters.CharFilter(field_name='country', lookup_expr='icontains')
    location = django_filters.CharFilter(method='filter_location')
    
    # Property type and status filters
    property_type = django_filters.ModelChoiceFilter(
        queryset=PropertyType.objects.filter(is_active=True),
        help_text='Property type'
    )
    
    # Listing type filter
    listing_type = django_filters.ChoiceFilter(
        choices=Property.ListingType.choices,
        help_text='Listing type (sale, rent, both)'
    )
    
    # Boolean feature filters
    has_garage = django_filters.BooleanFilter(field_name='has_garage')
    has_pool = django_filters.BooleanFilter(field_name='has_pool')
    has_garden = django_filters.BooleanFilter(field_name='has_garden')
    is_furnished = django_filters.BooleanFilter(field_name='is_furnished')
    
    # Availability filters
    is_published = django_filters.BooleanFilter(field_name='is_published')
    is_featured = django_filters.BooleanFilter(field_name='is_featured')
    is_available = django_filters.BooleanFilter(method='filter_is_available')
    
    # Features filter
    features = django_filters.ModelMultipleChoiceFilter(
        queryset=PropertyFeature.objects.filter(is_active=True),
        field_name='features',
        to_field_name='id',
        conjoined=False,  # OR logic (property has any of the selected features)
        help_text='Filter by features (comma-separated IDs)'
    )
    
    # Date filters
    available_from = django_filters.DateFilter(field_name='availability_date', lookup_expr='gte')
    available_until = django_filters.DateFilter(field_name='availability_date', lookup_expr='lte')
    
    # Year built filter
    min_year_built = django_filters.NumberFilter(field_name='year_built', lookup_expr='gte')
    max_year_built = django_filters.NumberFilter(field_name='year_built', lookup_expr='lte')
    
    # Parking spaces filter
    min_parking = django_filters.NumberFilter(field_name='parking_spaces', lookup_expr='gte')
    
    # Floor filters
    min_floor = django_filters.NumberFilter(field_name='floor_number', lookup_expr='gte')
    max_floor = django_filters.NumberFilter(field_name='floor_number', lookup_expr='lte')
    
    # Currency filter
    currency = django_filters.ChoiceFilter(
        choices=Property.CURRENCY_CHOICES,
        field_name='currency'
    )
    
    # Area unit filter
    area_unit = django_filters.ChoiceFilter(
        choices=Property.AREA_UNIT_CHOICES,
        field_name='area_unit'
    )
    
    # Owner filter (for admin purposes)
    owner = django_filters.ModelChoiceFilter(
        queryset=None,  # Will be set in __init__
        field_name='owner'
    )
    
    # Search filter for multiple fields
    search = django_filters.CharFilter(method='filter_search')
    
    class Meta:
        model = Property
        fields = {
            'sale_price': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'rent_price': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'square_feet': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'lot_size': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'bedrooms': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'bathrooms': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'year_built': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'parking_spaces': ['exact', 'lt', 'lte', 'gt', 'gte'],
            'property_type': ['exact'],
            'listing_type': ['exact'],
            'has_garage': ['exact'],
            'has_pool': ['exact'],
            'has_garden': ['exact'],
            'is_furnished': ['exact'],
            'is_published': ['exact'],
            'is_featured': ['exact'],
            'city': ['exact', 'icontains'],
            'state': ['exact', 'icontains'],
            'country': ['exact', 'icontains'],
            'currency': ['exact'],
            'owner': ['exact'],
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set owner queryset dynamically
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.filters['owner'].queryset = User.objects.filter(properties__isnull=False).distinct()
    
    def filter_location(self, queryset, name, value):
        """
        Filter by location (searches in location, city, state, country)
        """
        if value:
            return queryset.filter(
                Q(location__icontains=value) |
                Q(city__icontains=value) |
                Q(state__icontains=value) |
                Q(country__icontains=value)
            )
        return queryset
    
    def filter_is_available(self, queryset, name, value):
        """
        Filter by availability status
        """
        if value:
            return queryset.filter(status__name='Available')
        return queryset
    
    def filter_search(self, queryset, name, value):
        """
        Global search filter across multiple fields
        """
        if value:
            return queryset.filter(
                Q(title__icontains=value) |
                Q(description__icontains=value) |
                Q(location__icontains=value) |
                Q(city__icontains=value) |
                Q(state__icontains=value) |
                Q(country__icontains=value) |
                Q(owner__first_name__icontains=value) |
                Q(owner__last_name__icontains=value) |
                Q(amenities__name__icontains=value)
            ).distinct()
        return queryset
    
    @property
    def qs(self):
        """
        Override queryset to add custom ordering and optimizations
        """
        parent = super().qs
        
        # Add custom ordering based on query parameters
        order_by = self.request.GET.get('ordering', '-created_at')
        
        # Handle special ordering cases
        if order_by == 'price_asc':
            parent = parent.order_by('price')
        elif order_by == 'price_desc':
            parent = parent.order_by('-price')
        elif order_by == 'newest':
            parent = parent.order_by('-created_at')
        elif order_by == 'oldest':
            parent = parent.order_by('created_at')
        elif order_by == 'rating':
            parent = parent.order_by('-average_rating')
        elif order_by == 'area_asc':
            parent = parent.order_by('area')
        elif order_by == 'area_desc':
            parent = parent.order_by('-area')
        
        return parent