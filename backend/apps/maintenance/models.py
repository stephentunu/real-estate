from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date, timedelta
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin, SearchableMixin, NotifiableMixin


class MaintenanceRequest(VisibilityMixin, SoftDeleteMixin, SearchableMixin, NotifiableMixin, models.Model):
    """
    Maintenance Request model with enhanced capabilities:
    - Visibility controls for request access
    - Soft deletion with retention policies
    - Search functionality for requests
    - Notification system integration
    - Comprehensive maintenance management
    """
    
    class RequestStatus(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        ACKNOWLEDGED = 'acknowledged', 'Acknowledged'
        ASSIGNED = 'assigned', 'Assigned'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        ON_HOLD = 'on_hold', 'On Hold'
    
    class Priority(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'
        URGENT = 'urgent', 'Urgent'
        EMERGENCY = 'emergency', 'Emergency'
    
    class Category(models.TextChoices):
        PLUMBING = 'plumbing', 'Plumbing'
        ELECTRICAL = 'electrical', 'Electrical'
        HVAC = 'hvac', 'HVAC'
        APPLIANCES = 'appliances', 'Appliances'
        CARPENTRY = 'carpentry', 'Carpentry'
        PAINTING = 'painting', 'Painting'
        FLOORING = 'flooring', 'Flooring'
        ROOFING = 'roofing', 'Roofing'
        SECURITY = 'security', 'Security'
        CLEANING = 'cleaning', 'Cleaning'
        LANDSCAPING = 'landscaping', 'Landscaping'
        OTHER = 'other', 'Other'
    
    # Core request information
    request_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique maintenance request identifier"
    )
    property_ref = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='maintenance_requests',
        help_text="Property requiring maintenance"
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submitted_maintenance_requests',
        help_text="Tenant who submitted the request"
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_maintenance_requests',
        help_text="Landlord responsible for the property"
    )
    
    # Request details
    title = models.CharField(
        max_length=200,
        help_text="Brief title of the maintenance issue"
    )
    description = models.TextField(
        help_text="Detailed description of the maintenance issue"
    )
    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        help_text="Category of maintenance required"
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        help_text="Priority level of the request"
    )
    status = models.CharField(
        max_length=20,
        choices=RequestStatus.choices,
        default=RequestStatus.SUBMITTED,
        help_text="Current status of the request"
    )
    
    # Location and access
    location_details = models.TextField(
        blank=True,
        help_text="Specific location within the property"
    )
    access_instructions = models.TextField(
        blank=True,
        help_text="Instructions for accessing the property"
    )
    tenant_available = models.BooleanField(
        default=True,
        help_text="Whether tenant will be available for access"
    )
    
    # Scheduling
    preferred_date = models.DateField(
        null=True,
        blank=True,
        help_text="Tenant's preferred date for maintenance"
    )
    preferred_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Tenant's preferred time for maintenance"
    )
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scheduled date for maintenance"
    )
    scheduled_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Scheduled time for maintenance"
    )
    
    # Cost estimation
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Estimated cost of maintenance"
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Actual cost of maintenance"
    )
    
    # Images and documentation
    images = models.JSONField(
        default=list,
        help_text="List of image URLs showing the issue"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    acknowledged_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the request was acknowledged"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the maintenance was completed"
    )
    
    class Meta:
        db_table = 'maintenance_requests'
        verbose_name = 'Maintenance Request'
        verbose_name_plural = 'Maintenance Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['request_number']),
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['category']),
            models.Index(fields=['tenant']),
            models.Index(fields=['landlord']),
            models.Index(fields=['property_ref']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.request_number} - {self.title}"
    
    @property
    def is_overdue(self):
        """Check if scheduled maintenance is overdue"""
        if self.scheduled_date and self.status not in [self.RequestStatus.COMPLETED, self.RequestStatus.CANCELLED]:
            return self.scheduled_date < date.today()
        return False
    
    @property
    def days_since_submitted(self):
        """Calculate days since request was submitted"""
        return (date.today() - self.created_at.date()).days
    
    def mark_as_completed(self, actual_cost=None):
        """Mark request as completed"""
        self.status = self.RequestStatus.COMPLETED
        self.completed_at = timezone.now()
        if actual_cost is not None:
            self.actual_cost = actual_cost
        self.save()
    
    # SearchableMixin implementation
    def get_searchable_fields(self, user_context=None):
        """Define searchable fields based on user context"""
        base_fields = {
            'title': 'A',
            'description': 'B',
            'request_number': 'A',
            'category': 'B',
            'location_details': 'C'
        }
        
        # Add property details for broader search
        if hasattr(self, 'property_ref'):
            base_fields.update({
                'property_ref__title': 'B',
                'property_ref__address': 'B'
            })
        
        return base_fields
    
    def get_search_boost(self, user_context=None):
        """Define search boost factors"""
        boost = 1.0
        
        # Boost urgent/emergency requests
        if self.priority in [self.Priority.URGENT, self.Priority.EMERGENCY]:
            boost *= 1.5
        
        # Boost recent requests
        if self.days_since_submitted <= 7:
            boost *= 1.2
        
        return boost
    
    def get_search_filters(self, user_context=None):
        """Define search filters based on user context"""
        filters = {}
        
        if user_context:
            user_role = getattr(user_context, 'role', None)
            
            # Tenants see only their requests
            if user_role == 'tenant':
                filters['tenant'] = user_context
            
            # Landlords see requests for their properties
            elif user_role == 'landlord':
                filters['landlord'] = user_context
            
            # Contractors see assigned requests
            elif user_role == 'contractor':
                filters['work_orders__contractor'] = user_context
        
        return filters
    
    def get_search_result_fields(self, user_context=None):
        """Define fields to include in search results"""
        return [
            'id', 'request_number', 'title', 'category', 'priority',
            'status', 'created_at', 'scheduled_date', 'property_ref__title'
        ]
    
    # NotifiableMixin implementation
    def get_notification_recipients(self, notification_type, context=None):
        """Define who should receive notifications about this request"""
        recipients = []
        
        # Always notify tenant and landlord
        recipients.extend([self.tenant, self.landlord])
        
        # Include assigned contractors
        for work_order in self.work_orders.filter(status__in=['assigned', 'in_progress']):
            if work_order.contractor:
                recipients.append(work_order.contractor)
        
        # Admin notifications for urgent/emergency requests
        if self.priority in [self.Priority.URGENT, self.Priority.EMERGENCY]:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_users = User.objects.filter(role='admin', is_active=True)
            recipients.extend(admin_users)
        
        return recipients
    
    def should_trigger_notification(self, field_name, old_value, new_value):
        """Determine if field changes should trigger notifications"""
        notification_fields = {
            'status': 'maintenance_status_changed',
            'priority': 'maintenance_priority_changed',
            'scheduled_date': 'maintenance_scheduled',
            'completed_at': 'maintenance_completed'
        }
        
        return field_name in notification_fields


