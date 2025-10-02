from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LeaseViewSet, PaymentScheduleViewSet, LeaseTermsViewSet, LeaseTemplateViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'leases', LeaseViewSet, basename='lease')
router.register(r'payment-schedules', PaymentScheduleViewSet, basename='paymentschedule')
router.register(r'lease-terms', LeaseTermsViewSet, basename='leaseterms')
router.register(r'lease-templates', LeaseTemplateViewSet, basename='leasetemplate')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
]