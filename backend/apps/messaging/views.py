from rest_framework import viewsets, status, permissions, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Max
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Conversation, ConversationParticipant, Message, MessageReadStatus
from .serializers import (
    ConversationListSerializer,
    ConversationDetailSerializer,
    ConversationCreateSerializer,
    MessageSerializer,
    ConversationParticipantSerializer,
    MessageReadStatusSerializer
)
from apps.properties.models import Property

User = get_user_model()


class IsParticipantOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow participants to view/edit conversations
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in permissions.SAFE_METHODS:
            if isinstance(obj, Conversation):
                return obj.participants.filter(user=request.user).exists()
            elif isinstance(obj, Message):
                return obj.conversation.participants.filter(user=request.user).exists()
        
        # Write permissions only for participants
        if isinstance(obj, Conversation):
            return obj.participants.filter(user=request.user, is_active=True).exists()
        elif isinstance(obj, Message):
            # Only sender can edit their own messages
            return obj.sender == request.user
        
        return False


class ConversationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Conversation model
    Handles CRUD operations for conversations
    """
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'property__title']
    ordering_fields = ['created_at', 'updated_at', 'last_message_at']
    ordering = ['-last_message_at']
    
    def get_queryset(self):
        """
        Return conversations where user is a participant
        """
        if self.request.user.is_authenticated:
            return Conversation.objects.filter(
                participants__user=self.request.user,
                participants__is_active=True
            ).select_related('property').prefetch_related(
                'participants__user', 'messages'
            ).distinct()
        return Conversation.objects.none()
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return ConversationListSerializer
        elif self.action == 'create':
            return ConversationCreateSerializer
        return ConversationDetailSerializer
    
    def perform_create(self, serializer):
        """
        Create conversation and handle property-based conversations
        """
        conversation = serializer.save()
        
        # If it's a property inquiry, add property owner as participant
        if conversation.property:
            property_owner = conversation.property.owner
            if not conversation.participants.filter(user=property_owner).exists():
                ConversationParticipant.objects.create(
                    conversation=conversation,
                    user=property_owner,
                    role=ConversationParticipant.ParticipantRole.MEMBER
                )
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark conversation as read for current user
        """
        conversation = self.get_object()
        participant = conversation.participants.filter(user=request.user).first()
        
        if participant:
            participant.mark_as_read()
            return Response({'status': 'marked as read'})
        
        return Response(
            {'error': 'You are not a participant in this conversation'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """
        Archive conversation for current user
        """
        conversation = self.get_object()
        participant = conversation.participants.filter(user=request.user).first()
        
        if participant:
            # For now, we'll set the conversation as archived
            # In a more complex system, this might be per-participant
            conversation.is_archived = True
            conversation.save()
            return Response({'status': 'conversation archived'})
        
        return Response(
            {'error': 'You are not a participant in this conversation'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=True, methods=['post'])
    def leave(self, request, pk=None):
        """
        Leave conversation (mark participant as inactive)
        """
        conversation = self.get_object()
        participant = conversation.participants.filter(user=request.user).first()
        
        if participant:
            participant.is_active = False
            participant.left_at = timezone.now()
            participant.save()
            return Response({'status': 'left conversation'})
        
        return Response(
            {'error': 'You are not a participant in this conversation'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """
        Get total unread message count across all conversations
        """
        total_unread = 0
        conversations = self.get_queryset()
        
        for conversation in conversations:
            participant = conversation.participants.filter(user=request.user).first()
            if participant:
                total_unread += participant.get_unread_count()
        
        return Response({'unread_count': total_unread})
    
    @action(detail=False, methods=['post'])
    def start_property_inquiry(self, request):
        """
        Start a conversation about a specific property
        """
        property_id = request.data.get('property_id')
        message_content = request.data.get('message', '')
        
        if not property_id:
            return Response(
                {'error': 'Property ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            property_obj = Property.objects.get(id=property_id, is_published=True)
        except Property.DoesNotExist:
            return Response(
                {'error': 'Property not found or not published'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if conversation already exists between user and property owner
        existing_conversation = Conversation.objects.filter(
            property=property_obj,
            participants__user=request.user
        ).filter(
            participants__user=property_obj.owner
        ).first()
        
        if existing_conversation:
            # Add message to existing conversation if provided
            if message_content:
                Message.objects.create(
                    conversation=existing_conversation,
                    sender=request.user,
                    content=message_content,
                    message_type=Message.MessageType.TEXT
                )
                existing_conversation.update_last_message_time()
            
            serializer = ConversationDetailSerializer(
                existing_conversation, context={'request': request}
            )
            return Response(serializer.data)
        
        # Create new conversation
        conversation = Conversation.objects.create(
            title=f"Inquiry about {property_obj.title}",
            conversation_type=Conversation.ConversationType.DIRECT,
            property=property_obj
        )
        
        # Add participants
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=request.user,
            role=ConversationParticipant.ParticipantRole.MEMBER
        )
        
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=property_obj.owner,
            role=ConversationParticipant.ParticipantRole.MEMBER
        )
        
        # Add initial message if provided
        if message_content:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=message_content,
                message_type=Message.MessageType.TEXT
            )
            conversation.update_last_message_time()
        
        serializer = ConversationDetailSerializer(
            conversation, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class MessageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Message model
    Handles CRUD operations for messages
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsParticipantOrReadOnly]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at']
    ordering = ['created_at']
    parser_classes = [MultiPartParser, FormParser]
    
    def get_queryset(self):
        """
        Return messages from conversations where user is a participant
        """
        conversation_id = self.request.query_params.get('conversation_id')
        
        if not self.request.user.is_authenticated:
            return Message.objects.none()

        queryset = Message.objects.filter(
            conversation__participants__user=self.request.user,
            conversation__participants__is_active=True,
            is_deleted=False
        ).select_related('sender', 'conversation', 'reply_to__sender')
        
        if conversation_id:
            queryset = queryset.filter(conversation_id=conversation_id)
        
        return queryset.distinct()
    
    def perform_create(self, serializer):
        """
        Create message and update conversation timestamp
        """
        message = serializer.save(sender=self.request.user)
        message.conversation.update_last_message_time()
    
    def perform_update(self, serializer):
        """
        Update message and mark as edited
        """
        serializer.save(is_edited=True, edited_at=timezone.now())
    
    def perform_destroy(self, instance):
        """
        Soft delete message instead of hard delete
        """
        instance.is_deleted = True
        instance.save()
    
    @action(detail=True, methods=['post'])
    def mark_as_read(self, request, pk=None):
        """
        Mark message as read by current user
        """
        message = self.get_object()
        
        # Create or update read status
        read_status, created = MessageReadStatus.objects.get_or_create(
            message=message,
            user=request.user
        )
        
        if created:
            return Response({'status': 'marked as read'})
        else:
            return Response({'status': 'already marked as read'})
    
    @action(detail=False, methods=['post'])
    def mark_conversation_read(self, request):
        """
        Mark all messages in a conversation as read
        """
        conversation_id = request.data.get('conversation_id')
        
        if not conversation_id:
            return Response(
                {'error': 'Conversation ID is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            conversation = Conversation.objects.get(
                id=conversation_id,
                participants__user=request.user,
                participants__is_active=True
            )
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Mark participant's last read time
        participant = conversation.participants.filter(user=request.user).first()
        if participant:
            participant.mark_as_read()
        
        # Mark all unread messages as read
        unread_messages = conversation.messages.filter(
            is_deleted=False
        ).exclude(
            read_statuses__user=request.user
        )
        
        for message in unread_messages:
            MessageReadStatus.objects.get_or_create(
                message=message,
                user=request.user
            )
        
        return Response({'status': f'marked {unread_messages.count()} messages as read'})


class ConversationParticipantViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ConversationParticipant model
    Read-only access to conversation participants
    """
    serializer_class = ConversationParticipantSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Return participants from conversations where user is also a participant
        """
        if not self.request.user.is_authenticated:
            return ConversationParticipant.objects.none()

        return ConversationParticipant.objects.filter(
            conversation__participants__user=self.request.user,
            conversation__participants__is_active=True
        ).select_related('user', 'conversation').distinct()
