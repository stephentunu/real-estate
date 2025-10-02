from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Appointment, AppointmentType, AppointmentReminder

User = get_user_model()


class AppointmentTypeSerializer(serializers.ModelSerializer):
    """
    Serializer for AppointmentType model
    """
    
    appointment_count = serializers.ReadOnlyField()
    active_appointment_count = serializers.ReadOnlyField()
    
    class Meta:
        model = AppointmentType
        fields = [
            'id', 'name', 'description', 'duration_minutes', 'color',
            'is_active', 'requires_property', 'appointment_count',
            'active_appointment_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_color(self, value):
        """Validate hex color format"""
        if not value.startswith('#') or len(value) != 7:
            raise serializers.ValidationError("Color must be a valid hex code (e.g., #3B82F6)")
        return value


class AppointmentTypeCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating AppointmentType
    """
    
    class Meta:
        model = AppointmentType
        fields = [
            'name', 'description', 'duration_minutes', 'color',
            'is_active', 'requires_property'
        ]
    
    def validate_duration_minutes(self, value):
        """Validate duration is reasonable"""
        if value < 15 or value > 480:  # 15 minutes to 8 hours
            raise serializers.ValidationError("Duration must be between 15 minutes and 8 hours")
        return value


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for appointments
    """
    
    full_name = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = ['id', 'username', 'email', 'first_name', 'last_name', 'full_name']


class PropertyBasicSerializer(serializers.Serializer):
    """
    Basic property serializer for appointments
    """
    
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    address = serializers.CharField(read_only=True)
    property_type = serializers.CharField(read_only=True)
    price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    image = serializers.URLField(read_only=True)


class AppointmentListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing appointments
    """
    
    client = UserBasicSerializer(read_only=True)
    agent = UserBasicSerializer(read_only=True)
    property = PropertyBasicSerializer(read_only=True)
    appointment_type = AppointmentTypeSerializer(read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    scheduled_datetime = serializers.ReadOnlyField()
    end_datetime = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'title', 'description', 'appointment_type', 'client', 'agent',
            'property', 'scheduled_date', 'scheduled_time', 'scheduled_datetime',
            'end_datetime', 'duration_minutes', 'status', 'status_display',
            'priority', 'priority_display', 'is_past', 'is_today', 'is_upcoming',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'scheduled_datetime', 'end_datetime', 'is_past', 'is_today',
            'is_upcoming', 'created_at', 'updated_at'
        ]


class AppointmentDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for appointment details
    """
    
    client = UserBasicSerializer(read_only=True)
    agent = UserBasicSerializer(read_only=True)
    property = PropertyBasicSerializer(read_only=True)
    appointment_type = AppointmentTypeSerializer(read_only=True)
    cancelled_by = UserBasicSerializer(read_only=True)
    original_appointment = serializers.PrimaryKeyRelatedField(read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    scheduled_datetime = serializers.ReadOnlyField()
    end_datetime = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    is_today = serializers.ReadOnlyField()
    is_upcoming = serializers.ReadOnlyField()
    can_be_cancelled = serializers.ReadOnlyField()
    can_be_rescheduled = serializers.ReadOnlyField()
    
    class Meta:
        model = Appointment
        fields = [
            'id', 'title', 'description', 'appointment_type', 'client', 'agent',
            'property', 'scheduled_date', 'scheduled_time', 'scheduled_datetime',
            'end_datetime', 'duration_minutes', 'timezone', 'status', 'status_display',
            'priority', 'priority_display', 'client_phone', 'client_email',
            'meeting_location', 'meeting_link', 'agent_notes', 'client_notes',
            'completion_notes', 'reminder_sent', 'reminder_sent_at',
            'cancelled_at', 'cancelled_by', 'cancellation_reason',
            'original_appointment', 'reschedule_count', 'is_past', 'is_today',
            'is_upcoming', 'can_be_cancelled', 'can_be_rescheduled',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'scheduled_datetime', 'end_datetime', 'reminder_sent',
            'reminder_sent_at', 'cancelled_at', 'cancelled_by', 'cancellation_reason',
            'original_appointment', 'reschedule_count', 'is_past', 'is_today',
            'is_upcoming', 'can_be_cancelled', 'can_be_rescheduled',
            'created_at', 'updated_at'
        ]


class AppointmentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating appointments
    """
    
    class Meta:
        model = Appointment
        fields = [
            'title', 'description', 'appointment_type', 'client', 'agent',
            'property_ref', 'scheduled_date', 'scheduled_time', 'duration_minutes',
            'timezone', 'priority', 'client_phone', 'client_email',
            'meeting_location', 'meeting_link', 'agent_notes', 'client_notes'
        ]
    
    def validate_scheduled_date(self, value):
        """Validate scheduled date is not in the past"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Appointment date cannot be in the past")
        return value
    
    def validate_scheduled_time(self, value):
        """Validate scheduled time with date"""
        # This will be validated in the model's clean method
        return value
    
    def validate_duration_minutes(self, value):
        """Validate duration is reasonable"""
        if value and (value < 15 or value > 480):  # 15 minutes to 8 hours
            raise serializers.ValidationError("Duration must be between 15 minutes and 8 hours")
        return value
    
    def validate(self, attrs):
        """Cross-field validation"""
        # Check if appointment type requires property
        appointment_type = attrs.get('appointment_type')
        property_obj = attrs.get('property_ref')
        
        if appointment_type and appointment_type.requires_property and not property_obj:
            raise serializers.ValidationError({
                'property_ref': f'Property is required for {appointment_type.name} appointments.'
            })
        
        # Check if scheduled datetime is in the future
        scheduled_date = attrs.get('scheduled_date')
        scheduled_time = attrs.get('scheduled_time')
        
        if scheduled_date and scheduled_time:
            scheduled_datetime = timezone.datetime.combine(scheduled_date, scheduled_time)
            if scheduled_datetime <= timezone.now():
                raise serializers.ValidationError({
                    'scheduled_time': 'Appointment must be scheduled for a future date and time.'
                })
        
        return attrs


class AppointmentRescheduleSerializer(serializers.Serializer):
    """
    Serializer for rescheduling appointments
    """
    
    new_date = serializers.DateField()
    new_time = serializers.TimeField()
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)
    
    def validate_new_date(self, value):
        """Validate new date is not in the past"""
        if value < timezone.now().date():
            raise serializers.ValidationError("New appointment date cannot be in the past")
        return value
    
    def validate(self, attrs):
        """Validate new datetime is in the future"""
        new_date = attrs.get('new_date')
        new_time = attrs.get('new_time')
        
        if new_date and new_time:
            new_datetime = timezone.datetime.combine(new_date, new_time)
            if new_datetime <= timezone.now():
                raise serializers.ValidationError({
                    'new_time': 'New appointment time must be in the future.'
                })
        
        return attrs


