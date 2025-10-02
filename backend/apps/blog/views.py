from django.shortcuts import render
from django.utils import timezone
from django.db import models
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsOwnerOrReadOnly
from .models import BlogPost, BlogCategory, BlogComment, BlogTag
from .serializers import (
    BlogPostListSerializer,
    BlogPostDetailSerializer,
    BlogPostCreateUpdateSerializer,
    BlogCategorySerializer,
    BlogCommentSerializer,
    BlogCommentCreateSerializer,
    BlogTagSerializer
)


class BlogTagViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog tags
    """
    
    queryset = BlogTag.objects.filter(is_deleted=False)
    serializer_class = BlogTagSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def perform_create(self, serializer):
        """Set the created_by field when creating a tag"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set the updated_by field when updating a tag"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get all featured tags"""
        featured_tags = self.queryset.filter(is_featured=True)
        serializer = self.get_serializer(featured_tags, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all published posts with this tag"""
        tag = self.get_object()
        posts = BlogPost.objects.filter(
            tags=tag,
            status=BlogPost.StatusChoices.PUBLISHED,
            is_deleted=False
        ).order_by('-published_at')
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class BlogCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog categories
    """
    
    queryset = BlogCategory.objects.filter(is_deleted=False)
    serializer_class = BlogCategorySerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def perform_create(self, serializer):
        """Set the created_by field when creating a category"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set the updated_by field when updating a category"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def posts(self, request, pk=None):
        """Get all published posts in this category"""
        category = self.get_object()
        posts = BlogPost.objects.filter(
            category=category,
            status=BlogPost.StatusChoices.PUBLISHED,
            is_deleted=False
        ).order_by('-published_at')
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog posts
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'status', 'is_featured', 'author']
    search_fields = ['title', 'excerpt', 'content', 'tags']
    ordering_fields = ['title', 'published_at', 'created_at', 'views_count']
    ordering = ['-published_at', '-created_at']
    
    def get_queryset(self):
        """Get queryset based on user permissions"""
        queryset = BlogPost.objects.filter(is_deleted=False)
        
        # If user is not authenticated or not the author, only show published posts
        if not self.request.user.is_authenticated:
            queryset = queryset.filter(status=BlogPost.StatusChoices.PUBLISHED)
        elif not self.request.user.is_staff:
            # Non-staff users can only see their own posts or published posts
            queryset = queryset.filter(
                models.Q(author=self.request.user) |
                models.Q(status=BlogPost.StatusChoices.PUBLISHED)
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return BlogPostListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return BlogPostCreateUpdateSerializer
        return BlogPostDetailSerializer
    
    def perform_create(self, serializer):
        """Set the author and created_by fields when creating a post"""
        serializer.save(
            author=self.request.user,
            created_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set the updated_by field when updating a post"""
        serializer.save(updated_by=self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving a post"""
        instance = self.get_object()
        
        # Only increment views for published posts
        if instance.status == BlogPost.StatusChoices.PUBLISHED:
            instance.increment_views()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured blog posts"""
        posts = self.get_queryset().filter(
            is_featured=True,
            status=BlogPost.StatusChoices.PUBLISHED
        )[:6]
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent blog posts"""
        posts = self.get_queryset().filter(
            status=BlogPost.StatusChoices.PUBLISHED
        )[:10]
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def popular(self, request):
        """Get popular blog posts based on views"""
        posts = self.get_queryset().filter(
            status=BlogPost.StatusChoices.PUBLISHED
        ).order_by('-views_count')[:10]
        
        serializer = BlogPostListSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def comments(self, request, pk=None):
        """Get approved comments for a blog post"""
        post = self.get_object()
        comments = BlogComment.objects.filter(
            post=post,
            status=BlogComment.StatusChoices.APPROVED,
            is_visible=True,
            is_deleted=False,
            parent__isnull=True  # Only top-level comments
        ).order_by('created_at')
        
        serializer = BlogCommentSerializer(comments, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get blog statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_posts': queryset.count(),
            'published_posts': queryset.filter(status=BlogPost.StatusChoices.PUBLISHED).count(),
            'draft_posts': queryset.filter(status=BlogPost.StatusChoices.DRAFT).count(),
            'featured_posts': queryset.filter(is_featured=True).count(),
            'total_views': sum(post.views_count for post in queryset),
            'categories_count': BlogCategory.objects.filter(is_visible=True, is_deleted=False).count(),
        }
        
        return Response(stats)


class BlogCommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing blog comments
    """
    
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'status', 'parent']
    ordering_fields = ['created_at']
    ordering = ['created_at']
    
    def get_queryset(self):
        """Get queryset based on user permissions"""
        queryset = BlogComment.objects.filter(is_deleted=False)
        user = self.request.user

        if not user.is_authenticated:
            return queryset.none()
        
        # Non-staff users can only see approved comments or their own comments
        if not user.is_staff:
            queryset = queryset.filter(
                models.Q(author=user) |
                models.Q(status=BlogComment.StatusChoices.APPROVED)
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'create':
            return BlogCommentCreateSerializer
        return BlogCommentSerializer
    
    def perform_create(self, serializer):
        """Set the author and created_by fields when creating a comment"""
        serializer.save(
            author=self.request.user,
            created_by=self.request.user
        )
    
    def perform_update(self, serializer):
        """Set the updated_by field when updating a comment"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a comment (staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment = self.get_object()
        comment.status = BlogComment.StatusChoices.APPROVED
        comment.save()
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a comment (staff only)"""
        if not request.user.is_staff:
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        comment = self.get_object()
        comment.status = BlogComment.StatusChoices.REJECTED
        comment.save()
        
        serializer = self.get_serializer(comment)
        return Response(serializer.data)
