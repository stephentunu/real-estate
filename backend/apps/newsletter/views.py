from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Avg, Q
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from .models import NewsletterSubscription, NewsletterCampaign, NewsletterDelivery
from .serializers import (
    NewsletterSubscriptionSerializer,
    NewsletterSubscriptionCreateSerializer,
    NewsletterCampaignSerializer,
    NewsletterCampaignCreateSerializer,
    NewsletterDeliverySerializer,
    NewsletterStatsSerializer,
    UnsubscribeSerializer,
    ConfirmSubscriptionSerializer
)

class NewsletterSubscriptionListCreateView(generics.ListCreateAPIView):
    """
    List all newsletter subscriptions or create a new subscription
    """
    queryset = NewsletterSubscription.objects.all()
    permission_classes = [AllowAny]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewsletterSubscriptionCreateSerializer
        return NewsletterSubscriptionSerializer
    
    def get_queryset(self):
        queryset = NewsletterSubscription.objects.all()
        
        # Filter by user if authenticated
        if self.request.user.is_authenticated:
            user_filter = self.request.query_params.get('user_only', None)
            if user_filter == 'true':
                queryset = queryset.filter(user=self.request.user)
        
        # Filter by status
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        is_confirmed = self.request.query_params.get('is_confirmed', None)
        if is_confirmed is not None:
            queryset = queryset.filter(is_confirmed=is_confirmed.lower() == 'true')
        
        # Filter by frequency
        frequency = self.request.query_params.get('frequency', None)
        if frequency:
            queryset = queryset.filter(frequency=frequency)
        
        return queryset.order_by('-created_at')
    
    def perform_create(self, serializer):
        """
        Create subscription and send confirmation email
        """
        subscription = serializer.save()
        # TODO: Send confirmation email
        return subscription

class NewsletterSubscriptionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a newsletter subscription
    """
    queryset = NewsletterSubscription.objects.all()
    serializer_class = NewsletterSubscriptionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Users can only access their own subscriptions unless they're staff
        """
        # Prevent Swagger schema generation errors
        if getattr(self, 'swagger_fake_view', False):
            return NewsletterSubscription.objects.none()
        
        if self.request.user.is_staff:
            return NewsletterSubscription.objects.all()
        return NewsletterSubscription.objects.filter(user=self.request.user)

class NewsletterCampaignListCreateView(generics.ListCreateAPIView):
    """
    List all newsletter campaigns or create a new campaign
    """
    queryset = NewsletterCampaign.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return NewsletterCampaignCreateSerializer
        return NewsletterCampaignSerializer
    
    def get_queryset(self):
        queryset = NewsletterCampaign.objects.all()
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by created_by
        created_by = self.request.query_params.get('created_by', None)
        if created_by:
            queryset = queryset.filter(created_by_id=created_by)
        
        # Filter by date range
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        return queryset.order_by('-created_at')

class NewsletterCampaignDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a newsletter campaign
    """
    queryset = NewsletterCampaign.objects.all()
    serializer_class = NewsletterCampaignSerializer
    permission_classes = [IsAuthenticated]

class NewsletterDeliveryListView(generics.ListAPIView):
    """
    List newsletter deliveries
    """
    queryset = NewsletterDelivery.objects.all()
    serializer_class = NewsletterDeliverySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = NewsletterDelivery.objects.all()
        
        # Filter by campaign
        campaign_id = self.request.query_params.get('campaign', None)
        if campaign_id:
            queryset = queryset.filter(campaign_id=campaign_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by subscription
        subscription_id = self.request.query_params.get('subscription', None)
        if subscription_id:
            queryset = queryset.filter(subscription_id=subscription_id)
        
        return queryset.order_by('-created_at')

@api_view(['POST'])
@permission_classes([AllowAny])
def subscribe_newsletter(request):
    """
    Subscribe to newsletter (public endpoint)
    """
    serializer = NewsletterSubscriptionCreateSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Check if email already exists
        email = serializer.validated_data['email']
        existing_subscription = NewsletterSubscription.objects.filter(email=email).first()
        
        if existing_subscription:
            if existing_subscription.is_active:
                return Response(
                    {'message': 'Email is already subscribed to our newsletter'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                # Reactivate existing subscription
                existing_subscription.is_active = True
                existing_subscription.unsubscribed_at = None
                existing_subscription.frequency = serializer.validated_data.get('frequency', 'weekly')
                existing_subscription.categories = serializer.validated_data.get('categories', [])
                existing_subscription.save()
                
                return Response(
                    {
                        'message': 'Successfully resubscribed to newsletter',
                        'subscription': NewsletterSubscriptionSerializer(existing_subscription).data
                    },
                    status=status.HTTP_200_OK
                )
        
        subscription = serializer.save()
        # TODO: Send confirmation email
        
        return Response(
            {
                'message': 'Successfully subscribed to newsletter. Please check your email to confirm.',
                'subscription': NewsletterSubscriptionSerializer(subscription).data
            },
            status=status.HTTP_201_CREATED
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def unsubscribe_newsletter(request):
    """
    Unsubscribe from newsletter (public endpoint)
    """
    serializer = UnsubscribeSerializer(data=request.data)
    
    if serializer.is_valid():
        subscription = serializer.validated_data['subscription']
        subscription.unsubscribe()
        
        return Response(
            {'message': 'Successfully unsubscribed from newsletter'},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def confirm_subscription(request):
    """
    Confirm newsletter subscription (public endpoint)
    """
    serializer = ConfirmSubscriptionSerializer(data=request.data)
    
    if serializer.is_valid():
        subscription = serializer.subscription
        subscription.confirm_subscription()
        
        return Response(
            {
                'message': 'Email subscription confirmed successfully',
                'subscription': NewsletterSubscriptionSerializer(subscription).data
            },
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def newsletter_stats(request):
    """
    Get newsletter statistics (admin only)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Calculate statistics
    total_subscriptions = NewsletterSubscription.objects.count()
    active_subscriptions = NewsletterSubscription.objects.filter(is_active=True).count()
    confirmed_subscriptions = NewsletterSubscription.objects.filter(is_confirmed=True).count()
    
    total_campaigns = NewsletterCampaign.objects.count()
    sent_campaigns = NewsletterCampaign.objects.filter(status='sent').count()
    
    # Calculate average rates
    sent_campaigns_data = NewsletterCampaign.objects.filter(
        status='sent',
        total_sent__gt=0
    )
    
    if sent_campaigns_data.exists():
        avg_open_rate = sent_campaigns_data.aggregate(
            avg_rate=Avg('total_opened') / Avg('total_sent') * 100
        )['avg_rate'] or 0
        avg_click_rate = sent_campaigns_data.aggregate(
            avg_rate=Avg('total_clicked') / Avg('total_sent') * 100
        )['avg_rate'] or 0
    else:
        avg_open_rate = 0
        avg_click_rate = 0
    
    # Frequency breakdown
    frequency_stats = NewsletterSubscription.objects.filter(is_active=True).aggregate(
        daily=Count('id', filter=Q(frequency='daily')),
        weekly=Count('id', filter=Q(frequency='weekly')),
        monthly=Count('id', filter=Q(frequency='monthly'))
    )
    
    # Recent activity (last 30 days)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_subscriptions = NewsletterSubscription.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    recent_campaigns = NewsletterCampaign.objects.filter(
        created_at__gte=thirty_days_ago
    ).count()
    
    stats_data = {
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'confirmed_subscriptions': confirmed_subscriptions,
        'total_campaigns': total_campaigns,
        'sent_campaigns': sent_campaigns,
        'average_open_rate': round(avg_open_rate, 2),
        'average_click_rate': round(avg_click_rate, 2),
        'daily_subscribers': frequency_stats['daily'],
        'weekly_subscribers': frequency_stats['weekly'],
        'monthly_subscribers': frequency_stats['monthly'],
        'recent_subscriptions': recent_subscriptions,
        'recent_campaigns': recent_campaigns,
    }
    
    serializer = NewsletterStatsSerializer(stats_data)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def send_campaign(request, campaign_id):
    """
    Send a newsletter campaign (admin only)
    """
    if not request.user.is_staff:
        return Response(
            {'error': 'Permission denied'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    campaign = get_object_or_404(NewsletterCampaign, id=campaign_id)
    
    if campaign.status != 'draft' and campaign.status != 'scheduled':
        return Response(
            {'error': 'Campaign cannot be sent in current status'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Update campaign status
    campaign.status = 'sending'
    campaign.save()
    
    # TODO: Implement actual email sending logic
    # This would typically involve:
    # 1. Getting target subscribers based on campaign criteria
    # 2. Creating delivery records
    # 3. Sending emails asynchronously
    # 4. Updating campaign statistics
    
    return Response(
        {
            'message': 'Campaign sending initiated',
            'campaign': NewsletterCampaignSerializer(campaign).data
        },
        status=status.HTTP_200_OK
    )

@api_view(['GET'])
@permission_classes([AllowAny])
def newsletter_categories(request):
    """
    Get available newsletter categories
    """
    categories = [
        'property_updates',
        'market_news',
        'investment_tips',
        'legal_updates',
        'maintenance_tips',
        'community_news',
        'special_offers',
        'events'
    ]
    
    return Response({'categories': categories}, status=status.HTTP_200_OK)
