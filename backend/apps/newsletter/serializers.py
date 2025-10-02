from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import NewsletterSubscription, NewsletterCampaign, NewsletterDelivery
import secrets
import string

User = get_user_model()

class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletter subscriptions
    """
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = NewsletterSubscription
        fields = [
            'id', 'email', 'user', 'user_email', 'user_name',
            'is_active', 'is_confirmed', 'frequency', 'categories',
            'subscribed_at', 'unsubscribed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'user', 'user_email', 'user_name', 'is_confirmed',
            'subscribed_at', 'unsubscribed_at', 'created_at', 'updated_at'
        ]
    
    def create(self, validated_data):
        """
        Create newsletter subscription with confirmation token
        """
        # Generate confirmation token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        validated_data['confirmation_token'] = token
        
        # Link to user if authenticated
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        
        return super().create(validated_data)

class NewsletterSubscriptionCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating newsletter subscriptions
    """
    class Meta:
        model = NewsletterSubscription
        fields = ['email', 'frequency', 'categories']
    
    def create(self, validated_data):
        """
        Create newsletter subscription with confirmation token
        """
        # Generate confirmation token
        token = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(32))
        validated_data['confirmation_token'] = token
        
        # Link to user if authenticated
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user
        
        return super().create(validated_data)

class NewsletterCampaignSerializer(serializers.ModelSerializer):
    """
    Serializer for newsletter campaigns
    """
    created_by_name = serializers.CharField(source='created_by.get_full_name', read_only=True)
    open_rate = serializers.SerializerMethodField()
    click_rate = serializers.SerializerMethodField()
    
    class Meta:
        model = NewsletterCampaign
        fields = [
            'id', 'title', 'subject', 'content', 'html_content',
            'status', 'target_categories', 'target_frequency',
            'scheduled_at', 'sent_at', 'total_recipients', 'total_sent',
            'total_delivered', 'total_opened', 'total_clicked',
            'open_rate', 'click_rate', 'created_by', 'created_by_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'total_recipients', 'total_sent', 'total_delivered',
            'total_opened', 'total_clicked', 'open_rate', 'click_rate',
            'sent_at', 'created_by', 'created_by_name', 'created_at', 'updated_at'
        ]
    
    def get_open_rate(self, obj):
        """
        Calculate open rate percentage
        """
        if obj.total_sent > 0:
            return round((obj.total_opened / obj.total_sent) * 100, 2)
        return 0.0
    
    def get_click_rate(self, obj):
        """
        Calculate click rate percentage
        """
        if obj.total_sent > 0:
            return round((obj.total_clicked / obj.total_sent) * 100, 2)
        return 0.0
    
    def create(self, validated_data):
        """
        Set created_by to current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

class NewsletterCampaignCreateSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for creating newsletter campaigns
    """
    class Meta:
        model = NewsletterCampaign
        fields = [
            'title', 'subject', 'content', 'html_content',
            'target_categories', 'target_frequency', 'scheduled_at'
        ]
    
    def create(self, validated_data):
        """
        Set created_by to current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user
        return super().create(validated_data)

class NewsletterDeliverySerializer(serializers.ModelSerializer):
    """
    Serializer for newsletter deliveries
    """
    campaign_title = serializers.CharField(source='campaign.title', read_only=True)
    subscription_email = serializers.EmailField(source='subscription.email', read_only=True)
    
    class Meta:
        model = NewsletterDelivery
        fields = [
            'id', 'campaign', 'campaign_title', 'subscription', 'subscription_email',
            'status', 'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'campaign_title', 'subscription_email',
            'sent_at', 'delivered_at', 'opened_at', 'clicked_at',
            'created_at', 'updated_at'
        ]

class NewsletterStatsSerializer(serializers.Serializer):
    """
    Serializer for newsletter statistics
    """
    total_subscriptions = serializers.IntegerField()
    active_subscriptions = serializers.IntegerField()
    confirmed_subscriptions = serializers.IntegerField()
    total_campaigns = serializers.IntegerField()
    sent_campaigns = serializers.IntegerField()
    average_open_rate = serializers.FloatField()
    average_click_rate = serializers.FloatField()
    
    # Frequency breakdown
    daily_subscribers = serializers.IntegerField()
    weekly_subscribers = serializers.IntegerField()
    monthly_subscribers = serializers.IntegerField()
    
    # Recent activity
    recent_subscriptions = serializers.IntegerField()
    recent_campaigns = serializers.IntegerField()

class UnsubscribeSerializer(serializers.Serializer):
    """
    Serializer for unsubscribe requests
    """
    email = serializers.EmailField()
    token = serializers.CharField(max_length=255, required=False)
    
    def validate(self, data):
        """
        Validate unsubscribe request
        """
        email = data.get('email')
        token = data.get('token')
        
        try:
            subscription = NewsletterSubscription.objects.get(email=email)
            if token and subscription.confirmation_token != token:
                raise serializers.ValidationError('Invalid unsubscribe token')
            data['subscription'] = subscription
        except NewsletterSubscription.DoesNotExist:
            raise serializers.ValidationError('Email not found in our newsletter list')
        
        return data

class ConfirmSubscriptionSerializer(serializers.Serializer):
    """
    Serializer for subscription confirmation
    """
    token = serializers.CharField(max_length=255)
    
    def validate_token(self, value):
        """
        Validate confirmation token
        """
        try:
            subscription = NewsletterSubscription.objects.get(
                confirmation_token=value,
                is_confirmed=False
            )
            self.subscription = subscription
            return value
        except NewsletterSubscription.DoesNotExist:
            raise serializers.ValidationError('Invalid or expired confirmation token')