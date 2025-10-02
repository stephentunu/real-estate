from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model

from .models import Notification, NotificationType, NotificationPreference
from apps.users.serializers import UserBasicSerializer

User = get_user_model()


class NotificationTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationType model
    """
    
    class Meta:
        model = NotificationType
        fields = [
            'id', 'name', 'description', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationSerializer(serializers.ModelSerializer):
    """
    Serializer for Notification model
    """
    recipient = UserBasicSerializer(read_only=True)
    notification_type = NotificationTypeSerializer(read_only=True)
    notification_type_id = serializers.IntegerField(write_only=True)
    content_type_name = serializers.SerializerMethodField()
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'recipient', 'notification_type', 'notification_type_id',
            'title', 'message', 'priority', 'content_type', 'object_id',
            'content_type_name', 'is_read', 'read_at', 'email_sent',
            'email_sent_at', 'push_sent', 'push_sent_at', 'data',
            'created_at', 'updated_at', 'expires_at', 'time_since_created'
        ]
        read_only_fields = [
            'id', 'recipient', 'is_read', 'read_at', 'email_sent',
            'email_sent_at', 'push_sent', 'push_sent_at', 'created_at',
            'updated_at', 'content_type_name', 'time_since_created'
        ]
    
    def get_content_type_name(self, obj):
        """
        Get human-readable content type name
        """
        if obj.content_type:
            return obj.content_type.model
        return None
    
    def get_time_since_created(self, obj):
        """
        Get human-readable time since creation
        """
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        now = timezone.now()
        return timesince(obj.created_at, now)
    
    def validate_notification_type_id(self, value):
        """
        Validate notification type exists and is active
        """
        try:
            notification_type = NotificationType.objects.get(id=value, is_active=True)
        except NotificationType.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive notification type.")
        return value
    
    def create(self, validated_data):
        """
        Create notification with proper recipient assignment
        """
        notification_type_id = validated_data.pop('notification_type_id')
        notification_type = NotificationType.objects.get(id=notification_type_id)
        
        notification = Notification.objects.create(
            notification_type=notification_type,
            **validated_data
        )
        return notification


class NotificationListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for notification lists
    """
    notification_type_name = serializers.CharField(source='notification_type.name', read_only=True)
    time_since_created = serializers.SerializerMethodField()
    
    class Meta:
        model = Notification
        fields = [
            'id', 'title', 'message', 'priority', 'notification_type_name',
            'is_read', 'created_at', 'time_since_created'
        ]
    
    def get_time_since_created(self, obj):
        """
        Get human-readable time since creation
        """
        from django.utils import timezone
        from django.utils.timesince import timesince
        
        now = timezone.now()
        return timesince(obj.created_at, now)


class NotificationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating notifications
    """
    recipient_id = serializers.IntegerField(write_only=True)
    notification_type_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'recipient_id', 'notification_type_id', 'title', 'message',
            'priority', 'content_type', 'object_id', 'data', 'expires_at'
        ]
    
    def validate_recipient_id(self, value):
        """
        Validate recipient exists
        """
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid recipient.")
        return value
    
    def validate_notification_type_id(self, value):
        """
        Validate notification type exists and is active
        """
        try:
            NotificationType.objects.get(id=value, is_active=True)
        except NotificationType.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive notification type.")
        return value
    
    def create(self, validated_data):
        """
        Create notification with proper foreign key assignments
        """
        recipient_id = validated_data.pop('recipient_id')
        notification_type_id = validated_data.pop('notification_type_id')
        
        recipient = User.objects.get(id=recipient_id)
        notification_type = NotificationType.objects.get(id=notification_type_id)
        
        notification = Notification.objects.create(
            recipient=recipient,
            notification_type=notification_type,
            **validated_data
        )
        return notification


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """
    Serializer for NotificationPreference model
    """
    user = UserBasicSerializer(read_only=True)
    notification_type = NotificationTypeSerializer(read_only=True)
    notification_type_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id', 'user', 'notification_type', 'notification_type_id',
            'email_enabled', 'push_enabled', 'in_app_enabled',
            'quiet_hours_start', 'quiet_hours_end', 'frequency',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def validate_notification_type_id(self, value):
        """
        Validate notification type exists and is active
        """
        try:
            NotificationType.objects.get(id=value, is_active=True)
        except NotificationType.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive notification type.")
        return value
    
    def validate(self, attrs):
        """
        Validate quiet hours
        """
        quiet_hours_start = attrs.get('quiet_hours_start')
        quiet_hours_end = attrs.get('quiet_hours_end')
        
        if quiet_hours_start and not quiet_hours_end:
            raise serializers.ValidationError({
                'quiet_hours_end': 'End time is required when start time is provided.'
            })
        
        if quiet_hours_end and not quiet_hours_start:
            raise serializers.ValidationError({
                'quiet_hours_start': 'Start time is required when end time is provided.'
            })
        
        return attrs
    
    def create(self, validated_data):
        """
        Create notification preference with proper user assignment
        """
        notification_type_id = validated_data.pop('notification_type_id')
        notification_type = NotificationType.objects.get(id=notification_type_id)
        
        preference = NotificationPreference.objects.create(
            user=self.context['request'].user,
            notification_type=notification_type,
            **validated_data
        )
        return preference


class BulkNotificationSerializer(serializers.Serializer):
    """
    Serializer for creating bulk notifications
    """
    recipient_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        max_length=1000  # Limit bulk operations
    )
    notification_type_id = serializers.IntegerField()
    title = serializers.CharField(max_length=255)
    message = serializers.CharField()
    priority = serializers.ChoiceField(
        choices=Notification.PRIORITY_CHOICES,
        default='medium'
    )
    data = serializers.JSONField(default=dict, required=False)
    expires_at = serializers.DateTimeField(required=False)
    
    def validate_recipient_ids(self, value):
        """
        Validate all recipients exist
        """
        existing_ids = set(User.objects.filter(id__in=value).values_list('id', flat=True))
        invalid_ids = set(value) - existing_ids
        
        if invalid_ids:
            raise serializers.ValidationError(
                f"Invalid recipient IDs: {list(invalid_ids)}"
            )
        
        return value
    
    def validate_notification_type_id(self, value):
        """
        Validate notification type exists and is active
        """
        try:
            NotificationType.objects.get(id=value, is_active=True)
        except NotificationType.DoesNotExist:
            raise serializers.ValidationError("Invalid or inactive notification type.")
        return value
    
    def create(self, validated_data):
        """
        Create bulk notifications
        """
        recipient_ids = validated_data.pop('recipient_ids')
        notification_type_id = validated_data.pop('notification_type_id')
        
        notification_type = NotificationType.objects.get(id=notification_type_id)
        recipients = User.objects.filter(id__in=recipient_ids)
        
        notifications = []
        for recipient in recipients:
            notification = Notification(
                recipient=recipient,
                notification_type=notification_type,
                **validated_data
            )
            notifications.append(notification)
        
        # Bulk create for efficiency
        created_notifications = Notification.objects.bulk_create(notifications)
        return created_notifications


class NotificationStatsSerializer(serializers.Serializer):
    """
    Serializer for notification statistics
    """
    total_count = serializers.IntegerField()
    unread_count = serializers.IntegerField()
    read_count = serializers.IntegerField()
    priority_breakdown = serializers.DictField()
    type_breakdown = serializers.DictField()
    recent_count = serializers.IntegerField()  # Last 24 hours