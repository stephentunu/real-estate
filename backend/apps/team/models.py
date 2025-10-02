from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin, SearchableMixin

User = get_user_model()


class TeamDepartment(VisibilityMixin, SoftDeleteMixin, models.Model):
    """
    Team department model for organizing team members
    Following 3NF principles for database design
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the department"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the department"
    )
    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Hex color code for the department"
    )
    
    class Meta:
        db_table = 'team_department'
        verbose_name = 'Team Department'
        verbose_name_plural = 'Team Departments'
        indexes = [
            models.Index(fields=['name']),
        ]
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name
    
    @property
    def members_count(self):
        """Get the number of active members in this department"""
        return self.members.filter(is_active=True, is_deleted=False).count()


class TeamMember(VisibilityMixin, SoftDeleteMixin, SearchableMixin, models.Model):
    """
    Team member model for managing team information
    Following 3NF principles for database design
    """
    
    class PositionChoices(models.TextChoices):
        CEO = 'ceo', 'Chief Executive Officer'
        CTO = 'cto', 'Chief Technology Officer'
        CFO = 'cfo', 'Chief Financial Officer'
        MANAGER = 'manager', 'Manager'
        SENIOR_DEVELOPER = 'senior_developer', 'Senior Developer'
        DEVELOPER = 'developer', 'Developer'
        JUNIOR_DEVELOPER = 'junior_developer', 'Junior Developer'
        DESIGNER = 'designer', 'Designer'
        MARKETING = 'marketing', 'Marketing Specialist'
        SALES = 'sales', 'Sales Representative'
        HR = 'hr', 'Human Resources'
        SUPPORT = 'support', 'Customer Support'
        OTHER = 'other', 'Other'
    
    # Basic Information
    first_name = models.CharField(
        max_length=50,
        help_text="First name of the team member"
    )
    last_name = models.CharField(
        max_length=50,
        help_text="Last name of the team member"
    )
    email = models.EmailField(
        unique=True,
        help_text="Email address of the team member"
    )
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex],
        max_length=17,
        blank=True,
        help_text="Phone number of the team member"
    )
    
    # Professional Information
    position = models.CharField(
        max_length=50,
        choices=PositionChoices.choices,
        help_text="Position/role of the team member"
    )
    custom_position = models.CharField(
        max_length=100,
        blank=True,
        help_text="Custom position title if 'Other' is selected"
    )
    department = models.ForeignKey(
        TeamDepartment,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text="Department the team member belongs to"
    )
    bio = models.TextField(
        blank=True,
        help_text="Biography or description of the team member"
    )
    
    # Media
    profile_image = models.ImageField(
        upload_to='team/profiles/',
        blank=True,
        null=True,
        help_text="Profile image of the team member"
    )
    
    # Employment Details
    hire_date = models.DateField(
        blank=True,
        null=True,
        help_text="Date when the team member was hired"
    )
    salary = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Salary of the team member (confidential)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the team member is currently active"
    )
    
    # Social Media Links
    linkedin_url = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL"
    )
    twitter_url = models.URLField(
        blank=True,
        help_text="Twitter profile URL"
    )
    github_url = models.URLField(
        blank=True,
        help_text="GitHub profile URL"
    )
    website_url = models.URLField(
        blank=True,
        help_text="Personal website URL"
    )
    
    # Display Settings
    display_order = models.PositiveIntegerField(
        default=0,
        help_text="Order in which to display this team member"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this team member should be featured"
    )
    
    # User Account Link (optional)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_profile',
        help_text="Linked user account (if applicable)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Searchable fields for full-text search
    searchable_fields = ['first_name', 'last_name', 'position', 'custom_position', 'bio']
    
    class Meta:
        db_table = 'team_member'
        verbose_name = 'Team Member'
        verbose_name_plural = 'Team Members'
        indexes = [
            models.Index(fields=['first_name', 'last_name']),
            models.Index(fields=['email']),
            models.Index(fields=['position']),
            models.Index(fields=['department']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['display_order']),
        ]
        ordering = ['display_order', 'first_name', 'last_name']
    
    def __str__(self) -> str:
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        """Get the full name of the team member"""
        return f"{self.first_name} {self.last_name}"
    
    @property
    def display_position(self):
        """Get the display position (custom if available, otherwise standard)"""
        if self.position == self.PositionChoices.OTHER and self.custom_position:
            return self.custom_position
        return self.get_position_display()
    
    def get_absolute_url(self):
        """Get the absolute URL for this team member"""
        return f"/team/{self.id}/"
    
    def clean(self):
        """Validate the model data"""
        from django.core.exceptions import ValidationError
        
        # If position is 'other', custom_position should be provided
        if self.position == self.PositionChoices.OTHER and not self.custom_position:
            raise ValidationError({
                'custom_position': 'Custom position is required when position is set to "Other".'
            })
        
        # If position is not 'other', custom_position should be empty
        if self.position != self.PositionChoices.OTHER and self.custom_position:
            raise ValidationError({
                'custom_position': 'Custom position should only be set when position is "Other".'
            })


class TeamAchievement(VisibilityMixin, SoftDeleteMixin, models.Model):
    """
    Team achievement model for tracking team accomplishments
    Following 3NF principles for database design
    """
    
    title = models.CharField(
        max_length=200,
        help_text="Title of the achievement"
    )
    description = models.TextField(
        help_text="Description of the achievement"
    )
    date_achieved = models.DateField(
        help_text="Date when the achievement was accomplished"
    )
    team_members = models.ManyToManyField(
        TeamMember,
        related_name='achievements',
        blank=True,
        help_text="Team members involved in this achievement"
    )
    image = models.ImageField(
        upload_to='team/achievements/',
        blank=True,
        null=True,
        help_text="Image related to the achievement"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this achievement should be featured"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'team_achievement'
        verbose_name = 'Team Achievement'
        verbose_name_plural = 'Team Achievements'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['date_achieved']),
            models.Index(fields=['is_featured']),
        ]
        ordering = ['-date_achieved']
    
    def __str__(self) -> str:
        return self.title
    
    @property
    def members_count(self):
        """Get the number of team members involved in this achievement"""
        return self.team_members.count()