class AppointmentCancelSerializer(serializers.Serializer):
    """
    Serializer for cancelling appointments
    """
    
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)


class AppointmentCompleteSerializer(serializers.Serializer):
    """
    Serializer for completing appointments
    """
    
    completion_notes = serializers.CharField(max_length=1000, required=False, allow_blank=True)


class AppointmentReminderSerializer(serializers.ModelSerializer):
    """
    Serializer for appointment reminders
    """
    
    appointment = AppointmentListSerializer(read_only=True)
    reminder_type_display = serializers.CharField(source='get_reminder_type_display', read_only=True)
    
    class Meta:
        model = AppointmentReminder
        fields = [
            'id', 'appointment', 'reminder_type', 'reminder_type_display',
            'scheduled_for', 'sent_at', 'is_sent', 'subject', 'message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'sent_at', 'is_sent', 'created_at', 'updated_at']


class AppointmentStatsSerializer(serializers.Serializer):
    """
    Serializer for appointment statistics
    """
    
    total_appointments = serializers.IntegerField()
    pending_appointments = serializers.IntegerField()
    confirmed_appointments = serializers.IntegerField()
    completed_appointments = serializers.IntegerField()
    cancelled_appointments = serializers.IntegerField()
    today_appointments = serializers.IntegerField()
    upcoming_appointments = serializers.IntegerField()
    overdue_appointments = serializers.IntegerField()
    
    # Breakdown by status
    status_breakdown = serializers.DictField()
    
    # Breakdown by appointment type
    type_breakdown = serializers.DictField()
    
    # Breakdown by agent
    agent_breakdown = serializers.DictField()
    
    # Monthly trends
    monthly_trends = serializers.ListField()


class AgentAvailabilitySerializer(serializers.Serializer):
    """
    Serializer for checking agent availability
    """
    
    agent_id = serializers.IntegerField()
    date = serializers.DateField()
    start_time = serializers.TimeField(required=False)
    end_time = serializers.TimeField(required=False)
    
    available_slots = serializers.ListField(read_only=True)
    busy_slots = serializers.ListField(read_only=True)
    
    def validate_date(self, value):
        """Validate date is not in the past"""
        if value < timezone.now().date():
            raise serializers.ValidationError("Date cannot be in the past")
        return value
    
    def validate(self, attrs):
        """Validate time range"""
        start_time = attrs.get('start_time')
        end_time = attrs.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be after start time.'
            })
        
        return attrs