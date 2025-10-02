from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import BlogPost, BlogCategory, BlogComment, BlogTag

User = get_user_model()


class BlogTagSerializer(serializers.ModelSerializer):
    """
    Serializer for blog tags
    """
    
    post_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogTag
        fields = [
            'id', 'name', 'slug', 'description', 'color',
            'is_featured', 'post_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'post_count', 'created_at', 'updated_at']
    
    def get_post_count(self, obj):
        """Get the number of published posts with this tag"""
        return obj.blog_posts.filter(status=BlogPost.StatusChoices.PUBLISHED).count()


class BlogCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for blog categories
    """
    
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogCategory
        fields = [
            'id', 'name', 'slug', 'description', 'color',
            'posts_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'posts_count']
    
    def get_posts_count(self, obj):
        """Get the number of published posts in this category"""
        return obj.posts.filter(status=BlogPost.StatusChoices.PUBLISHED).count()


class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for blog post authors
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'email']


class BlogPostListSerializer(serializers.ModelSerializer):
    """
    Serializer for blog post list view
    """
    
    author = AuthorSerializer(read_only=True)
    category = BlogCategorySerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    tag_list = serializers.ReadOnlyField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'featured_image',
            'author', 'category', 'tags', 'tag_list', 'status',
            'is_featured', 'published_at', 'read_time', 'views_count',
            'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'views_count', 'comments_count',
            'created_at', 'updated_at', 'tag_list'
        ]
    
    def get_comments_count(self, obj):
        """Get the number of approved comments for this post"""
        return obj.comments.filter(status=BlogComment.StatusChoices.APPROVED).count()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for blog post detail view
    """
    
    author = AuthorSerializer(read_only=True)
    category = BlogCategorySerializer(read_only=True)
    tags = BlogTagSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    tag_list = serializers.ReadOnlyField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'featured_image',
            'author', 'category', 'tags', 'tag_list', 'status',
            'is_featured', 'published_at', 'read_time', 'views_count',
            'comments_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'slug', 'author', 'views_count', 'comments_count',
            'created_at', 'updated_at', 'tag_list'
        ]
    
    def get_comments_count(self, obj):
        """Get the number of approved comments for this post"""
        return obj.comments.filter(status=BlogComment.StatusChoices.APPROVED).count()


class BlogPostCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating blog posts
    """
    
    class Meta:
        model = BlogPost
        fields = [
            'title', 'excerpt', 'content', 'featured_image',
            'category', 'tags', 'status', 'is_featured', 'published_at'
        ]
    
    def validate_title(self, value):
        """Validate blog post title"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long."
            )
        return value.strip()
    
    def validate_excerpt(self, value):
        """Validate blog post excerpt"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Excerpt must be at least 10 characters long."
            )
        return value.strip()
    
    def validate_content(self, value):
        """Validate blog post content"""
        if len(value.strip()) < 50:
            raise serializers.ValidationError(
                "Content must be at least 50 characters long."
            )
        return value.strip()


class BlogCommentSerializer(serializers.ModelSerializer):
    """
    Serializer for blog comments
    """
    
    author = AuthorSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogComment
        fields = [
            'id', 'post', 'author', 'content', 'status',
            'parent', 'replies', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'author', 'status', 'replies', 'created_at', 'updated_at'
        ]
    
    def get_replies(self, obj):
        """Get approved replies to this comment"""
        if obj.replies.exists():
            replies = obj.replies.filter(status=BlogComment.StatusChoices.APPROVED)
            return BlogCommentSerializer(replies, many=True, context=self.context).data
        return []
    
    def validate_content(self, value):
        """Validate comment content"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Comment must be at least 5 characters long."
            )
        return value.strip()


class BlogCommentCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating blog comments
    """
    
    class Meta:
        model = BlogComment
        fields = ['post', 'content', 'parent']
    
    def validate_content(self, value):
        """Validate comment content"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Comment must be at least 5 characters long."
            )
        return value.strip()
    
    def validate(self, attrs):
        """Validate the comment data"""
        post = attrs.get('post')
        parent = attrs.get('parent')
        
        # Ensure the post is published
        if post and post.status != BlogPost.StatusChoices.PUBLISHED:
            raise serializers.ValidationError(
                "Cannot comment on unpublished posts."
            )
        
        # Ensure parent comment belongs to the same post
        if parent and parent.post != post:
            raise serializers.ValidationError(
                "Parent comment must belong to the same post."
            )
        
        return attrs