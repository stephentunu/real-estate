from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Case, When, IntegerField
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

from .models import Notification, NotificationType, NotificationPreference
from .serializers import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
    NotificationTypeSerializer,
    NotificationPreferenceSerializer,
    BulkNotificationSerializer,
    NotificationStatsSerializer
)

User = get_user_model()


class NotificationFilter(DjangoFilterBackend):
    """
    Custom filter for notifications
    """
    
    class Meta:
        model = Notification
        fields = {
            'is_read': ['exact'],
            'priority': ['exact', 'in'],
            'notification_type': ['exact'],
            'created_at': ['gte', 'lte', 'date'],
            'expires_at': ['gte', 'lte', 'isnull'],
        }


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners to view/edit their notifications
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user who owns the notification
        if hasattr(obj, 'recipient'):
            return obj.recipient == request.user
        elif hasattr(obj, 'user'):
            return obj.user == request.user
        return False


class NotificationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Notification model
    Handles CRUD operations for notifications
    """
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = {
        'is_read': ['exact'],
        'priority': ['exact', 'in'],
        'notification_type': ['exact'],
        'created_at': ['gte', 'lte', 'date'],
        'expires_at': ['gte', 'lte', 'isnull'],
    }
    search_fields = ['title', 'message']
    ordering_fields = ['created_at', 'priority', 'is_read']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Return notifications for the current user only
        """
        user = self.request.user
        if not user.is_authenticated:
            return Notification.objects.none()

        return Notification.objects.filter(
            recipient=user
        ).select_related(
            'notification_type', 'recipient', 'content_type'
        ).filter(
            # Exclude expired notifications
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return NotificationListSerializer
        elif self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def perform_create(self, serializer):
        """
        Create notification with current user as recipient if not specified
        """
        if 'recipient' not in serializer.validated_data:
            serializer.save(recipient=self.request.user)
        else:
            serializer.save()
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark notification as read
        """
        notification = self.get_object()
        notification.mark_as_read()
        return Response({'status': 'marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """
        Mark all notifications as read for current user
        """
        updated_count = self.get_queryset().filter(is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
        return Response({
            'status': f'marked {updated_count} notifications as read'
        })
    
    @action(detail=False, methods=['post'])
    def mark_selected_read(self, request):
        """
        Mark selected notifications as read
        """
        notification_ids = request.data.get('notification_ids', [])
        
        if not notification_ids:
            return Response(
                {'error': 'notification_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = self.get_queryset().filter(
            id__in=notification_ids,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        return Response({
            'status': f'marked {updated_count} notifications as read'
        })
    
    @action(detail=False, methods=['delete'])
    def delete_read(self, request):
        """
        Delete all read notifications for current user
        """
        deleted_count, _ = self.get_queryset().filter(is_read=True).delete()
        return Response({
            'status': f'deleted {deleted_count} read notifications'
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get unread notification count
        """
        count = self.get_queryset().filter(is_read=False).count()
        return Response({'unread_count': count})
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get notification statistics
        """
        queryset = self.get_queryset()
        
        # Basic counts
        total_count = queryset.count()
        unread_count = queryset.filter(is_read=False).count()
        read_count = total_count - unread_count
        
        # Recent count (last 24 hours)
        recent_threshold = timezone.now() - timedelta(hours=24)
        recent_count = queryset.filter(created_at__gte=recent_threshold).count()
        
        # Priority breakdown
        priority_breakdown = dict(
            queryset.values('priority').annotate(
                count=Count('id')
            ).values_list('priority', 'count')
        )
        
        # Type breakdown
        type_breakdown = dict(
            queryset.values('notification_type__name').annotate(
                count=Count('id')
            ).values_list('notification_type__name', 'count')
        )
        
        stats_data = {
            'total_count': total_count,
            'unread_count': unread_count,
            'read_count': read_count,
            'recent_count': recent_count,
            'priority_breakdown': priority_breakdown,
            'type_breakdown': type_breakdown,
        }
        
        serializer = NotificationStatsSerializer(stats_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent notifications (last 24 hours)
        """
        recent_threshold = timezone.now() - timedelta(hours=24)
        recent_notifications = self.get_queryset().filter(
            created_at__gte=recent_threshold
        )
        
        page = self.paginate_queryset(recent_notifications)
        if page is not None:
            serializer = NotificationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = NotificationListSerializer(recent_notifications, many=True)
        return Response(serializer.data)


class NotificationTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for NotificationType model
    Read-only access to notification types
    """
    queryset = NotificationType.objects.filter(is_active=True)
    serializer_class = NotificationTypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class NotificationPreferenceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for NotificationPreference model
    Handles user notification preferences
    """
    serializer_class = NotificationPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['notification_type', 'email_enabled', 'push_enabled', 'in_app_enabled']
    ordering_fields = ['notification_type__name', 'created_at']
    ordering = ['notification_type__name']
    
    def get_queryset(self):
        """
        Return preferences for the current user only
        """
        user = self.request.user
        if not user.is_authenticated:
            return NotificationPreference.objects.none()

        return NotificationPreference.objects.filter(
            user=user
        ).select_related('notification_type')
    
    def perform_create(self, serializer):
        """
        Create preference with current user
        """
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """
        Bulk update notification preferences
        """
        preferences_data = request.data.get('preferences', [])
        
        if not preferences_data:
            return Response(
                {'error': 'preferences data is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        updated_count = 0
        errors = []
        
        for pref_data in preferences_data:
            try:
                notification_type_id = pref_data.get('notification_type_id')
                if not notification_type_id:
                    errors.append({'error': 'notification_type_id is required'})
                    continue
                
                preference, created = NotificationPreference.objects.get_or_create(
                    user=request.user,
                    notification_type_id=notification_type_id,
                    defaults=pref_data
                )
                
                if not created:
                    # Update existing preference
                    for key, value in pref_data.items():
                        if key != 'notification_type_id':
                            setattr(preference, key, value)
                    preference.save()
                
                updated_count += 1
                
            except Exception as e:
                errors.append({'notification_type_id': notification_type_id, 'error': str(e)})
        
        response_data = {
            'updated_count': updated_count,
            'errors': errors
        }
        
        if errors:
            return Response(response_data, status=status.HTTP_207_MULTI_STATUS)
        
        return Response(response_data)
    
    @action(detail=False, methods=['post'])
    def reset_to_defaults(self, request):
        """
        Reset all preferences to default values
        """
        self.get_queryset().update(
            email_enabled=True,
            push_enabled=True,
            in_app_enabled=True,
            quiet_hours_start=None,
            quiet_hours_end=None,
            frequency='immediate'
        )
        
        return Response({'status': 'preferences reset to defaults'})


class BulkNotificationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for bulk notification operations
    Admin/Staff only functionality
    """
    serializer_class = BulkNotificationSerializer
    permission_classes = [permissions.IsAuthenticated, permissions.IsAdminUser]
    
    @action(detail=False, methods=['post'])
    def create_bulk(self, request):
        """
        Create bulk notifications
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notifications = serializer.save()
        
        return Response({
            'status': f'created {len(notifications)} notifications',
            'notification_count': len(notifications)
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['post'])
    def send_to_all_users(self, request):
        """
        Send notification to all active users
        """
        title = request.data.get('title')
        message = request.data.get('message')
        notification_type_id = request.data.get('notification_type_id')
        priority = request.data.get('priority', 'medium')
        
        if not all([title, message, notification_type_id]):
            return Response(
                {'error': 'title, message, and notification_type_id are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            notification_type = NotificationType.objects.get(
                id=notification_type_id, is_active=True
            )
        except NotificationType.DoesNotExist:
            return Response(
                {'error': 'Invalid notification type'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get all active users
        active_users = User.objects.filter(is_active=True)
        
        # Create notifications for all users
        notifications = []
        for user in active_users:
            notification = Notification(
                recipient=user,
                notification_type=notification_type,
                title=title,
                message=message,
                priority=priority,
                data=request.data.get('data', {})
            )
            notifications.append(notification)
        
        # Bulk create
        created_notifications = Notification.objects.bulk_create(notifications)
        
        return Response({
            'status': f'sent notification to {len(created_notifications)} users',
            'user_count': len(created_notifications)
        }, status=status.HTTP_201_CREATED)
