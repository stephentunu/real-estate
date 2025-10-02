from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import EmailValidator
from django.utils import timezone
import uuid

User = get_user_model()

class NewsletterSubscription(models.Model):
    """
    Newsletter subscription model for managing email subscriptions
    Follows 3NF design principles
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    user = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='newsletter_subscriptions'
    )
    is_active = models.BooleanField(default=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    unsubscribed_at = models.DateTimeField(null=True, blank=True)
    confirmation_token = models.CharField(max_length=255, unique=True, null=True, blank=True)
    is_confirmed = models.BooleanField(default=False)
    
    # Subscription preferences
    frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly'),
        ],
        default='weekly'
    )
    
    # Categories of interest
    categories = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'newsletter_subscriptions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['is_active']),
            models.Index(fields=['is_confirmed']),
        ]
    
    def __str__(self):
        return f"{self.email} - {'Active' if self.is_active else 'Inactive'}"
    
    def unsubscribe(self):
        """Unsubscribe user from newsletter"""
        self.is_active = False
        self.unsubscribed_at = timezone.now()
        self.save()
    
    def confirm_subscription(self):
        """Confirm email subscription"""
        self.is_confirmed = True
        self.confirmation_token = None
        self.save()

class NewsletterCampaign(models.Model):
    """
    Newsletter campaign model for managing email campaigns
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    content = models.TextField()
    html_content = models.TextField(blank=True)
    
    # Campaign status
    status = models.CharField(
        max_length=20,
        choices=[
            ('draft', 'Draft'),
            ('scheduled', 'Scheduled'),
            ('sending', 'Sending'),
            ('sent', 'Sent'),
            ('cancelled', 'Cancelled'),
        ],
        default='draft'
    )
    
    # Targeting
    target_categories = models.JSONField(default=list, blank=True)
    target_frequency = models.CharField(
        max_length=20,
        choices=[
            ('all', 'All Subscribers'),
            ('daily', 'Daily Subscribers'),
            ('weekly', 'Weekly Subscribers'),
            ('monthly', 'Monthly Subscribers'),
        ],
        default='all'
    )
    
    # Scheduling
    scheduled_at = models.DateTimeField(null=True, blank=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    # Statistics
    total_recipients = models.PositiveIntegerField(default=0)
    total_sent = models.PositiveIntegerField(default=0)
    total_delivered = models.PositiveIntegerField(default=0)
    total_opened = models.PositiveIntegerField(default=0)
    total_clicked = models.PositiveIntegerField(default=0)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_campaigns'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'newsletter_campaigns'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['scheduled_at']),
            models.Index(fields=['created_by']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.status}"

class NewsletterDelivery(models.Model):
    """
    Newsletter delivery tracking model
    Tracks individual email deliveries for analytics
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    campaign = models.ForeignKey(
        NewsletterCampaign,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    subscription = models.ForeignKey(
        NewsletterSubscription,
        on_delete=models.CASCADE,
        related_name='deliveries'
    )
    
    # Delivery status
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('delivered', 'Delivered'),
            ('bounced', 'Bounced'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )
    
    # Tracking
    sent_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    opened_at = models.DateTimeField(null=True, blank=True)
    clicked_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'newsletter_deliveries'
        ordering = ['-created_at']
        unique_together = ['campaign', 'subscription']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['campaign']),
            models.Index(fields=['subscription']),
        ]
    
    def __str__(self):
        return f"{self.campaign.title} -> {self.subscription.email} ({self.status})"
