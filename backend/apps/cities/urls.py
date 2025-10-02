from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CountryViewSet, StateViewSet, CityViewSet

# Create router and register viewsets
router = DefaultRouter()
router.register(r'countries', CountryViewSet, basename='country')
router.register(r'states', StateViewSet, basename='state')
router.register(r'cities', CityViewSet, basename='city')

app_name = 'cities'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Custom endpoints for countries
    path('countries/stats/', CountryViewSet.as_view({'get': 'stats'}), name='country-stats'),
    path('countries/<slug:slug>/states/', CountryViewSet.as_view({'get': 'states'}), name='country-states'),
    path('countries/<slug:slug>/cities/', CountryViewSet.as_view({'get': 'cities'}), name='country-cities'),
    
    # Custom endpoints for states
    path('states/stats/', StateViewSet.as_view({'get': 'stats'}), name='state-stats'),
    path('states/<slug:slug>/cities/', StateViewSet.as_view({'get': 'cities'}), name='state-cities'),
    
    # Custom endpoints for cities
    path('cities/stats/', CityViewSet.as_view({'get': 'stats'}), name='city-stats'),
    path('cities/featured/', CityViewSet.as_view({'get': 'featured'}), name='city-featured'),
    path('cities/capitals/', CityViewSet.as_view({'get': 'capitals'}), name='city-capitals'),
    path('cities/search-by-coordinates/', CityViewSet.as_view({'get': 'search_by_coordinates'}), name='city-search-coordinates'),
    path('cities/<slug:slug>/nearby/', CityViewSet.as_view({'get': 'nearby'}), name='city-nearby'),
]