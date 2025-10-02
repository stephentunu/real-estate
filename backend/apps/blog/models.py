from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from apps.core.mixins import VisibilityMixin, SoftDeleteMixin, SearchableMixin

User = get_user_model()


class BlogTag(VisibilityMixin, SoftDeleteMixin, models.Model):
    """
    Blog tag model for tagging blog posts
    Following 3NF principles for database design
    """
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Name of the tag"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        help_text="URL-friendly version of the tag name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the tag"
    )
    color = models.CharField(
        max_length=7,
        default="#6c757d",
        help_text="Hex color code for the tag"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this tag is featured"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search configuration
    searchable_fields = ['name', 'description']
    
    class Meta:
        db_table = 'blog_tag'
        verbose_name = 'Blog Tag'
        verbose_name_plural = 'Blog Tags'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
            models.Index(fields=['is_featured']),
        ]
        ordering = ['name']
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def post_count(self):
        """Get the number of posts with this tag"""
        return self.blog_posts.count()


class BlogCategory(VisibilityMixin, SoftDeleteMixin, models.Model):
    """
    Blog category model for organizing blog posts
    Following 3NF principles for database design
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Name of the blog category"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly version of the name"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of the category"
    )
    color = models.CharField(
        max_length=7,
        default="#007bff",
        help_text="Hex color code for the category"
    )
    
    class Meta:
        db_table = 'blog_category'
        verbose_name = 'Blog Category'
        verbose_name_plural = 'Blog Categories'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['slug']),
        ]
    
    def __str__(self) -> str:
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class BlogPost(VisibilityMixin, SoftDeleteMixin, SearchableMixin, models.Model):
    """
    Blog post model for managing blog content
    Following 3NF principles for database design
    """
    
    class StatusChoices(models.TextChoices):
        DRAFT = 'draft', 'Draft'
        PUBLISHED = 'published', 'Published'
        ARCHIVED = 'archived', 'Archived'
    
    title = models.CharField(
        max_length=200,
        help_text="Title of the blog post"
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        help_text="URL-friendly version of the title"
    )
    excerpt = models.TextField(
        max_length=300,
        help_text="Short description or excerpt of the post"
    )
    content = models.TextField(
        help_text="Full content of the blog post"
    )
    featured_image = models.ImageField(
        upload_to='blog/images/',
        blank=True,
        null=True,
        help_text="Featured image for the blog post"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_posts',
        help_text="Author of the blog post"
    )
    category = models.ForeignKey(
        BlogCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        help_text="Category of the blog post"
    )
    tags = models.ManyToManyField(
        BlogTag,
        blank=True,
        related_name='blog_posts',
        help_text="Tags associated with this post"
    )
    legacy_tags = models.CharField(
        max_length=500,
        blank=True,
        help_text="Legacy comma-separated tags (for migration purposes)"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.DRAFT,
        help_text="Publication status of the post"
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Whether this post is featured"
    )
    published_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Date and time when the post was published"
    )
    read_time = models.PositiveIntegerField(
        default=5,
        help_text="Estimated reading time in minutes"
    )
    views_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this post has been viewed"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Search configuration
    searchable_fields = ['title', 'excerpt', 'content', 'legacy_tags']
    
    class Meta:
        db_table = 'blog_post'
        verbose_name = 'Blog Post'
        verbose_name_plural = 'Blog Posts'
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['slug']),
            models.Index(fields=['status']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['published_at']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['-published_at', '-created_at']
    
    def __str__(self) -> str:
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-calculate read time based on content length
        if self.content:
            word_count = len(self.content.split())
            self.read_time = max(1, word_count // 200)  # Assuming 200 words per minute
        
        super().save(*args, **kwargs)
    
    @property
    def tag_list(self):
        """Get tags as a list"""
        # Return proper tags if available, otherwise fall back to legacy tags
        if self.tags.exists():
            return list(self.tags.values_list('name', flat=True))
        elif self.legacy_tags:
            return [tag.strip() for tag in self.legacy_tags.split(',') if tag.strip()]
        return []
    
    def get_absolute_url(self):
        """Get the absolute URL for this blog post"""
        return f"/blog/{self.slug}/"
    
    def increment_views(self):
        """Increment the view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])


class BlogComment(VisibilityMixin, SoftDeleteMixin, models.Model):
    """
    Blog comment model for user comments on blog posts
    Following 3NF principles for database design
    """
    
    class StatusChoices(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'
    
    post = models.ForeignKey(
        BlogPost,
        on_delete=models.CASCADE,
        related_name='comments',
        help_text="Blog post this comment belongs to"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='blog_comments',
        help_text="Author of the comment"
    )
    content = models.TextField(
        help_text="Content of the comment"
    )
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
        help_text="Moderation status of the comment"
    )
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent comment for nested replies"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'blog_comment'
        verbose_name = 'Blog Comment'
        verbose_name_plural = 'Blog Comments'
        indexes = [
            models.Index(fields=['post', 'status']),
            models.Index(fields=['author']),
            models.Index(fields=['created_at']),
        ]
        ordering = ['created_at']
    
    def __str__(self) -> str:
        return f"Comment by {self.author.username} on {self.post.title}"