class Contractor(VisibilityMixin, SoftDeleteMixin, SearchableMixin, models.Model):
    """
    Contractor model for managing maintenance service providers
    """
    
    class ContractorStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        INACTIVE = 'inactive', 'Inactive'
        SUSPENDED = 'suspended', 'Suspended'
        PENDING_APPROVAL = 'pending_approval', 'Pending Approval'
    
    # Basic information
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='contractor_profile',
        help_text="Associated user account"
    )
    company_name = models.CharField(
        max_length=200,
        help_text="Company or business name"
    )
    license_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Professional license number"
    )
    
    # Contact information
    business_phone = models.CharField(
        max_length=20,
        help_text="Business phone number"
    )
    business_email = models.EmailField(
        help_text="Business email address"
    )
    website = models.URLField(
        blank=True,
        help_text="Company website"
    )
    
    # Address
    address = models.TextField(
        help_text="Business address"
    )
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    
    # Specializations
    specializations = models.JSONField(
        default=list,
        help_text="List of maintenance categories contractor specializes in"
    )
    
    # Status and ratings
    status = models.CharField(
        max_length=20,
        choices=ContractorStatus.choices,
        default=ContractorStatus.PENDING_APPROVAL,
        help_text="Current contractor status"
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00')), MaxValueValidator(Decimal('5.00'))],
        help_text="Average rating (0-5)"
    )
    total_jobs = models.PositiveIntegerField(
        default=0,
        help_text="Total number of completed jobs"
    )
    
    # Availability
    available_days = models.JSONField(
        default=list,
        help_text="Days of the week contractor is available"
    )
    available_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text="Start of available hours"
    )
    available_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text="End of available hours"
    )
    
    # Insurance and certifications
    insurance_valid_until = models.DateField(
        null=True,
        blank=True,
        help_text="Insurance expiration date"
    )
    certifications = models.JSONField(
        default=list,
        help_text="List of professional certifications"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When contractor was approved"
    )
    
    class Meta:
        db_table = 'contractors'
        verbose_name = 'Contractor'
        verbose_name_plural = 'Contractors'
        ordering = ['-rating', 'company_name']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['rating']),
            models.Index(fields=['city']),
        ]
    
    def __str__(self):
        return f"{self.company_name} ({self.user.get_full_name()})"
    
    @property
    def is_available(self):
        """Check if contractor is currently available"""
        return self.status == self.ContractorStatus.ACTIVE
    
    @property
    def insurance_expired(self):
        """Check if insurance has expired"""
        if self.insurance_valid_until:
            return self.insurance_valid_until < date.today()
        return True
    
    def update_rating(self):
        """Recalculate average rating based on completed work orders"""
        completed_orders = self.work_orders.filter(
            status='completed',
            rating__isnull=False
        )
        
        if completed_orders.exists():
            avg_rating = completed_orders.aggregate(
                avg_rating=models.Avg('rating')
            )['avg_rating']
            self.rating = round(avg_rating, 2)
            self.total_jobs = completed_orders.count()
            self.save()
    
    # SearchableMixin implementation
    def get_searchable_fields(self, user_context=None):
        """Define searchable fields"""
        return {
            'company_name': 'A',
            'user__first_name': 'B',
            'user__last_name': 'B',
            'specializations': 'B',
            'city': 'C',
            'license_number': 'C'
        }
    
    def get_search_boost(self, user_context=None):
        """Define search boost factors"""
        boost = 1.0
        
        # Boost highly rated contractors
        if self.rating >= 4.5:
            boost *= 1.3
        elif self.rating >= 4.0:
            boost *= 1.1
        
        # Boost active contractors
        if self.status == self.ContractorStatus.ACTIVE:
            boost *= 1.2
        
        return boost
    
    def get_search_filters(self, user_context=None):
        """Define search filters"""
        return {
            'status': self.ContractorStatus.ACTIVE
        }
    
    def get_search_result_fields(self, user_context=None):
        """Define fields to include in search results"""
        return [
            'id', 'company_name', 'user__first_name', 'user__last_name',
            'rating', 'total_jobs', 'specializations', 'city'
        ]


