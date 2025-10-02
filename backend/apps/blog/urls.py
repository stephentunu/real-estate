from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BlogPostViewSet, BlogCategoryViewSet, BlogCommentViewSet, BlogTagViewSet

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'posts', BlogPostViewSet, basename='blogpost')
router.register(r'categories', BlogCategoryViewSet, basename='blogcategory')
router.register(r'comments', BlogCommentViewSet, basename='blogcomment')
router.register(r'tags', BlogTagViewSet, basename='blogtag')

# The API URLs are now determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    
    # Custom endpoints for blog functionality
    path('posts/featured/', BlogPostViewSet.as_view({'get': 'featured'}), name='blog-posts-featured'),
    path('posts/recent/', BlogPostViewSet.as_view({'get': 'recent'}), name='blog-posts-recent'),
    path('posts/popular/', BlogPostViewSet.as_view({'get': 'popular'}), name='blog-posts-popular'),
    path('posts/stats/', BlogPostViewSet.as_view({'get': 'stats'}), name='blog-posts-stats'),
    
    # Category specific endpoints
    path('categories/<int:pk>/posts/', BlogCategoryViewSet.as_view({'get': 'posts'}), name='blog-category-posts'),
    
    # Comment specific endpoints
    path('comments/<int:pk>/approve/', BlogCommentViewSet.as_view({'post': 'approve'}), name='blog-comment-approve'),
    path('comments/<int:pk>/reject/', BlogCommentViewSet.as_view({'post': 'reject'}), name='blog-comment-reject'),
]

app_name = 'blog'