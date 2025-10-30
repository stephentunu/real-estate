from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'profiles', views.UserProfileViewSet, basename='user-profile')

urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Authentication endpoints
    path('register/', views.UserRegistrationView.as_view(), name='user-register'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),
    
    # User management endpoints
    path('me/', views.CurrentUserView.as_view(), name='current-user'),
    path('list/', views.UserListView.as_view(), name='user-list'),
    path("health/", views.healt_check, name="healt_chec")
]