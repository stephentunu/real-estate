from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import BlogPost, BlogCategory, BlogComment


@admin.register(BlogCategory)
class BlogCategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for blog categories
    """
    
    list_display = [
        'name', 'slug', 'posts_count', 'color_display',
        'visibility_level'
    ]
    list_filter = ['visibility_level']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'color')
        }),
        ('Visibility', {
            'fields': ('visibility_level',)
        }),
        ('Metadata', {
            'fields': (),
            'classes': ('collapse',)
        })
    )
    
    def posts_count(self, obj):
        """Display the number of posts in this category"""
        count = obj.posts.filter(status=BlogPost.StatusChoices.PUBLISHED).count()
        if count > 0:
            url = reverse('admin:blog_blogpost_changelist') + f'?category__id__exact={obj.id}'
            return format_html('<a href="{}">{} posts</a>', url, count)
        return '0 posts'
    posts_count.short_description = 'Posts Count'
    
    def color_display(self, obj):
        """Display the color as a colored box"""
        return format_html(
            '<div style="width: 20px; height: 20px; background-color: {}; border: 1px solid #ccc;"></div>',
            obj.color
        )
    color_display.short_description = 'Color'
    
    actions = ['make_public', 'make_private']
    
    def make_public(self, request, queryset):
        """Make selected categories public"""
        updated = queryset.update(visibility_level='public')
        self.message_user(request, f'{updated} categories were successfully made public.')
    make_public.short_description = 'Make selected categories public'
    
    def make_private(self, request, queryset):
        """Make selected categories private"""
        updated = queryset.update(visibility_level='private')
        self.message_user(request, f'{updated} categories were successfully made private.')
    make_private.short_description = 'Make selected categories private'


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Admin configuration for blog posts
    """
    
    list_display = [
        'title', 'author', 'category', 'status', 'is_featured',
        'published_at', 'views_count', 'comments_count', 'created_at'
    ]
    list_filter = [
        'status', 'is_featured', 'category', 'author',
        'published_at', 'created_at', 'visibility_level'
    ]
    search_fields = ['title', 'excerpt', 'content', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = [
        'slug', 'views_count', 'read_time', 'created_at',
        'updated_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Classification', {
            'fields': ('category', 'tags')
        }),
        ('Publication', {
            'fields': ('status', 'is_featured', 'published_at')
        }),
        ('Statistics', {
            'fields': ('views_count', 'read_time'),
            'classes': ('collapse',)
        }),
        ('Visibility', {
            'fields': ('visibility_level',)
        }),
        ('Metadata', {
            'fields': ('author', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def comments_count(self, obj):
        """Display the number of approved comments"""
        count = obj.comments.filter(status=BlogComment.StatusChoices.APPROVED).count()
        if count > 0:
            url = reverse('admin:blog_blogcomment_changelist') + f'?post__id__exact={obj.id}'
            return format_html('<a href="{}">{} comments</a>', url, count)
        return '0 comments'
    comments_count.short_description = 'Comments'
    
    actions = [
        'make_published', 'make_draft', 'make_featured',
        'remove_featured', 'make_public', 'make_private'
    ]
    
    def make_published(self, request, queryset):
        """Publish selected posts"""
        from django.utils import timezone
        updated = queryset.update(
            status=BlogPost.StatusChoices.PUBLISHED,
            published_at=timezone.now()
        )
        self.message_user(request, f'{updated} posts were successfully published.')
    make_published.short_description = 'Publish selected posts'
    
    def make_draft(self, request, queryset):
        """Make selected posts draft"""
        updated = queryset.update(status=BlogPost.StatusChoices.DRAFT)
        self.message_user(request, f'{updated} posts were moved to draft.')
    make_draft.short_description = 'Move selected posts to draft'
    
    def make_featured(self, request, queryset):
        """Make selected posts featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} posts were marked as featured.')
    make_featured.short_description = 'Mark selected posts as featured'
    
    def remove_featured(self, request, queryset):
        """Remove featured status from selected posts"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} posts were unmarked as featured.')
    remove_featured.short_description = 'Remove featured status from selected posts'
    
    def make_public(self, request, queryset):
        """Make selected posts public"""
        updated = queryset.update(visibility_level='public')
        self.message_user(request, f'{updated} posts were successfully made public.')
    make_public.short_description = 'Make selected posts public'
    
    def make_private(self, request, queryset):
        """Make selected posts private"""
        updated = queryset.update(visibility_level='private')
        self.message_user(request, f'{updated} posts were successfully made private.')
    make_private.short_description = 'Make selected posts private'


@admin.register(BlogComment)
class BlogCommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for blog comments
    """
    
    list_display = [
        'post_title', 'author', 'content_preview', 'status',
        'parent_comment', 'created_at'
    ]
    list_filter = ['status', 'created_at', 'visibility_level']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Comment Information', {
            'fields': ('post', 'author', 'content', 'parent')
        }),
        ('Moderation', {
            'fields': ('status',)
        }),
        ('Visibility', {
            'fields': ('visibility_level',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def post_title(self, obj):
        """Display the post title with link"""
        url = reverse('admin:blog_blogpost_change', args=[obj.post.id])
        return format_html('<a href="{}">{}</a>', url, obj.post.title)
    post_title.short_description = 'Post'
    
    def content_preview(self, obj):
        """Display a preview of the comment content"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def parent_comment(self, obj):
        """Display parent comment if exists"""
        if obj.parent:
            return f'Reply to: {obj.parent.content[:30]}...'
        return 'Top-level comment'
    parent_comment.short_description = 'Parent'
    
    actions = ['approve_comments', 'reject_comments', 'make_public', 'make_private']
    
    def approve_comments(self, request, queryset):
        """Approve selected comments"""
        updated = queryset.update(status=BlogComment.StatusChoices.APPROVED)
        self.message_user(request, f'{updated} comments were approved.')
    approve_comments.short_description = 'Approve selected comments'
    
    def reject_comments(self, request, queryset):
        """Reject selected comments"""
        updated = queryset.update(status=BlogComment.StatusChoices.REJECTED)
        self.message_user(request, f'{updated} comments were rejected.')
    reject_comments.short_description = 'Reject selected comments'
    
    def make_public(self, request, queryset):
        """Make selected comments public"""
        updated = queryset.update(visibility_level='public')
        self.message_user(request, f'{updated} comments were successfully made public.')
    make_public.short_description = 'Make selected comments public'
    
    def make_private(self, request, queryset):
        """Make selected comments private"""
        updated = queryset.update(visibility_level='private')
        self.message_user(request, f'{updated} comments were successfully made private.')
    make_private.short_description = 'Make selected comments private'
