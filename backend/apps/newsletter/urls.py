from django.urls import path
from . import views

app_name = 'newsletter'

urlpatterns = [
    # Newsletter subscriptions
    path(
        'subscriptions/', 
        views.NewsletterSubscriptionListCreateView.as_view(), 
        name='subscription-list-create'
    ),
    path(
        'subscriptions/<uuid:pk>/', 
        views.NewsletterSubscriptionDetailView.as_view(), 
        name='subscription-detail'
    ),
    
    # Newsletter campaigns
    path(
        'campaigns/', 
        views.NewsletterCampaignListCreateView.as_view(), 
        name='campaign-list-create'
    ),
    path(
        'campaigns/<uuid:pk>/', 
        views.NewsletterCampaignDetailView.as_view(), 
        name='campaign-detail'
    ),
    path(
        'campaigns/<uuid:campaign_id>/send/', 
        views.send_campaign, 
        name='campaign-send'
    ),
    
    # Newsletter deliveries
    path(
        'deliveries/', 
        views.NewsletterDeliveryListView.as_view(), 
        name='delivery-list'
    ),
    
    # Public endpoints
    path(
        'subscribe/', 
        views.subscribe_newsletter, 
        name='subscribe'
    ),
    path(
        'unsubscribe/', 
        views.unsubscribe_newsletter, 
        name='unsubscribe'
    ),
    path(
        'confirm/', 
        views.confirm_subscription, 
        name='confirm-subscription'
    ),
    
    # Utility endpoints
    path(
        'categories/', 
        views.newsletter_categories, 
        name='categories'
    ),
    path(
        'stats/', 
        views.newsletter_stats, 
        name='stats'
    ),
]