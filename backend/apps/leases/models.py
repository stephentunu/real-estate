from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from datetime import date, timedelta
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin, NotifiableMixin


class LeaseTemplate(VisibilityMixin, SoftDeleteMixin, models.Model):
    """
    Lease template model for creating standardized lease agreements
    Allows landlords and agents to create reusable lease templates
    """
    
    class TemplateType(models.TextChoices):
        RESIDENTIAL = 'residential', 'Residential'
        COMMERCIAL = 'commercial', 'Commercial'
        INDUSTRIAL = 'industrial', 'Industrial'
        RETAIL = 'retail', 'Retail'
        OFFICE = 'office', 'Office'
    
    # Template identification
    name = models.CharField(
        max_length=200,
        help_text="Template name for identification"
    )
    description = models.TextField(
        blank=True,
        help_text="Template description and usage notes"
    )
    template_type = models.CharField(
        max_length=20,
        choices=TemplateType.choices,
        default=TemplateType.RESIDENTIAL,
        help_text="Type of lease template"
    )
    
    # Template creator and ownership
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_lease_templates',
        help_text="User who created this template"
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Whether this template is available to all users"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is a default template for the type"
    )
    
    # Default lease terms
    default_lease_duration_months = models.PositiveIntegerField(
        default=12,
        help_text="Default lease duration in months"
    )
    default_notice_period_days = models.PositiveIntegerField(
        default=30,
        help_text="Default notice period in days"
    )
    
    # Default financial terms
    default_security_deposit_months = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=Decimal('1.0'),
        validators=[MinValueValidator(Decimal('0.0')), MaxValueValidator(Decimal('12.0'))],
        help_text="Default security deposit in months of rent"
    )
    
    # Template content
    terms_and_conditions = models.TextField(
        help_text="Standard terms and conditions text"
    )
    special_clauses = models.TextField(
        blank=True,
        help_text="Special clauses or additional terms"
    )
    
    # Default occupancy terms
    default_max_occupants = models.PositiveIntegerField(
        default=2,
        help_text="Default maximum number of occupants"
    )
    default_pets_allowed = models.BooleanField(
        default=False,
        help_text="Default pets policy"
    )
    default_smoking_allowed = models.BooleanField(
        default=False,
        help_text="Default smoking policy"
    )
    default_subletting_allowed = models.BooleanField(
        default=False,
        help_text="Default subletting policy"
    )
    
    # Usage tracking
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this template has been used"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lease_templates'
        verbose_name = 'Lease Template'
        verbose_name_plural = 'Lease Templates'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['template_type']),
            models.Index(fields=['is_public']),
            models.Index(fields=['is_default']),
            models.Index(fields=['created_by']),
            models.Index(fields=['name']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['template_type', 'is_default', 'created_by'],
                condition=models.Q(is_default=True),
                name='unique_default_template_per_type_per_user'
            )
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"
    
    def save(self, *args, **kwargs):
        """Override save to handle default template logic"""
        if self.is_default:
            # Ensure only one default template per type per user
            LeaseTemplate.objects.filter(
                template_type=self.template_type,
                created_by=self.created_by,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        
        super().save(*args, **kwargs)
    
    @property
    def is_popular(self):
        """Check if template is popular based on usage"""
        return self.usage_count >= 10
    
    def increment_usage(self):
        """Increment usage count when template is used"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
    
    def get_notification_recipients(self, notification_type):
        """Get recipients for template-related notifications"""
        recipients = []
        
        # Always notify creator
        recipients.append(self.created_by)
        
        return recipients


class Lease(VisibilityMixin, SoftDeleteMixin, NotifiableMixin, models.Model):
    """
    Main Lease model with enhanced capabilities:
    - Visibility controls for lease access
    - Soft deletion with retention policies
    - Notification system integration
    - Comprehensive lease management
    """
    
    class LeaseStatus(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        ACTIVE = 'active', 'Active'
        EXPIRED = 'expired', 'Expired'
        TERMINATED = 'terminated', 'Terminated'
        RENEWED = 'renewed', 'Renewed'
        CANCELLED = 'cancelled', 'Cancelled'
    
    class LeaseType(models.TextChoices):
        RESIDENTIAL = 'residential', 'Residential'
        COMMERCIAL = 'commercial', 'Commercial'
        INDUSTRIAL = 'industrial', 'Industrial'
        RETAIL = 'retail', 'Retail'
        OFFICE = 'office', 'Office'
    
    # Core lease information
    property_ref = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='leases',
        help_text="Property being leased"
    )
    tenant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tenant_leases',
        help_text="Tenant user"
    )
    landlord = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='landlord_leases',
        help_text="Landlord user"
    )
    agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_leases',
        help_text="Managing agent (optional)"
    )
    
    # Lease details
    lease_number = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique lease identifier"
    )
    lease_type = models.CharField(
        max_length=20,
        choices=LeaseType.choices,
        default=LeaseType.RESIDENTIAL,
        help_text="Type of lease"
    )
    status = models.CharField(
        max_length=20,
        choices=LeaseStatus.choices,
        default=LeaseStatus.DRAFT,
        help_text="Current lease status"
    )
    
    # Lease period
    start_date = models.DateField(
        help_text="Lease start date"
    )
    end_date = models.DateField(
        help_text="Lease end date"
    )
    notice_period_days = models.PositiveIntegerField(
        default=30,
        help_text="Notice period required for termination (in days)"
    )
    
    # Financial terms
    monthly_rent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Monthly rent amount"
    )
    security_deposit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        help_text="Security deposit amount"
    )
    currency = models.CharField(
        max_length=3,
        default='KES',
        help_text="Currency code (e.g., KES, USD)"
    )
    
    # Lease terms and conditions
    terms_and_conditions = models.TextField(
        blank=True,
        help_text="Additional terms and conditions"
    )
    special_clauses = models.TextField(
        blank=True,
        help_text="Special clauses or agreements"
    )
    
    # Renewal options
    auto_renewal = models.BooleanField(
        default=False,
        help_text="Whether lease auto-renews"
    )
    renewal_notice_days = models.PositiveIntegerField(
        default=60,
        help_text="Days before expiry to give renewal notice"
    )
    
    # Document management
    lease_document = models.FileField(
        upload_to='leases/documents/',
        blank=True,
        null=True,
        help_text="Signed lease agreement document"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the lease was signed"
    )
    
    class Meta:
        db_table = 'leases'
        verbose_name = 'Lease'
        verbose_name_plural = 'Leases'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['lease_number']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['tenant']),
            models.Index(fields=['landlord']),
            models.Index(fields=['property_ref']),
        ]
    
    def __str__(self):
        return f"Lease {self.lease_number} - {self.property_ref.title}"
    
    @property
    def is_active(self):
        """Check if lease is currently active"""
        today = date.today()
        return (
            self.status == self.LeaseStatus.ACTIVE and
            self.start_date <= today <= self.end_date
        )
    
    @property
    def days_remaining(self):
        """Calculate days remaining in lease"""
        if self.end_date:
            return (self.end_date - date.today()).days
        return None
    
    @property
    def is_expiring_soon(self):
        """Check if lease is expiring within notice period"""
        days_remaining = self.days_remaining
        return days_remaining is not None and 0 <= days_remaining <= self.notice_period_days
    
    def calculate_total_rent(self):
        """Calculate total rent for the lease period"""
        if self.start_date and self.end_date:
            months = (self.end_date.year - self.start_date.year) * 12 + \
                    (self.end_date.month - self.start_date.month)
            return self.monthly_rent * months
        return Decimal('0.00')
    
    # NotifiableMixin implementation
    def get_notification_recipients(self, notification_type, context=None):
        """Define who should receive notifications about this lease"""
        recipients = []
        
        # Always notify tenant and landlord
        recipients.extend([self.tenant, self.landlord])
        
        # Include agent if assigned
        if self.agent:
            recipients.append(self.agent)
        
        # Admin notifications for certain events
        if notification_type in ['lease_created', 'lease_terminated']:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_users = User.objects.filter(role='admin', is_active=True)
            recipients.extend(admin_users)
        
        return recipients
    
    def should_trigger_notification(self, field_name, old_value, new_value):
        """Determine if field changes should trigger notifications"""
        notification_fields = {
            'status': 'lease_status_changed',
            'monthly_rent': 'rent_changed',
            'end_date': 'lease_extended',
            'signed_at': 'lease_signed'
        }
        
        return field_name in notification_fields


class LeaseTerms(VisibilityMixin, SoftDeleteMixin, models.Model):
    """
    Detailed lease terms and conditions
    Separated for better organization and flexibility
    """
    
    lease = models.OneToOneField(
        Lease,
        on_delete=models.CASCADE,
        related_name='terms',
        help_text="Associated lease"
    )
    
    # Occupancy terms
    max_occupants = models.PositiveIntegerField(
        default=2,
        help_text="Maximum number of occupants allowed"
    )
    pets_allowed = models.BooleanField(
        default=False,
        help_text="Whether pets are allowed"
    )
    pet_deposit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Additional deposit for pets"
    )
    
    # Maintenance responsibilities
    tenant_maintenance_responsibilities = models.TextField(
        blank=True,
        help_text="What maintenance tenant is responsible for"
    )
    landlord_maintenance_responsibilities = models.TextField(
        blank=True,
        help_text="What maintenance landlord is responsible for"
    )
    
    # Utilities and services
    utilities_included = models.JSONField(
        default=list,
        help_text="List of utilities included in rent"
    )
    utilities_tenant_pays = models.JSONField(
        default=list,
        help_text="List of utilities tenant must pay separately"
    )
    
    # Restrictions and rules
    smoking_allowed = models.BooleanField(
        default=False,
        help_text="Whether smoking is allowed"
    )
    subletting_allowed = models.BooleanField(
        default=False,
        help_text="Whether subletting is allowed"
    )
    commercial_use_allowed = models.BooleanField(
        default=False,
        help_text="Whether commercial use is allowed"
    )
    
    # Parking and storage
    parking_spaces_included = models.PositiveIntegerField(
        default=0,
        help_text="Number of parking spaces included"
    )
    storage_included = models.BooleanField(
        default=False,
        help_text="Whether storage space is included"
    )
    
    # Late fees and penalties
    late_fee_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Late payment fee amount"
    )
    late_fee_grace_days = models.PositiveIntegerField(
        default=5,
        help_text="Grace period before late fees apply"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'lease_terms'
        verbose_name = 'Lease Terms'
        verbose_name_plural = 'Lease Terms'
    
    def __str__(self):
        return f"Terms for {self.lease.lease_number}"


class PaymentSchedule(VisibilityMixin, SoftDeleteMixin, NotifiableMixin, models.Model):
    """
    Payment schedule for lease payments
    Tracks rent payments, due dates, and payment history
    """
    
    class PaymentType(models.TextChoices):
        RENT = 'rent', 'Monthly Rent'
        DEPOSIT = 'deposit', 'Security Deposit'
        LATE_FEE = 'late_fee', 'Late Fee'
        UTILITY = 'utility', 'Utility Payment'
        MAINTENANCE = 'maintenance', 'Maintenance Fee'
        OTHER = 'other', 'Other'
    
    class PaymentStatus(models.TextChoices):
        PENDING = 'pending', 'Pending'
        PAID = 'paid', 'Paid'
        OVERDUE = 'overdue', 'Overdue'
        PARTIAL = 'partial', 'Partially Paid'
        CANCELLED = 'cancelled', 'Cancelled'
    
    lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        related_name='payment_schedules',
        help_text="Associated lease"
    )
    
    # Payment details
    payment_type = models.CharField(
        max_length=20,
        choices=PaymentType.choices,
        default=PaymentType.RENT,
        help_text="Type of payment"
    )
    amount_due = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Amount due for this payment"
    )
    amount_paid = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Amount actually paid"
    )
    
    # Dates
    due_date = models.DateField(
        help_text="Payment due date"
    )
    paid_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date payment was made"
    )
    
    # Status and tracking
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        help_text="Payment status"
    )
    
    # Payment method and reference
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        help_text="Payment method used (e.g., Bank Transfer, M-Pesa)"
    )
    payment_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Payment reference or transaction ID"
    )
    
    # Notes and receipts
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this payment"
    )
    receipt = models.FileField(
        upload_to='leases/receipts/',
        blank=True,
        null=True,
        help_text="Payment receipt or proof"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'payment_schedules'
        verbose_name = 'Payment Schedule'
        verbose_name_plural = 'Payment Schedules'
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['due_date']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_type']),
            models.Index(fields=['lease']),
        ]
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - {self.due_date} ({self.get_status_display()})"
    
    @property
    def is_overdue(self):
        """Check if payment is overdue"""
        return (
            self.status in [self.PaymentStatus.PENDING, self.PaymentStatus.PARTIAL] and
            self.due_date < date.today()
        )
    
    @property
    def days_overdue(self):
        """Calculate days overdue"""
        if self.is_overdue:
            return (date.today() - self.due_date).days
        return 0
    
    @property
    def balance_remaining(self):
        """Calculate remaining balance"""
        return self.amount_due - self.amount_paid
    
    def mark_as_paid(self, amount_paid=None, payment_date=None, payment_method=None, reference=None):
        """Mark payment as paid with details"""
        if amount_paid is None:
            amount_paid = self.amount_due
        
        self.amount_paid = amount_paid
        self.paid_date = payment_date or date.today()
        
        if payment_method:
            self.payment_method = payment_method
        if reference:
            self.payment_reference = reference
        
        # Update status based on amount paid
        if self.amount_paid >= self.amount_due:
            self.status = self.PaymentStatus.PAID
        elif self.amount_paid > 0:
            self.status = self.PaymentStatus.PARTIAL
        
        self.save()
    
    # NotifiableMixin implementation
    def get_notification_recipients(self, notification_type, context=None):
        """Define who should receive notifications about this payment"""
        recipients = []
        
        # Always notify tenant and landlord
        recipients.extend([self.lease.tenant, self.lease.landlord])
        
        # Include agent if assigned
        if self.lease.agent:
            recipients.append(self.lease.agent)
        
        return recipients
    
    def should_trigger_notification(self, field_name, old_value, new_value):
        """Determine if field changes should trigger notifications"""
        notification_fields = {
            'status': 'payment_status_changed',
            'amount_paid': 'payment_received',
            'due_date': 'payment_due_date_changed'
        }
        
        return field_name in notification_fields


# Signal handlers for automatic payment schedule generation
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from calendar import monthrange


@receiver(post_save, sender=Lease)
def create_payment_schedule(sender, instance, created, **kwargs):
    """Automatically create payment schedule when lease is created or activated"""
    if created or (instance.status == Lease.LeaseStatus.ACTIVE and 
                   not instance.payment_schedules.exists()):
        
        # Create security deposit payment if applicable
        if instance.security_deposit > 0:
            PaymentSchedule.objects.create(
                lease=instance,
                payment_type=PaymentSchedule.PaymentType.DEPOSIT,
                amount_due=instance.security_deposit,
                due_date=instance.start_date,
                status=PaymentSchedule.PaymentStatus.PENDING
            )
        
        # Create monthly rent payments
        current_date = instance.start_date
        while current_date <= instance.end_date:
            PaymentSchedule.objects.create(
                lease=instance,
                payment_type=PaymentSchedule.PaymentType.RENT,
                amount_due=instance.monthly_rent,
                due_date=current_date,
                status=PaymentSchedule.PaymentStatus.PENDING
            )
            # Move to next month
            if current_date.month == 12:
                current_date = current_date.replace(year=current_date.year + 1, month=1)
            else:
                current_date = current_date.replace(month=current_date.month + 1)
