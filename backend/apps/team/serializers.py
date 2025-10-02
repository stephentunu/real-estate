from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import TeamMember, TeamDepartment, TeamAchievement

User = get_user_model()


class TeamDepartmentSerializer(serializers.ModelSerializer):
    """
    Serializer for team departments
    """
    
    members_count = serializers.ReadOnlyField()
    
    class Meta:
        model = TeamDepartment
        fields = [
            'id', 'name', 'description', 'color',
            'members_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'members_count']


class TeamMemberListSerializer(serializers.ModelSerializer):
    """
    Serializer for team member list view
    """
    
    department = TeamDepartmentSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    display_position = serializers.ReadOnlyField()
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email',
            'position', 'custom_position', 'display_position',
            'department', 'profile_image', 'is_active', 'is_featured',
            'display_order', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'display_position', 'created_at', 'updated_at'
        ]


class TeamMemberDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for team member detail view
    """
    
    department = TeamDepartmentSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    display_position = serializers.ReadOnlyField()
    achievements_count = serializers.SerializerMethodField()
    
    class Meta:
        model = TeamMember
        fields = [
            'id', 'first_name', 'last_name', 'full_name', 'email', 'phone',
            'position', 'custom_position', 'display_position', 'department',
            'bio', 'profile_image', 'hire_date', 'is_active', 'is_featured',
            'linkedin_url', 'twitter_url', 'github_url', 'website_url',
            'display_order', 'achievements_count', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'full_name', 'display_position', 'achievements_count',
            'created_at', 'updated_at'
        ]
    
    def get_achievements_count(self, obj):
        """Get the number of achievements for this team member"""
        return obj.achievements.filter(is_deleted=False).count()


class TeamMemberCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating team members
    """
    
    class Meta:
        model = TeamMember
        fields = [
            'first_name', 'last_name', 'email', 'phone',
            'position', 'custom_position', 'department', 'bio',
            'profile_image', 'hire_date', 'is_active', 'is_featured',
            'linkedin_url', 'twitter_url', 'github_url', 'website_url',
            'display_order'
        ]
    
    def validate_first_name(self, value):
        """Validate first name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "First name must be at least 2 characters long."
            )
        return value.strip().title()
    
    def validate_last_name(self, value):
        """Validate last name"""
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Last name must be at least 2 characters long."
            )
        return value.strip().title()
    
    def validate_email(self, value):
        """Validate email uniqueness"""
        # Check if email already exists (excluding current instance during update)
        queryset = TeamMember.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError(
                "A team member with this email already exists."
            )
        
        return value.lower()
    
    def validate(self, attrs):
        """Validate the team member data"""
        position = attrs.get('position')
        custom_position = attrs.get('custom_position')
        
        # If position is 'other', custom_position is required
        if position == TeamMember.PositionChoices.OTHER and not custom_position:
            raise serializers.ValidationError({
                'custom_position': 'Custom position is required when position is set to "Other".'
            })
        
        # If position is not 'other', custom_position should be empty
        if position != TeamMember.PositionChoices.OTHER and custom_position:
            raise serializers.ValidationError({
                'custom_position': 'Custom position should only be set when position is "Other".'
            })
        
        return attrs


class TeamAchievementSerializer(serializers.ModelSerializer):
    """
    Serializer for team achievements
    """
    
    team_members = TeamMemberListSerializer(many=True, read_only=True)
    members_count = serializers.ReadOnlyField()
    
    class Meta:
        model = TeamAchievement
        fields = [
            'id', 'title', 'description', 'date_achieved',
            'team_members', 'members_count', 'image', 'is_featured',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'team_members', 'members_count', 'created_at', 'updated_at'
        ]


class TeamAchievementCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating team achievements
    """
    
    team_members = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=TeamMember.objects.filter(is_active=True, is_deleted=False),
        required=False
    )
    
    class Meta:
        model = TeamAchievement
        fields = [
            'title', 'description', 'date_achieved',
            'team_members', 'image', 'is_featured'
        ]
    
    def validate_title(self, value):
        """Validate achievement title"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError(
                "Title must be at least 5 characters long."
            )
        return value.strip()
    
    def validate_description(self, value):
        """Validate achievement description"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Description must be at least 10 characters long."
            )
        return value.strip()


class TeamStatsSerializer(serializers.Serializer):
    """
    Serializer for team statistics
    """
    
    total_members = serializers.IntegerField()
    active_members = serializers.IntegerField()
    inactive_members = serializers.IntegerField()
    featured_members = serializers.IntegerField()
    departments_count = serializers.IntegerField()
    achievements_count = serializers.IntegerField()
    positions_breakdown = serializers.DictField()
    departments_breakdown = serializers.DictField()