from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.exceptions import ValidationError
import uuid


class VisibilityMixin(models.Model):
    """
    Mixin to provide granular visibility control across all entities.
    Implements the visibility levels defined in the platform requirements:
    - PUBLIC: Visible to all users, even unauthenticated
    - REGISTERED: Visible to all registered users
    - AGENCY_ONLY: Visible only to managing agency staff
    - LANDLORD_ONLY: Visible only to property owner(s)
    - TENANT_ONLY: Visible only to current tenant
    - CLASSIFIED: Visible only to specific users/groups
    - SYSTEM: Visible only to platform staff
    """
    
    class VisibilityLevel(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        REGISTERED = 'REGISTERED', 'Registered Users'
        AGENCY_ONLY = 'AGENCY_ONLY', 'Agency Only'
        LANDLORD_ONLY = 'LANDLORD_ONLY', 'Landlord Only'
        TENANT_ONLY = 'TENANT_ONLY', 'Tenant Only'
        CLASSIFIED = 'CLASSIFIED', 'Classified'
        SYSTEM = 'SYSTEM', 'System Only'
    
    visibility_level = models.CharField(
        max_length=20,
        choices=VisibilityLevel.choices,
        default=VisibilityLevel.REGISTERED,
        help_text="Visibility level for this record",
        db_index=True
    )
    
    # For PostgreSQL, use ArrayField. For SQLite development, use TextField with JSON serialization
    visibility_groups = models.TextField(
        blank=True,
        default='[]',
        help_text="JSON array of group names with access (e.g., ['landlords', 'agents'])"
    )
    
    visibility_users = models.TextField(
        blank=True,
        default='[]',
        help_text="JSON array of specific user IDs with access"
    )
    
    visibility_exceptions = models.JSONField(
        blank=True,
        default=dict,
        help_text="Complex visibility rules as JSON (e.g., {'tenant': 'LEASE.active'})"
    )
    
    class Meta:
        abstract = True
    
    def can_view(self, user):
        """
        Check if a user can view this record based on visibility settings.
        
        Args:
            user: User instance or None for anonymous users
            
        Returns:
            bool: True if user can view this record
        """
        # PUBLIC level - everyone can view
        if self.visibility_level == self.VisibilityLevel.PUBLIC:
            return True
        
        # Anonymous users can only see PUBLIC content
        if not user or not user.is_authenticated:
            return False
        
        # SYSTEM level - only superusers
        if self.visibility_level == self.VisibilityLevel.SYSTEM:
            return user.is_superuser
        
        # REGISTERED level - any authenticated user
        if self.visibility_level == self.VisibilityLevel.REGISTERED:
            return True
        
        # Check specific user access
        import json
        try:
            visibility_users = json.loads(self.visibility_users or '[]')
            if str(user.id) in visibility_users:
                return True
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Check group access
        try:
            visibility_groups = json.loads(self.visibility_groups or '[]')
            user_groups = user.groups.values_list('name', flat=True)
            if any(group in visibility_groups for group in user_groups):
                return True
        except (json.JSONDecodeError, AttributeError):
            pass
        
        # Role-based visibility checks
        if hasattr(user, 'role'):
            if self.visibility_level == self.VisibilityLevel.AGENCY_ONLY:
                return user.role == 'agent'
            elif self.visibility_level == self.VisibilityLevel.LANDLORD_ONLY:
                return user.role in ['seller', 'admin']  # Sellers are landlords
            elif self.visibility_level == self.VisibilityLevel.TENANT_ONLY:
                return user.role == 'buyer'  # Buyers are tenants
        
        # Check visibility exceptions (complex rules)
        if self.visibility_exceptions:
            return self._check_visibility_exceptions(user)
        
        # Default deny
        return False
    
    def _check_visibility_exceptions(self, user):
        """
        Check complex visibility exception rules.
        This is a simplified implementation - in production, you'd want
        a more sophisticated rule engine.
        """
        # This would be expanded based on specific business rules
        # For now, return False to maintain security
        return False
    
    @classmethod
    def get_visible_queryset(cls, user, queryset=None):
        """
        Filter queryset to only include records visible to the user.
        
        Args:
            user: User instance or None
            queryset: Optional base queryset, defaults to cls.objects.all()
            
        Returns:
            QuerySet: Filtered queryset
        """
        if queryset is None:
            queryset = cls.objects.all()
        
        # Anonymous users only see PUBLIC content
        if not user or not user.is_authenticated:
            return queryset.filter(visibility_level=cls.VisibilityLevel.PUBLIC)
        
        # Superusers see everything
        if user.is_superuser:
            return queryset
        
        # Build visibility filter conditions
        from django.db.models import Q
        
        conditions = Q(visibility_level=cls.VisibilityLevel.PUBLIC)
        conditions |= Q(visibility_level=cls.VisibilityLevel.REGISTERED)
        
        # Add role-based conditions
        if hasattr(user, 'role'):
            if user.role == 'agent':
                conditions |= Q(visibility_level=cls.VisibilityLevel.AGENCY_ONLY)
            elif user.role in ['seller', 'admin']:
                conditions |= Q(visibility_level=cls.VisibilityLevel.LANDLORD_ONLY)
            elif user.role == 'buyer':
                conditions |= Q(visibility_level=cls.VisibilityLevel.TENANT_ONLY)
        
        # Add user-specific access
        conditions |= Q(visibility_users__icontains=f'"{user.id}"')
        
        # Add group-based access
        user_groups = list(user.groups.values_list('name', flat=True))
        for group in user_groups:
            conditions |= Q(visibility_groups__icontains=f'"{group}"')
        
        return queryset.filter(conditions)


class SoftDeleteMixin(models.Model):
    """
    Mixin to provide soft deletion functionality with retention policies.
    Preserves data integrity while supporting user expectations of 'deletion'.
    """
    
    is_deleted = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether this record has been soft deleted"
    )
    
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this record was deleted"
    )
    
    deleted_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(class)s_deleted_records',
        help_text="User who deleted this record"
    )
    
    retention_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this record will be permanently deleted"
    )
    
    class Meta:
        abstract = True
    
    def soft_delete(self, user=None, retention_days=None):
        """
        Soft delete this record.
        
        Args:
            user: User performing the deletion
            retention_days: Override default retention period
        """
        if self.is_deleted:
            return  # Already deleted
        
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.deleted_by = user
        
        # Set retention period
        if retention_days is None:
            retention_days = self.get_default_retention_days()
        
        if retention_days > 0:
            self.retention_until = timezone.now() + timezone.timedelta(days=retention_days)
        
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'retention_until'])
    
    def restore(self, user=None):
        """
        Restore a soft-deleted record.
        
        Args:
            user: User performing the restoration
        """
        if not self.is_deleted:
            return  # Not deleted
        
        self.is_deleted = False
        self.deleted_at = None
        self.deleted_by = None
        self.retention_until = None
        
        self.save(update_fields=['is_deleted', 'deleted_at', 'deleted_by', 'retention_until'])
    
    def get_default_retention_days(self):
        """
        Get default retention period for this model.
        Override in subclasses for model-specific retention policies.
        
        Returns:
            int: Number of days to retain deleted records
        """
        # Default retention policies based on model type
        model_name = self.__class__.__name__.lower()
        
        retention_policies = {
            'user': 90,
            'property': 2555,  # 7 years
            'lease': 2555,     # 7 years
            'payment': 3650,   # 10 years
            'maintenancerequest': 1095,  # 3 years
            'document': 2555,  # 7 years default
        }
        
        return retention_policies.get(model_name, 90)  # Default 90 days
    
    @classmethod
    def get_active_queryset(cls, queryset=None):
        """
        Get queryset excluding soft-deleted records.
        
        Args:
            queryset: Optional base queryset
            
        Returns:
            QuerySet: Filtered queryset excluding deleted records
        """
        if queryset is None:
            queryset = cls.objects.all()
        
        return queryset.filter(is_deleted=False)
    
    @classmethod
    def get_deleted_queryset(cls, queryset=None):
        """
        Get queryset of only soft-deleted records.
        
        Args:
            queryset: Optional base queryset
            
        Returns:
            QuerySet: Filtered queryset of deleted records
        """
        if queryset is None:
            queryset = cls.objects.all()
        
        return queryset.filter(is_deleted=True)
    
    @classmethod
    def get_expired_records(cls):
        """
        Get records that have exceeded their retention period.
        
        Returns:
            QuerySet: Records ready for permanent deletion
        """
        return cls.objects.filter(
            is_deleted=True,
            retention_until__lte=timezone.now()
        )


