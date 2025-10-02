from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin, SearchableMixin

User = get_user_model()


class AppointmentType(VisibilityMixin, SoftDeleteMixin, SearchableMixin):
    """
    Model for appointment types (Property Viewing, Consultation, etc.)
    """
    
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField(default=60, help_text="Default duration in minutes")
    color = models.CharField(max_length=7, default='#3B82F6', help_text="Hex color code for calendar display")
    is_active = models.BooleanField(default=True)
    requires_property = models.BooleanField(default=True, help_text="Whether this appointment type requires a property")
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_appointment_types')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_appointment_types')
    
    class Meta:
        db_table = 'appointment_types'
        verbose_name = 'Appointment Type'
        verbose_name_plural = 'Appointment Types'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('appointments:type-detail', kwargs={'pk': self.pk})
    
    @property
    def appointment_count(self):
        """Return count of appointments using this type"""
        return self.appointments.filter(is_deleted=False).count()
    
    @property
    def active_appointment_count(self):
        """Return count of active appointments using this type"""
        return self.appointments.filter(
            is_deleted=False,
            status__in=[Appointment.StatusChoices.SCHEDULED, Appointment.StatusChoices.CONFIRMED]
        ).count()


class Appointment(VisibilityMixin, SoftDeleteMixin, SearchableMixin):
    """
    Model for property appointments
    """
    
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        CONFIRMED = 'confirmed', 'Confirmed'
        SCHEDULED = 'scheduled', 'Scheduled'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        NO_SHOW = 'no_show', 'No Show'
        RESCHEDULED = 'rescheduled', 'Rescheduled'
    
    class PriorityChoices(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'
    
    # Core fields
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    appointment_type = models.ForeignKey(AppointmentType, on_delete=models.PROTECT, related_name='appointments')
    
    # Participants
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='client_appointments')
    agent = models.ForeignKey(User, on_delete=models.CASCADE, related_name='agent_appointments', limit_choices_to={'is_staff': True})
    
    # Property (optional based on appointment type)
    property_ref = models.ForeignKey('properties.Property', on_delete=models.CASCADE, related_name='appointments', null=True, blank=True)
    
    # Scheduling
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    timezone = models.CharField(max_length=50, default='UTC')
    
    # Status and priority
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.PENDING)
    priority = models.CharField(max_length=10, choices=PriorityChoices.choices, default=PriorityChoices.MEDIUM)
    
    # Contact information
    client_phone = models.CharField(max_length=20, blank=True)
    client_email = models.EmailField(blank=True)
    
    # Location (if different from property)
    meeting_location = models.TextField(blank=True, help_text="Custom meeting location if not at property")
    meeting_link = models.URLField(blank=True, help_text="Video call link for virtual appointments")
    
    # Notes and feedback
    agent_notes = models.TextField(blank=True, help_text="Private notes for agent")
    client_notes = models.TextField(blank=True, help_text="Notes from client")
    completion_notes = models.TextField(blank=True, help_text="Notes after appointment completion")
    
    # Reminders
    reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    # Cancellation
    cancelled_at = models.DateTimeField(null=True, blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='cancelled_appointments')
    cancellation_reason = models.TextField(blank=True)
    
    # Rescheduling
    original_appointment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='rescheduled_appointments')
    reschedule_count = models.PositiveIntegerField(default=0)
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_appointments')
    updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updated_appointments')
    
    class Meta:
        db_table = 'appointments'
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        ordering = ['-scheduled_date', '-scheduled_time']
        indexes = [
            models.Index(fields=['scheduled_date', 'scheduled_time']),
            models.Index(fields=['status']),
            models.Index(fields=['client']),
            models.Index(fields=['agent']),
            models.Index(fields=['property_ref']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.scheduled_date} {self.scheduled_time}"
    
    def clean(self):
        """Validate appointment data"""
        super().clean()
        
        # Check if appointment type requires property
        if self.appointment_type and self.appointment_type.requires_property and not self.property:
            raise ValidationError({
                'property': f'Property is required for {self.appointment_type.name} appointments.'
            })
        
        # Check if scheduled time is in the future (for new appointments)
        if not self.pk:  # New appointment
            scheduled_datetime = timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
            if scheduled_datetime <= timezone.now():
                raise ValidationError({
                    'scheduled_date': 'Appointment must be scheduled for a future date and time.'
                })
        
        # Check agent availability (basic check)
        if self.agent and self.scheduled_date and self.scheduled_time:
            overlapping = Appointment.objects.filter(
                agent=self.agent,
                scheduled_date=self.scheduled_date,
                scheduled_time=self.scheduled_time,
                status__in=[self.StatusChoices.SCHEDULED, self.StatusChoices.CONFIRMED],
                is_deleted=False
            ).exclude(pk=self.pk)
            
            if overlapping.exists():
                raise ValidationError({
                    'scheduled_time': 'Agent is not available at this time.'
                })
    
    def save(self, *args, **kwargs):
        """Override save to handle business logic"""
        # Set duration from appointment type if not specified
        if not self.duration_minutes and self.appointment_type:
            self.duration_minutes = self.appointment_type.duration_minutes
        
        # Set client contact info from user if not provided
        if self.client and not self.client_email:
            self.client_email = self.client.email
        
        # Auto-generate title if not provided
        if not self.title:
            property_name = self.property_ref.title if self.property_ref else "General"
            self.title = f"{self.appointment_type.name} - {property_name}"
        
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('appointments:detail', kwargs={'pk': self.pk})
    
    @property
    def scheduled_datetime(self):
        """Return combined date and time"""
        return timezone.datetime.combine(self.scheduled_date, self.scheduled_time)
    
    @property
    def end_datetime(self):
        """Return appointment end time"""
        return self.scheduled_datetime + timezone.timedelta(minutes=self.duration_minutes)
    
    @property
    def is_past(self):
        """Check if appointment is in the past"""
        return self.scheduled_datetime < timezone.now()
    
    @property
    def is_today(self):
        """Check if appointment is today"""
        return self.scheduled_date == timezone.now().date()
    
    @property
    def is_upcoming(self):
        """Check if appointment is upcoming (within next 24 hours)"""
        return self.scheduled_datetime <= timezone.now() + timezone.timedelta(hours=24)
    
    @property
    def can_be_cancelled(self):
        """Check if appointment can be cancelled"""
        return self.status in [self.StatusChoices.PENDING, self.StatusChoices.CONFIRMED, self.StatusChoices.SCHEDULED]
    
    @property
    def can_be_rescheduled(self):
        """Check if appointment can be rescheduled"""
        return self.status in [self.StatusChoices.PENDING, self.StatusChoices.CONFIRMED, self.StatusChoices.SCHEDULED]
    
    def cancel(self, user, reason=""):
        """Cancel the appointment"""
        if not self.can_be_cancelled:
            raise ValidationError("This appointment cannot be cancelled.")
        
        self.status = self.StatusChoices.CANCELLED
        self.cancelled_at = timezone.now()
        self.cancelled_by = user
        self.cancellation_reason = reason
        self.save()
    
    def reschedule(self, new_date, new_time, user):
        """Reschedule the appointment"""
        if not self.can_be_rescheduled:
            raise ValidationError("This appointment cannot be rescheduled.")
        
        # Create new appointment
        new_appointment = Appointment.objects.create(
            title=self.title,
            description=self.description,
            appointment_type=self.appointment_type,
            client=self.client,
            agent=self.agent,
            property=self.property,
            scheduled_date=new_date,
            scheduled_time=new_time,
            duration_minutes=self.duration_minutes,
            priority=self.priority,
            client_phone=self.client_phone,
            client_email=self.client_email,
            meeting_location=self.meeting_location,
            meeting_link=self.meeting_link,
            agent_notes=self.agent_notes,
            client_notes=self.client_notes,
            original_appointment=self,
            reschedule_count=self.reschedule_count + 1,
            created_by=user
        )
        
        # Mark current appointment as rescheduled
        self.status = self.StatusChoices.RESCHEDULED
        self.save()
        
        return new_appointment
    
    def mark_completed(self, completion_notes=""):
        """Mark appointment as completed"""
        self.status = self.StatusChoices.COMPLETED
        self.completion_notes = completion_notes
        self.save()
    
    def mark_no_show(self):
        """Mark appointment as no show"""
        self.status = self.StatusChoices.NO_SHOW
        self.save()


class AppointmentReminder(models.Model):
    """
    Model for appointment reminders
    """
    
    class ReminderType(models.TextChoices):
        EMAIL = 'email', 'Email'
        SMS = 'sms', 'SMS'
        PUSH = 'push', 'Push Notification'
        IN_APP = 'in_app', 'In-App Notification'
    
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=10, choices=ReminderType.choices)
    scheduled_for = models.DateTimeField()
    sent_at = models.DateTimeField(null=True, blank=True)
    is_sent = models.BooleanField(default=False)
    
    # Message content
    subject = models.CharField(max_length=200, blank=True)
    message = models.TextField()
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'appointment_reminders'
        verbose_name = 'Appointment Reminder'
        verbose_name_plural = 'Appointment Reminders'
        ordering = ['scheduled_for']
        indexes = [
            models.Index(fields=['scheduled_for', 'is_sent']),
            models.Index(fields=['appointment']),
        ]
    
    def __str__(self):
        return f"Reminder for {self.appointment.title} - {self.get_reminder_type_display()}"
    
    def mark_sent(self):
        """Mark reminder as sent"""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()
