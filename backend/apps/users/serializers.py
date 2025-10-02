from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic serializer for User model with minimal fields
    Used for references in other models
    """
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'email', 'full_name', 'avatar', 'role']
        read_only_fields = ['id', 'email', 'full_name', 'avatar', 'role']
    
    def get_full_name(self, obj):
        """
        Get user's full name from profile if available
        """
        if hasattr(obj, 'profile') and obj.profile:
            first_name = obj.profile.first_name or ''
            last_name = obj.profile.last_name or ''
            full_name = f"{first_name} {last_name}".strip()
            return full_name if full_name else obj.email.split('@')[0]
        return obj.email.split('@')[0]


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model
    """
    class Meta:
        model = UserProfile
        fields = [
            'id', 'address_line_1', 'address_line_2', 'city', 'state', 
            'postal_code', 'country', 'company_name', 'license_number',
            'years_experience', 'website', 'linkedin_url', 'twitter_url',
            'preferred_language', 'timezone', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model with profile information
    """
    profile = UserProfileSerializer(read_only=True)
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            'id', 'email', 'phone_number', 'role', 'avatar', 'bio',
            'email_verified', 'is_active', 'is_staff', 'is_superuser',
            'date_joined', 'last_login', 'profile', 'password', 'password_confirm'
        ]
        read_only_fields = [
            'id', 'email_verified', 'is_staff', 'is_superuser',
            'date_joined', 'last_login'
        ]
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def validate(self, attrs):
        """
        Validate password confirmation
        """
        if 'password' in attrs and 'password_confirm' in attrs:
            if attrs['password'] != attrs['password_confirm']:
                raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        """
        Create user with encrypted password
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password')
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        """
        Update user instance
        """
        validated_data.pop('password_confirm', None)
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    user_role = serializers.ChoiceField(choices=User.UserRole.choices, required=False, default='buyer')

    class Meta:
        model = User
        fields = ['email', 'phone_number', 'role', 'password', 'password_confirm', 'first_name', 'last_name', 'user_role']

    def validate(self, attrs):
        """
        Validate password confirmation
        """
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Passwords don't match.")
        return attrs

    def create(self, validated_data):
        """
        Create user with encrypted password and profile
        """
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        first_name = validated_data.pop('first_name', '')
        last_name = validated_data.pop('last_name', '')
        user_role = validated_data.pop('user_role', 'buyer')
        
        # Set role from user_role if role is not provided
        if 'role' not in validated_data:
            validated_data['role'] = user_role
        
        # Set username to email since USERNAME_FIELD is 'email'
        # but Django still requires username in REQUIRED_FIELDS
        if 'username' not in validated_data:
            validated_data['username'] = validated_data['email']
        
        # Set first_name and last_name for User model
        validated_data['first_name'] = first_name
        validated_data['last_name'] = last_name
        
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        
        # Create user profile (first_name and last_name are stored in User model)
        UserProfile.objects.create(user=user)
        
        return user


class UserLoginSerializer(serializers.Serializer):
    """
    Serializer for user login
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        """
        Validate user credentials
        """
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')
        
        return attrs


class UserProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile information
    """
    class Meta:
        model = UserProfile
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'gender',
            'address', 'city', 'state', 'postal_code', 'country',
            'company_name', 'job_title', 'years_of_experience',
            'linkedin_url', 'twitter_url', 'facebook_url', 'instagram_url',
            'website_url', 'language_preference', 'timezone',
            'marketing_emails', 'push_notifications', 'sms_notifications'
        ]


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change
    """
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
    new_password_confirm = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        """
        Validate old password
        """
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value

    def validate(self, attrs):
        """
        Validate new password confirmation
        """
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError("New passwords don't match.")
        return attrs

    def save(self):
        """
        Save new password
        """
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user