class WorkOrder(VisibilityMixin, SoftDeleteMixin, NotifiableMixin, models.Model):
    """
    Work Order model for tracking contractor assignments and job progress
    """
    
    class WorkOrderStatus(models.TextChoices):
        CREATED = 'created', 'Created'
        ASSIGNED = 'assigned', 'Assigned'
        ACCEPTED = 'accepted', 'Accepted'
        IN_PROGRESS = 'in_progress', 'In Progress'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        REJECTED = 'rejected', 'Rejected'
    
    # Core work order information
    work_order_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique work order identifier"
    )
    maintenance_request = models.ForeignKey(
        MaintenanceRequest,
        on_delete=models.CASCADE,
        related_name='work_orders',
        help_text="Associated maintenance request"
    )
    contractor = models.ForeignKey(
        Contractor,
        on_delete=models.CASCADE,
        related_name='work_orders',
        null=True,
        blank=True,
        help_text="Assigned contractor"
    )
    
    # Work details
    title = models.CharField(
        max_length=200,
        help_text="Work order title"
    )
    description = models.TextField(
        help_text="Detailed work description"
    )
    status = models.CharField(
        max_length=20,
        choices=WorkOrderStatus.choices,
        default=WorkOrderStatus.CREATED,
        help_text="Current work order status"
    )
    
    # Scheduling
    scheduled_date = models.DateField(
        null=True,
        blank=True,
        help_text="Scheduled work date"
    )
    scheduled_time = models.TimeField(
        null=True,
        blank=True,
        help_text="Scheduled work time"
    )
    estimated_duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Estimated work duration"
    )
    
    # Cost and materials
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Estimated cost"
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Actual cost"
    )
    materials_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost of materials"
    )
    labor_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Cost of labor"
    )
    
    # Work completion details
    work_performed = models.TextField(
        blank=True,
        help_text="Description of work performed"
    )
    materials_used = models.JSONField(
        default=list,
        help_text="List of materials used"
    )
    before_images = models.JSONField(
        default=list,
        help_text="Before work images"
    )
    after_images = models.JSONField(
        default=list,
        help_text="After work images"
    )
    
    # Quality and feedback
    rating = models.PositiveIntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating given by tenant/landlord (1-5)"
    )
    feedback = models.TextField(
        blank=True,
        help_text="Feedback from tenant/landlord"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When work order was assigned"
    )
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When work started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When work was completed"
    )
    
    class Meta:
        db_table = 'work_orders'
        verbose_name = 'Work Order'
        verbose_name_plural = 'Work Orders'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['work_order_number']),
            models.Index(fields=['status']),
            models.Index(fields=['contractor']),
            models.Index(fields=['maintenance_request']),
            models.Index(fields=['scheduled_date']),
        ]
    
    def __str__(self):
        return f"{self.work_order_number} - {self.title}"
    
    @property
    def is_overdue(self):
        """Check if work order is overdue"""
        if self.scheduled_date and self.status not in [self.WorkOrderStatus.COMPLETED, self.WorkOrderStatus.CANCELLED]:
            return self.scheduled_date < date.today()
        return False
    
    @property
    def total_cost(self):
        """Calculate total cost (materials + labor)"""
        return self.materials_cost + self.labor_cost
    
    def assign_contractor(self, contractor):
        """Assign contractor to work order"""
        self.contractor = contractor
        self.status = self.WorkOrderStatus.ASSIGNED
        self.assigned_at = timezone.now()
        self.save()
    
    def mark_completed(self, work_performed, materials_used=None, actual_cost=None):
        """Mark work order as completed"""
        self.status = self.WorkOrderStatus.COMPLETED
        self.work_performed = work_performed
        self.completed_at = timezone.now()
        
        if materials_used:
            self.materials_used = materials_used
        if actual_cost:
            self.actual_cost = actual_cost
        
        self.save()
        
        # Update contractor rating
        if self.contractor:
            self.contractor.update_rating()
    
    # NotifiableMixin implementation
    def get_notification_recipients(self, notification_type, context=None):
        """Define who should receive notifications about this work order"""
        recipients = []
        
        # Always notify maintenance request stakeholders
        recipients.extend([
            self.maintenance_request.tenant,
            self.maintenance_request.landlord
        ])
        
        # Include assigned contractor
        if self.contractor:
            recipients.append(self.contractor.user)
        
        return recipients
    
    def should_trigger_notification(self, field_name, old_value, new_value):
        """Determine if field changes should trigger notifications"""
        notification_fields = {
            'status': 'work_order_status_changed',
            'contractor': 'work_order_assigned',
            'scheduled_date': 'work_order_scheduled',
            'completed_at': 'work_order_completed'
        }
        
        return field_name in notification_fields


