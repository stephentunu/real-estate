from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MaintenanceRequestViewSet, ContractorViewSet, WorkOrderViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'maintenance-requests', MaintenanceRequestViewSet, basename='maintenancerequest')
router.register(r'contractors', ContractorViewSet, basename='contractor')
router.register(r'work-orders', WorkOrderViewSet, basename='workorder')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]