class SearchableMixin(models.Model):
    """
    Mixin to provide consistent search functionality across entities.
    Enables high-performance search with customizable fields and boost factors.
    """
    
    search_vector = models.TextField(
        blank=True,
        help_text="Computed search vector for full-text search"
    )
    
    search_metadata = models.JSONField(
        blank=True,
        default=dict,
        help_text="Additional search metadata and configuration"
    )
    
    class Meta:
        abstract = True
    
    @classmethod
    def get_searchable_fields(cls):
        """
        List of fields available for search.
        Override in subclasses to define searchable fields.
        
        Returns:
            list: Field names that can be searched
        """
        return []
    
    @classmethod
    def get_search_boost(cls):
        """
        Field-specific search weighting.
        Override in subclasses to define boost factors.
        
        Returns:
            dict: Field names mapped to boost factors
        """
        return {}
    
    @classmethod
    def get_search_filters(cls):
        """
        Custom filter methods for search.
        Override in subclasses to define custom filters.
        
        Returns:
            dict: Filter names mapped to filter functions
        """
        return {}
    
    @classmethod
    def get_search_result_fields(cls, context=None):
        """
        Fields to return in search results.
        Override in subclasses to define result fields.
        
        Args:
            context: Optional context (e.g., user role) for customization
            
        Returns:
            list: Field names to include in search results
        """
        return ['id']
    
    def update_search_vector(self):
        """
        Update the search vector for this record.
        This would typically use PostgreSQL's full-text search capabilities.
        For SQLite development, we'll use a simple concatenation approach.
        """
        searchable_fields = self.get_searchable_fields()
        search_content = []
        
        for field_name in searchable_fields:
            try:
                # Handle nested field access (e.g., 'features.value')
                if '.' in field_name:
                    # This would need more sophisticated handling for related fields
                    continue
                
                value = getattr(self, field_name, '')
                if value:
                    search_content.append(str(value))
            except AttributeError:
                continue
        
        self.search_vector = ' '.join(search_content).lower()
        
    def save(self, *args, **kwargs):
        """
        Override save to update search vector.
        """
        self.update_search_vector()
        super().save(*args, **kwargs)


