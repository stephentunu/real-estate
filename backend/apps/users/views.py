from rest_framework import generics, status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import User, UserProfile
from .serializers import (
    UserSerializer, UserProfileSerializer, UserRegistrationSerializer,
    UserLoginSerializer, UserProfileUpdateSerializer, PasswordChangeSerializer
)


@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.save()
        
        # Create auth token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data with profile and token
        user_serializer = UserSerializer(user)
        profile_serializer = UserProfileSerializer(user.profile)
        return Response({
            'user': user_serializer.data,
            'profile': profile_serializer.data,
            'token': token.key,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)


@method_decorator(csrf_exempt, name='dispatch')
class UserLoginView(ObtainAuthToken):
    """
    API endpoint for user login
    """
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        user = serializer.validated_data['user']
        
        # Create or get auth token
        token, created = Token.objects.get_or_create(user=user)
        
        # Login user
        login(request, user)
        
        # Return user data with profile and token
        user_serializer = UserSerializer(user)
        
        # Ensure user has a profile (create if missing)
        if not hasattr(user, 'profile') or user.profile is None:
            from .models import UserProfile
            UserProfile.objects.create(user=user)
            user.refresh_from_db()
        
        profile_serializer = UserProfileSerializer(user.profile)
        return Response({
            'user': user_serializer.data,
            'profile': profile_serializer.data,
            'token': token.key,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)


class UserLogoutView(generics.GenericAPIView):
    """
    API endpoint for user logout
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, *args, **kwargs):
        try:
            # Delete the user's token
            request.user.auth_token.delete()
        except Token.DoesNotExist:
            pass
        
        # Logout user
        logout(request)
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)


class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user profiles
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Filter queryset based on user role
        """
        user = self.request.user
        if user.is_staff or user.is_superuser:
            return User.objects.all()
        return User.objects.filter(id=user.id)

    def get_object(self):
        """
        Get user object - allow 'me' as pk for current user
        """
        pk = self.kwargs.get('pk')
        if pk == 'me':
            return self.request.user
        return super().get_object()

    @action(detail=True, methods=['get', 'patch'], url_path='profile')
    def profile(self, request, pk=None):
        """
        Get or update user profile information
        """
        user = self.get_object()
        profile, created = UserProfile.objects.get_or_create(user=user)
        
        if request.method == 'GET':
            serializer = UserProfileSerializer(profile)
            return Response(serializer.data)
        
        elif request.method == 'PATCH':
            serializer = UserProfileUpdateSerializer(
                profile, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='change-password')
    def change_password(self, request, pk=None):
        """
        Change user password
        """
        user = self.get_object()
        
        # Ensure user can only change their own password
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only change your own password'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='upload-avatar')
    def upload_avatar(self, request, pk=None):
        """
        Upload user avatar
        """
        user = self.get_object()
        
        # Ensure user can only upload their own avatar
        if user != request.user and not request.user.is_staff:
            return Response(
                {'error': 'You can only upload your own avatar'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if 'avatar' not in request.FILES:
            return Response(
                {'error': 'No avatar file provided'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.avatar = request.FILES['avatar']
        user.save()
        
        serializer = UserSerializer(user)
        return Response({
            'user': serializer.data,
            'message': 'Avatar uploaded successfully'
        }, status=status.HTTP_200_OK)


class CurrentUserView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for current user information
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserListView(generics.ListAPIView):
    """
    API endpoint for listing users (admin only)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """
        Filter users based on query parameters
        """
        queryset = User.objects.all()
        role = self.request.query_params.get('role')
        is_active = self.request.query_params.get('is_active')
        
        if role:
            queryset = queryset.filter(role=role)
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('-date_joined')
