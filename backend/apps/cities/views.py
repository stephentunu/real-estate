from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache

from .models import Country, State, City
from .serializers import (
    CountrySerializer, CountryListSerializer,
    StateSerializer, StateListSerializer,
    CitySerializer, CityListSerializer, CityDetailSerializer,
    CityCreateUpdateSerializer, CityStatsSerializer,
    CountryStatsSerializer, StateStatsSerializer
)


class CountryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing countries
    """
    
    queryset = Country.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['continent', 'is_active']
    search_fields = ['name', 'code', 'currency_code']
    ordering_fields = ['name', 'code', 'created_at']
    ordering = ['name']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return CountryListSerializer
        return CountrySerializer
    
    def get_queryset(self):
        """Filter queryset based on visibility and deletion status"""
        queryset = super().get_queryset()
        return queryset.filter(
            visibility_level='public',
            is_deleted=False
        ).annotate(
            state_count=Count('states', filter=Q(states__visibility_level='public', states__is_deleted=False)),
            city_count=Count('states__cities', filter=Q(
                states__cities__visibility_level='public',
                states__cities__is_deleted=False
            ))
        )
    
    def perform_create(self, serializer):
        """Set created_by when creating"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating"""
        serializer.save(updated_by=self.request.user)
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get country statistics"""
        cache_key = 'country_stats'
        stats = cache.get(cache_key)
        
        if not stats:
            countries = Country.objects.filter(is_visible=True, is_deleted=False)
            
            stats = {
                'total_countries': countries.count(),
                'active_countries': countries.filter(is_active=True).count(),
                'countries_by_continent': dict(
                    countries.values('continent').annotate(
                        count=Count('id')
                    ).values_list('continent', 'count')
                ),
                'top_countries_by_cities': list(
                    countries.annotate(
                        city_count=Count('states__cities', filter=Q(
                            states__cities__is_visible=True,
                            states__cities__is_deleted=False
                        ))
                    ).order_by('-city_count')[:10].values(
                        'name', 'code', 'city_count'
                    )
                ),
                'top_countries_by_properties': []  # Would be implemented with Property model
            }
            
            cache.set(cache_key, stats, 60 * 30)  # Cache for 30 minutes
        
        serializer = CountryStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def states(self, request, slug=None):
        """Get states for a specific country"""
        country = self.get_object()
        states = country.states.filter(
            is_visible=True,
            is_deleted=False
        ).annotate(
            city_count=Count('cities', filter=Q(
                cities__is_visible=True,
                cities__is_deleted=False
            ))
        )
        
        serializer = StateListSerializer(states, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cities(self, request, slug=None):
        """Get cities for a specific country"""
        country = self.get_object()
        cities = City.objects.filter(
            state__country=country,
            is_visible=True,
            is_deleted=False
        ).select_related('state')
        
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data)


class StateViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing states/provinces
    """
    
    queryset = State.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['country', 'type', 'is_active']
    search_fields = ['name', 'code']
    ordering_fields = ['name', 'country__name', 'created_at']
    ordering = ['country__name', 'name']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return StateListSerializer
        return StateSerializer
    
    def get_queryset(self):
        """Filter queryset based on visibility and deletion status"""
        queryset = super().get_queryset()
        return queryset.filter(
            visibility_level='public',
            is_deleted=False,
            country__visibility_level='public',
            country__is_deleted=False
        ).select_related('country').annotate(
            city_count=Count('cities', filter=Q(
                cities__visibility_level='public',
                cities__is_deleted=False
            ))
        )
    
    def perform_create(self, serializer):
        """Set created_by when creating"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating"""
        serializer.save(updated_by=self.request.user)
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get state statistics"""
        cache_key = 'state_stats'
        stats = cache.get(cache_key)
        
        if not stats:
            states = State.objects.filter(
                visibility_level='public',
                is_deleted=False,
                country__visibility_level='public',
                country__is_deleted=False
            )
            
            stats = {
                'total_states': states.count(),
                'active_states': states.filter(is_active=True).count(),
                'states_by_type': dict(
                    states.values('type').annotate(
                        count=Count('id')
                    ).values_list('type', 'count')
                ),
                'top_states_by_cities': list(
                    states.annotate(
                        city_count=Count('cities', filter=Q(
                            cities__visibility_level='public',
                            cities__is_deleted=False
                        ))
                    ).order_by('-city_count')[:10].values(
                        'name', 'country__name', 'city_count'
                    )
                ),
                'top_states_by_properties': []  # Would be implemented with Property model
            }
            
            cache.set(cache_key, stats, 60 * 30)  # Cache for 30 minutes
        
        serializer = StateStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def cities(self, request, slug=None):
        """Get cities for a specific state"""
        state = self.get_object()
        cities = state.cities.filter(
            visibility_level='public',
            is_deleted=False
        )
        
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data)


class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing cities
    """
    
    queryset = City.objects.all()
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'state', 'state__country', 'is_capital', 'is_major', 'is_active'
    ]
    search_fields = ['name', 'description', 'state__name', 'state__country__name']
    ordering_fields = ['name', 'population', 'area_km2', 'created_at']
    ordering = ['state__country__name', 'state__name', 'name']
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return CityListSerializer
        elif self.action == 'retrieve':
            return CityDetailSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return CityCreateUpdateSerializer
        return CitySerializer
    
    def get_queryset(self):
        """Filter queryset based on visibility and deletion status"""
        queryset = super().get_queryset()
        return queryset.filter(
            visibility_level='public',
            is_deleted=False,
            state__visibility_level='public',
            state__is_deleted=False,
            state__country__visibility_level='public',
            state__country__is_deleted=False
        ).select_related('state', 'state__country')
    
    def perform_create(self, serializer):
        """Set created_by when creating"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set updated_by when updating"""
        serializer.save(updated_by=self.request.user)
    
    @method_decorator(cache_page(60 * 15))  # Cache for 15 minutes
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get city statistics"""
        cache_key = 'city_stats'
        stats = cache.get(cache_key)
        
        if not stats:
            cities = City.objects.filter(
                visibility_level='public',
                is_deleted=False,
                state__visibility_level='public',
                state__is_deleted=False,
                state__country__visibility_level='public',
                state__country__is_deleted=False
            )
            
            stats = {
                'total_cities': cities.count(),
                'active_cities': cities.filter(is_active=True).count(),
                'major_cities': cities.filter(is_major=True).count(),
                'capital_cities': cities.filter(is_capital=True).count(),
                'cities_by_country': dict(
                    cities.values('state__country__name').annotate(
                        count=Count('id')
                    ).values_list('state__country__name', 'count')
                ),
                'cities_by_state': dict(
                    cities.values('state__name').annotate(
                        count=Count('id')
                    ).values_list('state__name', 'count')
                ),
                'top_cities_by_properties': []  # Would be implemented with Property model
            }
            
            cache.set(cache_key, stats, 60 * 30)  # Cache for 30 minutes
        
        serializer = CityStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured cities (major cities)"""
        cities = self.get_queryset().filter(
            is_major=True,
            is_active=True
        )[:20]  # Limit to 20 featured cities
        
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def capitals(self, request):
        """Get capital cities"""
        cities = self.get_queryset().filter(
            is_capital=True,
            is_active=True
        )
        
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def nearby(self, request, slug=None):
        """Get nearby cities"""
        city = self.get_object()
        radius = request.query_params.get('radius', 100)
        
        try:
            radius = int(radius)
            if radius > 500:  # Limit radius to 500km
                radius = 500
        except (ValueError, TypeError):
            radius = 100
        
        nearby_cities = city.get_nearby_cities(radius_km=radius)[:20]
        serializer = CityListSerializer(nearby_cities, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def search_by_coordinates(self, request):
        """Search cities by coordinates"""
        lat = request.query_params.get('lat')
        lng = request.query_params.get('lng')
        radius = request.query_params.get('radius', 50)
        
        if not lat or not lng:
            return Response(
                {'error': 'Both lat and lng parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            lat = float(lat)
            lng = float(lng)
            radius = int(radius)
            
            if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
                raise ValueError("Invalid coordinates")
            
            if radius > 500:
                radius = 500
                
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid coordinate or radius values'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Simple bounding box search (in production, use PostGIS)
        lat_delta = radius / 111.0
        lng_delta = radius / (111.0 * abs(lat) * 0.017453)
        
        cities = self.get_queryset().filter(
            latitude__range=(lat - lat_delta, lat + lat_delta),
            longitude__range=(lng - lng_delta, lng + lng_delta),
            is_active=True
        )[:50]  # Limit results
        
        serializer = CityListSerializer(cities, many=True)
        return Response(serializer.data)
