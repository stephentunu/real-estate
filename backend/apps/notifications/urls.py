from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'notifications', views.NotificationViewSet, basename='notification')
router.register(r'notification-types', views.NotificationTypeViewSet)
router.register(r'preferences', views.NotificationPreferenceViewSet, basename='notificationpreference')
router.register(r'bulk', views.BulkNotificationViewSet, basename='bulknotification')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Available endpoints:
    # GET /notifications/ - List user's notifications
    # POST /notifications/ - Create notification
    # GET /notifications/{id}/ - Get notification detail
    # PUT/PATCH /notifications/{id}/ - Update notification
    # DELETE /notifications/{id}/ - Delete notification
    # POST /notifications/{id}/mark_as_read/ - Mark notification as read
    # POST /notifications/mark_all_read/ - Mark all notifications as read
    # POST /notifications/mark_selected_read/ - Mark selected notifications as read
    # DELETE /notifications/delete_read/ - Delete all read notifications
    # GET /notifications/unread_count/ - Get unread count
    # GET /notifications/stats/ - Get notification statistics
    # GET /notifications/recent/ - Get recent notifications
    # 
    # GET /notification-types/ - List notification types
    # GET /notification-types/{id}/ - Get notification type detail
    # 
    # GET /preferences/ - List user's notification preferences
    # POST /preferences/ - Create notification preference
    # GET /preferences/{id}/ - Get preference detail
    # PUT/PATCH /preferences/{id}/ - Update preference
    # DELETE /preferences/{id}/ - Delete preference
    # POST /preferences/bulk_update/ - Bulk update preferences
    # POST /preferences/reset_to_defaults/ - Reset preferences to defaults
    # 
    # POST /bulk/create_bulk/ - Create bulk notifications (admin only)
    # POST /bulk/send_to_all_users/ - Send notification to all users (admin only)
]