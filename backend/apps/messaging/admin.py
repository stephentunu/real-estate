from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count, Q
from .models import Conversation, ConversationParticipant, Message, MessageReadStatus


class ConversationParticipantInline(admin.TabularInline):
    """
    Inline admin for ConversationParticipant
    """
    model = ConversationParticipant
    extra = 1
    fields = ('user', 'role', 'is_active', 'is_muted', 'last_read_at')
    readonly_fields = ('joined_at', 'last_read_at')


class MessageInline(admin.TabularInline):
    """
    Inline admin for Message (limited to recent messages)
    """
    model = Message
    extra = 0
    fields = ('sender', 'message_type', 'content', 'is_deleted', 'created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender').order_by('-created_at')[:10]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    """
    Comprehensive Conversation admin
    """
    inlines = [ConversationParticipantInline, MessageInline]
    
    list_display = (
        'get_conversation_title', 'conversation_type', 'property',
        'participant_count', 'message_count', 'is_active',
        'is_archived', 'last_message_at', 'created_at'
    )
    
    list_filter = (
        'conversation_type', 'is_active', 'is_archived',
        'created_at', 'last_message_at'
    )
    
    search_fields = (
        'title', 'property__title',
        'participants__user__email', 'participants__user__first_name',
        'participants__user__last_name'
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_message_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'conversation_type', 'property')
        }),
        ('Status', {
            'fields': ('is_active', 'is_archived')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_message_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['archive_conversations', 'unarchive_conversations', 'activate_conversations', 'deactivate_conversations']
    
    def get_conversation_title(self, obj):
        return str(obj)
    get_conversation_title.short_description = 'Title'
    
    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'
    
    def message_count(self, obj):
        return obj.messages.count()
    message_count.short_description = 'Messages'
    
    def archive_conversations(self, request, queryset):
        """
        Archive selected conversations
        """
        updated = queryset.update(is_archived=True)
        self.message_user(request, f'{updated} conversations archived.')
    archive_conversations.short_description = "Archive selected conversations"
    
    def unarchive_conversations(self, request, queryset):
        """
        Unarchive selected conversations
        """
        updated = queryset.update(is_archived=False)
        self.message_user(request, f'{updated} conversations unarchived.')
    unarchive_conversations.short_description = "Unarchive selected conversations"
    
    def activate_conversations(self, request, queryset):
        """
        Activate selected conversations
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} conversations activated.')
    activate_conversations.short_description = "Activate selected conversations"
    
    def deactivate_conversations(self, request, queryset):
        """
        Deactivate selected conversations
        """
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} conversations deactivated.')
    deactivate_conversations.short_description = "Deactivate selected conversations"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('property').prefetch_related('participants__user')


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    """
    Admin for ConversationParticipant
    """
    list_display = (
        'conversation', 'user', 'role', 'is_active',
        'is_muted', 'unread_count', 'joined_at'
    )
    
    list_filter = (
        'role', 'is_active', 'is_muted', 'joined_at'
    )
    
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'conversation__title'
    )
    
    readonly_fields = ('joined_at', 'left_at', 'last_read_at')
    
    def unread_count(self, obj):
        return obj.get_unread_count()
    unread_count.short_description = 'Unread'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'conversation')


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    """
    Comprehensive Message admin
    """
    list_display = (
        'get_message_preview', 'sender', 'conversation',
        'message_type', 'is_edited', 'is_deleted',
        'reply_to', 'created_at'
    )
    
    list_filter = (
        'message_type', 'is_edited', 'is_deleted',
        'created_at', 'conversation__conversation_type'
    )
    
    search_fields = (
        'content', 'sender__email', 'sender__first_name',
        'sender__last_name', 'conversation__title'
    )
    
    readonly_fields = (
        'created_at', 'updated_at', 'edited_at',
        'file_size', 'get_read_count'
    )
    
    fieldsets = (
        ('Message Content', {
            'fields': ('conversation', 'sender', 'message_type', 'content')
        }),
        ('File Attachment', {
            'fields': ('file_attachment', 'file_name', 'file_size'),
            'classes': ('collapse',)
        }),
        ('Message Status', {
            'fields': ('is_edited', 'is_deleted', 'reply_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'edited_at'),
            'classes': ('collapse',)
        }),
        ('Read Status', {
            'fields': ('get_read_count',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['soft_delete_messages', 'restore_messages', 'mark_as_edited']
    
    def get_message_preview(self, obj):
        if obj.is_deleted:
            return format_html('<em style="color: #999;">Message deleted</em>')
        elif obj.message_type == 'text':
            preview = obj.content[:50]
            if len(obj.content) > 50:
                preview += '...'
            return preview
        else:
            return f'[{obj.get_message_type_display()}]'
    get_message_preview.short_description = 'Content'
    
    def get_read_count(self, obj):
        return obj.read_statuses.count()
    get_read_count.short_description = 'Read by'
    
    def soft_delete_messages(self, request, queryset):
        """
        Soft delete selected messages
        """
        updated = 0
        for message in queryset:
            if not message.is_deleted:
                message.soft_delete()
                updated += 1
        self.message_user(request, f'{updated} messages deleted.')
    soft_delete_messages.short_description = "Delete selected messages"
    
    def restore_messages(self, request, queryset):
        """
        Restore selected messages
        """
        updated = queryset.update(is_deleted=False)
        self.message_user(request, f'{updated} messages restored.')
    restore_messages.short_description = "Restore selected messages"
    
    def mark_as_edited(self, request, queryset):
        """
        Mark selected messages as edited
        """
        updated = 0
        for message in queryset:
            if not message.is_edited:
                message.mark_as_edited()
                updated += 1
        self.message_user(request, f'{updated} messages marked as edited.')
    mark_as_edited.short_description = "Mark selected messages as edited"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('sender', 'conversation', 'reply_to')


@admin.register(MessageReadStatus)
class MessageReadStatusAdmin(admin.ModelAdmin):
    """
    Admin for MessageReadStatus
    """
    list_display = ('message', 'user', 'read_at')
    list_filter = ('read_at',)
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'message__content'
    )
    readonly_fields = ('read_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'message')
