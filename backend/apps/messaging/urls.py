from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'conversations', views.ConversationViewSet, basename='conversation')
router.register(r'messages', views.MessageViewSet, basename='message')
router.register(r'participants', views.ConversationParticipantViewSet, basename='participant')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Custom endpoints are handled by ViewSet actions
    # Available endpoints:
    # GET /conversations/ - List conversations
    # POST /conversations/ - Create conversation
    # GET /conversations/{id}/ - Get conversation details
    # POST /conversations/{id}/mark_as_read/ - Mark conversation as read
    # POST /conversations/{id}/archive/ - Archive conversation
    # POST /conversations/{id}/leave/ - Leave conversation
    # GET /conversations/unread_count/ - Get unread count
    # POST /conversations/start_property_inquiry/ - Start property inquiry
    # 
    # GET /messages/ - List messages (with ?conversation_id filter)
    # POST /messages/ - Send message
    # PUT /messages/{id}/ - Edit message
    # DELETE /messages/{id}/ - Delete message (soft delete)
    # POST /messages/{id}/mark_as_read/ - Mark message as read
    # POST /messages/mark_conversation_read/ - Mark all messages in conversation as read
]