from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TeamMemberViewSet, TeamDepartmentViewSet, TeamAchievementViewSet

app_name = 'team'

# Create router and register viewsets
router = DefaultRouter()
router.register(r'members', TeamMemberViewSet, basename='member')
router.register(r'departments', TeamDepartmentViewSet, basename='department')
router.register(r'achievements', TeamAchievementViewSet, basename='achievement')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Custom endpoints for team functionality
    path('members/featured/', TeamMemberViewSet.as_view({'get': 'featured'}), name='members-featured'),
    path('members/leadership/', TeamMemberViewSet.as_view({'get': 'leadership'}), name='members-leadership'),
    path('members/by-department/', TeamMemberViewSet.as_view({'get': 'by_department'}), name='members-by-department'),
    path('members/stats/', TeamMemberViewSet.as_view({'get': 'stats'}), name='members-stats'),
    
    # Department-specific endpoints
    path('departments/<int:pk>/members/', TeamDepartmentViewSet.as_view({'get': 'members'}), name='department-members'),
    
    # Achievement-specific endpoints
    path('achievements/featured/', TeamAchievementViewSet.as_view({'get': 'featured'}), name='achievements-featured'),
    path('achievements/recent/', TeamAchievementViewSet.as_view({'get': 'recent'}), name='achievements-recent'),
    
    # Member-specific endpoints
    path('members/<int:pk>/achievements/', TeamMemberViewSet.as_view({'get': 'achievements'}), name='member-achievements'),
]