from django.db import models
from django.conf import settings
from django.utils import timezone


class Conversation(models.Model):
    """
    Conversation model for messaging between users
    Following 3NF principles for database design
    """
    
    class ConversationType(models.TextChoices):
        DIRECT = 'direct', 'Direct Message'
        PROPERTY_INQUIRY = 'property_inquiry', 'Property Inquiry'
        GROUP = 'group', 'Group Chat'
    
    # Basic conversation information
    title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Conversation title (optional for direct messages)"
    )
    conversation_type = models.CharField(
        max_length=20,
        choices=ConversationType.choices,
        default=ConversationType.DIRECT,
        help_text="Type of conversation"
    )
    
    # Property reference (for property inquiries)
    property = models.ForeignKey(
        'properties.Property',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='conversations',
        help_text="Related property (for property inquiries)"
    )
    
    # Conversation metadata
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the conversation is active"
    )
    is_archived = models.BooleanField(
        default=False,
        help_text="Whether the conversation is archived"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_message_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Timestamp of the last message"
    )
    
    class Meta:
        db_table = 'conversations'
        verbose_name = 'Conversation'
        verbose_name_plural = 'Conversations'
        ordering = ['-last_message_at', '-updated_at']
        indexes = [
            models.Index(fields=['conversation_type']),
            models.Index(fields=['property']),
            models.Index(fields=['is_active', 'is_archived']),
            models.Index(fields=['last_message_at']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        if self.title:
            return self.title
        elif self.conversation_type == self.ConversationType.PROPERTY_INQUIRY and self.property:
            return f"Inquiry about {self.property.title}"
        else:
            participants = self.participants.all()[:2]
            if len(participants) >= 2:
                return f"Conversation between {participants[0].user.get_full_name()} and {participants[1].user.get_full_name()}"
            return f"Conversation {self.id}"
    
    def get_participants(self):
        """Get all participants in the conversation"""
        return [p.user for p in self.participants.all()]
    
    def get_other_participant(self, user):
        """Get the other participant in a direct conversation"""
        if self.conversation_type == self.ConversationType.DIRECT:
            participants = self.get_participants()
            return next((p for p in participants if p != user), None)
        return None
    
    def update_last_message_time(self):
        """Update the last message timestamp"""
        self.last_message_at = timezone.now()
        self.save(update_fields=['last_message_at', 'updated_at'])


class ConversationParticipant(models.Model):
    """
    Participants in a conversation
    Following 3NF principles with explicit through model
    """
    
    class ParticipantRole(models.TextChoices):
        MEMBER = 'member', 'Member'
        ADMIN = 'admin', 'Admin'
        OWNER = 'owner', 'Owner'
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversation_participations'
    )
    role = models.CharField(
        max_length=10,
        choices=ParticipantRole.choices,
        default=ParticipantRole.MEMBER,
        help_text="Role of the participant in the conversation"
    )
    
    # Participant status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the participant is active in the conversation"
    )
    is_muted = models.BooleanField(
        default=False,
        help_text="Whether the participant has muted notifications"
    )
    
    # Read status
    last_read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the participant last read messages"
    )
    
    # Timestamps
    joined_at = models.DateTimeField(auto_now_add=True)
    left_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the participant left the conversation"
    )
    
    class Meta:
        db_table = 'conversation_participants'
        verbose_name = 'Conversation Participant'
        verbose_name_plural = 'Conversation Participants'
        unique_together = ['conversation', 'user']
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['conversation', 'role']),
            models.Index(fields=['last_read_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} in {self.conversation}"
    
    def mark_as_read(self):
        """Mark conversation as read for this participant"""
        self.last_read_at = timezone.now()
        self.save(update_fields=['last_read_at'])
    
    def get_unread_count(self):
        """Get count of unread messages for this participant"""
        if not self.last_read_at:
            return self.conversation.messages.count()
        return self.conversation.messages.filter(
            created_at__gt=self.last_read_at
        ).exclude(sender=self.user).count()


class Message(models.Model):
    """
    Individual messages in conversations
    Following 3NF principles for database design
    """
    
    class MessageType(models.TextChoices):
        TEXT = 'text', 'Text Message'
        IMAGE = 'image', 'Image'
        FILE = 'file', 'File'
        SYSTEM = 'system', 'System Message'
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
        null=True,
        blank=True,
        help_text="Message sender (null for system messages)"
    )
    
    # Message content
    message_type = models.CharField(
        max_length=10,
        choices=MessageType.choices,
        default=MessageType.TEXT,
        help_text="Type of message"
    )
    content = models.TextField(
        help_text="Message content"
    )
    
    # File attachments
    file_attachment = models.FileField(
        upload_to='messages/',
        null=True,
        blank=True,
        help_text="File attachment (for file/image messages)"
    )
    file_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Original filename"
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    
    # Message metadata
    is_edited = models.BooleanField(
        default=False,
        help_text="Whether the message has been edited"
    )
    is_deleted = models.BooleanField(
        default=False,
        help_text="Whether the message has been deleted"
    )
    
    # Reply functionality
    reply_to = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Message this is replying to"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the message was last edited"
    )
    
    class Meta:
        db_table = 'messages'
        verbose_name = 'Message'
        verbose_name_plural = 'Messages'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['conversation', 'created_at']),
            models.Index(fields=['sender']),
            models.Index(fields=['message_type']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['reply_to']),
        ]
    
    def __str__(self):
        if self.sender:
            return f"Message from {self.sender.get_full_name()} in {self.conversation}"
        return f"System message in {self.conversation}"
    
    def save(self, *args, **kwargs):
        """Override save to update conversation timestamp"""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Update conversation's last message time
        if is_new and not self.is_deleted:
            self.conversation.update_last_message_time()
    
    def soft_delete(self):
        """Soft delete the message"""
        self.is_deleted = True
        self.content = "[Message deleted]"
        self.save(update_fields=['is_deleted', 'content', 'updated_at'])
    
    def mark_as_edited(self):
        """Mark message as edited"""
        self.is_edited = True
        self.edited_at = timezone.now()
        self.save(update_fields=['is_edited', 'edited_at', 'updated_at'])


class MessageReadStatus(models.Model):
    """
    Track read status of messages by participants
    Following 3NF principles
    """
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='read_statuses'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='message_read_statuses'
    )
    read_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'message_read_statuses'
        verbose_name = 'Message Read Status'
        verbose_name_plural = 'Message Read Statuses'
        unique_together = ['message', 'user']
        indexes = [
            models.Index(fields=['message']),
            models.Index(fields=['user', 'read_at']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name()} read message {self.message.id}"