class NotifiableMixin(models.Model):
    """
    Mixin to standardize notification handling across critical business events.
    Provides a consistent interface for triggering and managing notifications.
    """
    
    notifications_enabled = models.BooleanField(
        default=True,
        help_text="Whether notifications are enabled for this record"
    )
    
    notification_channels = models.TextField(
        blank=True,
        default='["in_app"]',
        help_text="JSON array of enabled notification channels"
    )
    
    class Meta:
        abstract = True
    
    @classmethod
    def get_notification_events(cls):
        """
        List of notification events for this model.
        Override in subclasses to define notification events.
        
        Returns:
            list: Event names that can trigger notifications
        """
        return []
    
    @classmethod
    def get_notification_recipients(cls, event, instance):
        """
        Determine who should be notified for an event.
        Override in subclasses to define recipient logic.
        
        Args:
            event: Event name
            instance: Model instance that triggered the event
            
        Returns:
            list: User instances who should receive notifications
        """
        return []
    
    @classmethod
    def get_notification_channels(cls, event, user):
        """
        Determine delivery channels for a user.
        Override in subclasses to define channel logic.
        
        Args:
            event: Event name
            user: User who will receive the notification
            
        Returns:
            list: Channel names for notification delivery
        """
        return ['in_app']
    
    @classmethod
    def get_notification_template(cls, event):
        """
        Get message template for an event.
        Override in subclasses to define template logic.
        
        Args:
            event: Event name
            
        Returns:
            str: Template name or identifier
        """
        return f"{cls.__name__.lower()}_{event}"
    
    def trigger_notification(self, event, **kwargs):
        """
        Trigger a notification for this instance.
        
        Args:
            event: Event name
            **kwargs: Additional context for the notification
        """
        if not self.notifications_enabled:
            return
        
        recipients = self.get_notification_recipients(event, self)
        if not recipients:
            return
        
        # This would integrate with your notification system
        # For now, we'll just log the notification
        import logging
        logger = logging.getLogger(__name__)
        
        for recipient in recipients:
            channels = self.get_notification_channels(event, recipient)
            template = self.get_notification_template(event)
            
            logger.info(
                f"Notification triggered: {event} for {recipient} "
                f"via {channels} using template {template}"
            )