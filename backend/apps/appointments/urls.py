from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    AppointmentTypeViewSet,
    AppointmentViewSet,
    AppointmentReminderViewSet
)

# Create router and register viewsets
router = DefaultRouter()
router.register(r'types', AppointmentTypeViewSet, basename='appointmenttype')
router.register(r'appointments', AppointmentViewSet, basename='appointment')
router.register(r'reminders', AppointmentReminderViewSet, basename='appointmentreminder')

app_name = 'appointments'

urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Custom appointment type endpoints
    path('types/active/', AppointmentTypeViewSet.as_view({'get': 'active'}), name='appointmenttype-active'),
    path('types/<int:pk>/toggle-active/', AppointmentTypeViewSet.as_view({'post': 'toggle_active'}), name='appointmenttype-toggle-active'),
    
    # Custom appointment endpoints
    path('appointments/my/', AppointmentViewSet.as_view({'get': 'my_appointments'}), name='appointment-my'),
    path('appointments/today/', AppointmentViewSet.as_view({'get': 'today'}), name='appointment-today'),
    path('appointments/upcoming/', AppointmentViewSet.as_view({'get': 'upcoming'}), name='appointment-upcoming'),
    path('appointments/past/', AppointmentViewSet.as_view({'get': 'past'}), name='appointment-past'),
    path('appointments/by-status/', AppointmentViewSet.as_view({'get': 'by_status'}), name='appointment-by-status'),
    path('appointments/stats/', AppointmentViewSet.as_view({'get': 'stats'}), name='appointment-stats'),
    path('appointments/check-availability/', AppointmentViewSet.as_view({'post': 'check_availability'}), name='appointment-check-availability'),
    
    # Appointment action endpoints
    path('appointments/<int:pk>/reschedule/', AppointmentViewSet.as_view({'post': 'reschedule'}), name='appointment-reschedule'),
    path('appointments/<int:pk>/cancel/', AppointmentViewSet.as_view({'post': 'cancel'}), name='appointment-cancel'),
    path('appointments/<int:pk>/confirm/', AppointmentViewSet.as_view({'post': 'confirm'}), name='appointment-confirm'),
    path('appointments/<int:pk>/complete/', AppointmentViewSet.as_view({'post': 'complete'}), name='appointment-complete'),
    
    # Custom reminder endpoints
    path('reminders/pending/', AppointmentReminderViewSet.as_view({'get': 'pending'}), name='appointmentreminder-pending'),
    path('reminders/<int:pk>/mark-sent/', AppointmentReminderViewSet.as_view({'post': 'mark_sent'}), name='appointmentreminder-mark-sent'),
]