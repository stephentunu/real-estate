from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, ConversationParticipant, Message, MessageReadStatus
from apps.properties.models import Property

User = get_user_model()


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """
    Serializer for ConversationParticipant model
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_avatar = serializers.ImageField(source='user.avatar', read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationParticipant
        fields = [
            'id', 'user', 'user_name', 'user_email', 'user_avatar', 'role',
            'is_active', 'is_muted', 'last_read_at', 'joined_at', 'left_at',
            'unread_count'
        ]
        read_only_fields = ['id', 'joined_at', 'left_at', 'unread_count']
    
    def get_unread_count(self, obj):
        """
        Get unread message count for this participant
        """
        return obj.get_unread_count()


class MessageSerializer(serializers.ModelSerializer):
    """
    Serializer for Message model
    """
    sender_name = serializers.CharField(source='sender.get_full_name', read_only=True)
    sender_avatar = serializers.ImageField(source='sender.avatar', read_only=True)
    reply_to_content = serializers.CharField(source='reply_to.content', read_only=True)
    reply_to_sender = serializers.CharField(source='reply_to.sender.get_full_name', read_only=True)
    is_own_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Message
        fields = [
            'id', 'conversation', 'sender', 'sender_name', 'sender_avatar',
            'message_type', 'content', 'file_attachment', 'file_name', 'file_size',
            'is_edited', 'is_deleted', 'reply_to', 'reply_to_content', 'reply_to_sender',
            'is_own_message', 'created_at', 'updated_at', 'edited_at'
        ]
        read_only_fields = [
            'id', 'sender', 'is_edited', 'created_at', 'updated_at', 'edited_at',
            'is_own_message'
        ]
    
    def get_is_own_message(self, obj):
        """
        Check if message belongs to current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.sender == request.user
        return False
    
    def create(self, validated_data):
        """
        Create message with sender as current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['sender'] = request.user
        return super().create(validated_data)


class ConversationListSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model list view
    """
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_image = serializers.SerializerMethodField()
    other_participant = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'conversation_type', 'property', 'property_title',
            'property_image', 'other_participant', 'last_message', 'unread_count',
            'is_active', 'is_archived', 'created_at', 'updated_at', 'last_message_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_message_at',
            'property_title', 'property_image', 'other_participant',
            'last_message', 'unread_count'
        ]
    
    def get_property_image(self, obj):
        """
        Get property primary image
        """
        if obj.property:
            primary_image = obj.property.images.filter(is_primary=True).first()
            if primary_image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(primary_image.image.url)
        return None
    
    def get_other_participant(self, obj):
        """
        Get other participant in direct conversation
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_user = obj.get_other_participant(request.user)
            if other_user:
                return {
                    'id': other_user.id,
                    'name': other_user.get_full_name(),
                    'email': other_user.email,
                    'avatar': other_user.avatar.url if other_user.avatar else None
                }
        return None
    
    def get_last_message(self, obj):
        """
        Get last message in conversation
        """
        last_message = obj.messages.filter(is_deleted=False).last()
        if last_message:
            return {
                'id': last_message.id,
                'content': last_message.content,
                'message_type': last_message.message_type,
                'sender_name': last_message.sender.get_full_name() if last_message.sender else 'System',
                'created_at': last_message.created_at
            }
        return None
    
    def get_unread_count(self, obj):
        """
        Get unread message count for current user
        """
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            participant = obj.participants.filter(user=request.user).first()
            if participant:
                return participant.get_unread_count()
        return 0


class ConversationDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Conversation model detail view
    """
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    property_title = serializers.CharField(source='property.title', read_only=True)
    property_owner = serializers.CharField(source='property.owner.get_full_name', read_only=True)
    messages = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'title', 'conversation_type', 'property', 'property_title',
            'property_owner', 'participants', 'messages', 'is_active', 'is_archived',
            'created_at', 'updated_at', 'last_message_at'
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'last_message_at',
            'property_title', 'property_owner', 'participants', 'messages'
        ]
    
    def get_messages(self, obj):
        """
        Get recent messages (last 50)
        """
        messages = obj.messages.filter(is_deleted=False).order_by('-created_at')[:50]
        return MessageSerializer(messages, many=True, context=self.context).data


class ConversationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating conversations
    """
    participant_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False,
        help_text="List of user IDs to add as participants"
    )
    initial_message = serializers.CharField(
        write_only=True,
        required=False,
        help_text="Initial message content"
    )
    
    class Meta:
        model = Conversation
        fields = [
            'title', 'conversation_type', 'property', 'participant_ids', 'initial_message'
        ]
    
    def validate_participant_ids(self, value):
        """
        Validate participant IDs
        """
        if value:
            existing_users = User.objects.filter(id__in=value).count()
            if existing_users != len(value):
                raise serializers.ValidationError("Some user IDs are invalid")
        return value
    
    def validate_property(self, value):
        """
        Validate property exists and is published
        """
        if value and not value.is_published:
            raise serializers.ValidationError("Cannot create conversation for unpublished property")
        return value
    
    def create(self, validated_data):
        """
        Create conversation with participants and initial message
        """
        participant_ids = validated_data.pop('participant_ids', [])
        initial_message = validated_data.pop('initial_message', None)
        
        # Create conversation
        conversation = super().create(validated_data)
        
        # Add current user as participant
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            ConversationParticipant.objects.create(
                conversation=conversation,
                user=request.user,
                role=ConversationParticipant.ParticipantRole.MEMBER
            )
        
        # Add other participants
        for user_id in participant_ids:
            user = User.objects.get(id=user_id)
            ConversationParticipant.objects.create(
                conversation=conversation,
                user=user,
                role=ConversationParticipant.ParticipantRole.MEMBER
            )
        
        # Create initial message if provided
        if initial_message and request and request.user.is_authenticated:
            Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=initial_message,
                message_type=Message.MessageType.TEXT
            )
            conversation.update_last_message_time()
        
        return conversation


class MessageReadStatusSerializer(serializers.ModelSerializer):
    """
    Serializer for MessageReadStatus model
    """
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = MessageReadStatus
        fields = ['id', 'message', 'user', 'user_name', 'read_at']
        read_only_fields = ['id', 'user', 'read_at']