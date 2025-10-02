from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PropertyViewSet,
    PropertyTypeViewSet,
    PropertyStatusViewSet,
    PropertyImageViewSet,
    PropertyFeatureViewSet,
    SavedPropertyViewSet,
    AmenityViewSet,
    PropertyAmenityViewSet
)

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'properties', PropertyViewSet)
router.register(r'property-types', PropertyTypeViewSet)
router.register(r'property-statuses', PropertyStatusViewSet)
router.register(r'property-images', PropertyImageViewSet)
router.register(r'property-features', PropertyFeatureViewSet)
router.register(r'amenities', AmenityViewSet)
router.register(r'property-amenities', PropertyAmenityViewSet)
router.register(r'saved-properties', SavedPropertyViewSet)

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    # Manual URL patterns for custom actions
    path('featured/', PropertyViewSet.as_view({'get': 'featured'}), name='property-featured'),
]