# Signal handlers for automatic work order creation and updates
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
import uuid


@receiver(pre_save, sender=MaintenanceRequest)
def generate_request_number(sender, instance, **kwargs):
    """Generate unique request number if not provided"""
    if not instance.request_number:
        instance.request_number = f"MR-{uuid.uuid4().hex[:8].upper()}"


@receiver(pre_save, sender=WorkOrder)
def generate_work_order_number(sender, instance, **kwargs):
    """Generate unique work order number if not provided"""
    if not instance.work_order_number:
        instance.work_order_number = f"WO-{uuid.uuid4().hex[:8].upper()}"


@receiver(post_save, sender=MaintenanceRequest)
def create_work_order(sender, instance, created, **kwargs):
    """Automatically create work order when maintenance request is acknowledged"""
    if not created and instance.status == MaintenanceRequest.RequestStatus.ACKNOWLEDGED:
        # Check if work order already exists
        if not instance.work_orders.exists():
            WorkOrder.objects.create(
                maintenance_request=instance,
                title=instance.title,
                description=instance.description,
                estimated_cost=instance.estimated_cost,
                scheduled_date=instance.scheduled_date,
                scheduled_time=instance.scheduled_time
            )


@receiver(post_save, sender=WorkOrder)
def update_maintenance_request_status(sender, instance, **kwargs):
    """Update maintenance request status based on work order status"""
    maintenance_request = instance.maintenance_request
    
    if instance.status == WorkOrder.WorkOrderStatus.ASSIGNED:
        maintenance_request.status = MaintenanceRequest.RequestStatus.ASSIGNED
    elif instance.status == WorkOrder.WorkOrderStatus.IN_PROGRESS:
        maintenance_request.status = MaintenanceRequest.RequestStatus.IN_PROGRESS
    elif instance.status == WorkOrder.WorkOrderStatus.COMPLETED:
        maintenance_request.status = MaintenanceRequest.RequestStatus.COMPLETED
        maintenance_request.completed_at = instance.completed_at
        maintenance_request.actual_cost = instance.actual_cost
    
    maintenance_request.save()
