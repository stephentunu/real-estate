from django.urls import re_path
# from . import consumers

# WebSocket URL patterns for real-time messaging
websocket_urlpatterns = [
    # WebSocket endpoint for conversation messaging
    # re_path(r'ws/conversations/(?P<conversation_id>\d+)/$', consumers.ConversationConsumer.as_asgi()),
    
    # WebSocket endpoint for general notifications
    # re_path(r'ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]