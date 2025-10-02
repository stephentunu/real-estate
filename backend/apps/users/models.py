from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin, SearchableMixin, NotifiableMixin


class User(VisibilityMixin, SoftDeleteMixin, SearchableMixin, NotifiableMixin, AbstractUser):
    """
    Custom User model extending Django's AbstractUser with enhanced capabilities:
    - Visibility controls for user profile access
    - Soft deletion with retention policies
    - Full-text search functionality
    - Notification system integration
    - Contact methods and workclass assignments
    Following 3NF principles for database design
    """
    
    class UserRole(models.TextChoices):
        BUYER = 'buyer', 'Buyer'
        SELLER = 'seller', 'Seller'
        AGENT = 'agent', 'Agent'
        ADMIN = 'admin', 'Admin'
        LANDLORD = 'landlord', 'Landlord'
        TENANT = 'tenant', 'Tenant'
        CONTRACTOR = 'contractor', 'Contractor'
        PROPERTY_MANAGER = 'property_manager', 'Property Manager'
    
    class ContactMethod(models.TextChoices):
        EMAIL = 'email', 'Email'
        PHONE = 'phone', 'Phone'
        SMS = 'sms', 'SMS'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        IN_APP = 'in_app', 'In-App Notification'
    
    class WorkClass(models.TextChoices):
        FULL_TIME = 'full_time', 'Full Time'
        PART_TIME = 'part_time', 'Part Time'
        CONTRACT = 'contract', 'Contract'
        FREELANCE = 'freelance', 'Freelance'
        CONSULTANT = 'consultant', 'Consultant'
    
    # Basic user information
    email = models.EmailField(unique=True)
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True,
        help_text="Phone number in international format"
    )
    
    # User role and status
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.BUYER,
        help_text="User role in the system"
    )
    
    # Contact preferences and methods
    preferred_contact_method = models.CharField(
        max_length=20,
        choices=ContactMethod.choices,
        default=ContactMethod.EMAIL,
        help_text="Preferred method for receiving notifications"
    )
    secondary_contact_method = models.CharField(
        max_length=20,
        choices=ContactMethod.choices,
        blank=True,
        help_text="Secondary contact method"
    )
    
    # Professional information
    scheme_code = models.CharField(
        max_length=50,
        blank=True,
        help_text="Professional scheme or certification code"
    )
    work_class = models.CharField(
        max_length=20,
        choices=WorkClass.choices,
        blank=True,
        help_text="Work classification for professional users"
    )
    
    # WhatsApp number (separate from phone for international compatibility)
    whatsapp_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="WhatsApp number for notifications"
    )
    
    # Profile information
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        help_text="User profile picture"
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text="Brief description about the user"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Email verification
    email_verified = models.BooleanField(
        default=False,
        help_text="Whether the user's email has been verified"
    )
    email_verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the email was verified"
    )
    
    # Account status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the user account is active"
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['role']),
            models.Index(fields=['created_at']),
            models.Index(fields=['scheme_code']),
            models.Index(fields=['work_class']),
            models.Index(fields=['preferred_contact_method']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.email})"
    
    def get_full_name(self):
        """Return the user's full name"""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_short_name(self):
        """Return the user's short name"""
        return self.first_name or self.username
    
    # SearchableMixin implementation
    def get_searchable_fields(self):
        """Define fields that should be included in search index"""
        return [
            'username', 'first_name', 'last_name', 'email',
            'bio', 'scheme_code', 'profile__company_name',
            'profile__license_number'
        ]
    
    def get_search_boost(self):
        """Define boost factors for different fields"""
        return {
            'username': 1.2,
            'first_name': 1.1,
            'last_name': 1.1,
            'email': 1.0,
            'scheme_code': 1.3,
            'profile__company_name': 1.2,
            'profile__license_number': 1.1,
            'bio': 0.8
        }
    
    def get_search_filters(self, user_context=None):
        """Define search filters based on user context"""
        filters = {}
        
        if user_context:
            # Role-based filtering
            if user_context.role == self.UserRole.BUYER:
                filters['role__in'] = [self.UserRole.AGENT, self.UserRole.SELLER, self.UserRole.LANDLORD]
            elif user_context.role == self.UserRole.AGENT:
                filters['role__in'] = [self.UserRole.BUYER, self.UserRole.SELLER, self.UserRole.LANDLORD, self.UserRole.AGENT]
        
        return filters
    
    def get_search_result_fields(self, user_context=None):
        """Define which fields to return in search results"""
        base_fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'role', 'avatar', 'created_at'
        ]
        
        if user_context and user_context.role in [self.UserRole.AGENT, self.UserRole.ADMIN]:
            base_fields.extend([
                'phone_number', 'scheme_code', 'work_class',
                'profile__company_name', 'profile__license_number'
            ])
        
        return base_fields
    
    # NotifiableMixin implementation
    def get_notification_recipients(self, notification_type, context=None):
        """Define who should receive notifications about this user"""
        recipients = []
        
        # Self-notifications for account changes
        if notification_type in ['profile_updated', 'password_changed', 'email_verified']:
            recipients.append(self)
        
        # Admin notifications for new registrations
        if notification_type == 'user_registered':
            from django.contrib.auth import get_user_model
            User = get_user_model()
            admin_users = User.objects.filter(role=self.UserRole.ADMIN, is_active=True)
            recipients.extend(admin_users)
        
        return recipients
    
    def should_trigger_notification(self, field_name, old_value, new_value):
        """Determine if field changes should trigger notifications"""
        # Trigger notifications for important field changes
        notification_fields = {
            'email': 'email_changed',
            'role': 'role_changed',
            'is_active': 'account_status_changed',
            'scheme_code': 'certification_updated'
        }
        
        return field_name in notification_fields


class UserProfile(models.Model):
    """
    Extended user profile information
    Separated from User model following 3NF principles
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    
    # Address information
    address_line_1 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Primary address line"
    )
    address_line_2 = models.CharField(
        max_length=255,
        blank=True,
        help_text="Secondary address line (apartment, suite, etc.)"
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City name"
    )
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="State or province"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="Postal or ZIP code"
    )
    country = models.CharField(
        max_length=100,
        blank=True,
        default='Kenya',
        help_text="Country name"
    )
    
    # Professional information (for agents/sellers)
    company_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Company or agency name"
    )
    license_number = models.CharField(
        max_length=100,
        blank=True,
        help_text="Professional license number"
    )
    years_experience = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Years of experience in real estate"
    )
    
    # Social media links
    website = models.URLField(
        blank=True,
        help_text="Personal or company website"
    )
    linkedin_url = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL"
    )
    twitter_url = models.URLField(
        blank=True,
        help_text="Twitter profile URL"
    )
    
    # Preferences
    preferred_language = models.CharField(
        max_length=10,
        default='en',
        help_text="Preferred language code (e.g., 'en', 'sw')"
    )
    timezone = models.CharField(
        max_length=50,
        default='Africa/Nairobi',
        help_text="User's timezone"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'user_profiles'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        indexes = [
            models.Index(fields=['city', 'state']),
            models.Index(fields=['company_name']),
        ]
    
    def __str__(self):
        return f"Profile for {self.user.get_full_name()}"
    
    def get_full_address(self):
        """Return formatted full address"""
        address_parts = [
            self.address_line_1,
            self.address_line_2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ', '.join(filter(None, address_parts))
