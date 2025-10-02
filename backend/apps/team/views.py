from django.shortcuts import render
from django.db.models import Count, Q
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from apps.core.permissions import IsOwnerOrReadOnly
from .models import TeamMember, TeamDepartment, TeamAchievement
from .serializers import (
    TeamMemberListSerializer,
    TeamMemberDetailSerializer,
    TeamMemberCreateUpdateSerializer,
    TeamDepartmentSerializer,
    TeamAchievementSerializer,
    TeamAchievementCreateUpdateSerializer,
    TeamStatsSerializer
)


class TeamDepartmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing team departments
    """
    
    queryset = TeamDepartment.objects.filter(is_deleted=False)
    serializer_class = TeamDepartmentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def perform_create(self, serializer):
        """Set the created_by field when creating a department"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set the updated_by field when updating a department"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=True, methods=['get'])
    def members(self, request, pk=None):
        """Get all active members in this department"""
        department = self.get_object()
        members = TeamMember.objects.filter(
            department=department,
            is_active=True,
            is_deleted=False
        ).order_by('display_order', 'first_name', 'last_name')
        
        serializer = TeamMemberListSerializer(members, many=True, context={'request': request})
        return Response(serializer.data)


class TeamMemberViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing team members
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['department', 'position', 'is_active', 'is_featured']
    search_fields = ['first_name', 'last_name', 'position', 'custom_position', 'bio']
    ordering_fields = ['first_name', 'last_name', 'position', 'hire_date', 'display_order']
    ordering = ['display_order', 'first_name', 'last_name']
    
    def get_queryset(self):
        """Get queryset based on user permissions"""
        queryset = TeamMember.objects.filter(is_deleted=False)
        
        # Non-staff users can only see active members
        if not self.request.user.is_authenticated or not self.request.user.is_staff:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return TeamMemberListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return TeamMemberCreateUpdateSerializer
        return TeamMemberDetailSerializer
    
    def perform_create(self, serializer):
        """Set the created_by field when creating a team member"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set the updated_by field when updating a team member"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured team members"""
        members = self.get_queryset().filter(
            is_featured=True,
            is_active=True
        )[:6]
        
        serializer = TeamMemberListSerializer(members, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def leadership(self, request):
        """Get leadership team members (CEO, CTO, CFO, Managers)"""
        leadership_positions = [
            TeamMember.PositionChoices.CEO,
            TeamMember.PositionChoices.CTO,
            TeamMember.PositionChoices.CFO,
            TeamMember.PositionChoices.MANAGER
        ]
        
        members = self.get_queryset().filter(
            position__in=leadership_positions,
            is_active=True
        ).order_by('display_order', 'first_name')
        
        serializer = TeamMemberListSerializer(members, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_department(self, request):
        """Get team members grouped by department"""
        departments = TeamDepartment.objects.filter(
            is_visible=True,
            is_deleted=False
        ).prefetch_related('members')
        
        result = []
        for department in departments:
            members = department.members.filter(
                is_active=True,
                is_visible=True,
                is_deleted=False
            ).order_by('display_order', 'first_name', 'last_name')
            
            if members.exists():
                result.append({
                    'department': TeamDepartmentSerializer(department, context={'request': request}).data,
                    'members': TeamMemberListSerializer(members, many=True, context={'request': request}).data
                })
        
        # Add members without department
        members_without_dept = self.get_queryset().filter(
            department__isnull=True,
            is_active=True
        ).order_by('display_order', 'first_name', 'last_name')
        
        if members_without_dept.exists():
            result.append({
                'department': {'name': 'Other', 'description': 'Members without specific department'},
                'members': TeamMemberListSerializer(members_without_dept, many=True, context={'request': request}).data
            })
        
        return Response(result)
    
    @action(detail=True, methods=['get'])
    def achievements(self, request, pk=None):
        """Get achievements for a specific team member"""
        member = self.get_object()
        achievements = member.achievements.filter(
            is_visible=True,
            is_deleted=False
        ).order_by('-date_achieved')
        
        serializer = TeamAchievementSerializer(achievements, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get team statistics"""
        queryset = self.get_queryset()
        
        # Basic counts
        total_members = queryset.count()
        active_members = queryset.filter(is_active=True).count()
        inactive_members = queryset.filter(is_active=False).count()
        featured_members = queryset.filter(is_featured=True).count()
        
        # Department and position breakdowns
        departments_breakdown = {}
        departments = TeamDepartment.objects.filter(is_visible=True, is_deleted=False)
        for dept in departments:
            count = queryset.filter(department=dept, is_active=True).count()
            if count > 0:
                departments_breakdown[dept.name] = count
        
        # Members without department
        no_dept_count = queryset.filter(department__isnull=True, is_active=True).count()
        if no_dept_count > 0:
            departments_breakdown['Other'] = no_dept_count
        
        # Position breakdown
        positions_breakdown = {}
        for position_choice in TeamMember.PositionChoices.choices:
            count = queryset.filter(position=position_choice[0], is_active=True).count()
            if count > 0:
                positions_breakdown[position_choice[1]] = count
        
        stats = {
            'total_members': total_members,
            'active_members': active_members,
            'inactive_members': inactive_members,
            'featured_members': featured_members,
            'departments_count': len(departments_breakdown),
            'achievements_count': TeamAchievement.objects.filter(
                is_visible=True, is_deleted=False
            ).count(),
            'positions_breakdown': positions_breakdown,
            'departments_breakdown': departments_breakdown,
        }
        
        serializer = TeamStatsSerializer(stats)
        return Response(serializer.data)


class TeamAchievementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing team achievements
    """
    
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_featured', 'date_achieved']
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'date_achieved', 'created_at']
    ordering = ['-date_achieved']
    
    def get_queryset(self):
        """Get queryset for team achievements"""
        return TeamAchievement.objects.filter(is_deleted=False)
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action in ['create', 'update', 'partial_update']:
            return TeamAchievementCreateUpdateSerializer
        return TeamAchievementSerializer
    
    def perform_create(self, serializer):
        """Set the created_by field when creating an achievement"""
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        """Set the updated_by field when updating an achievement"""
        serializer.save(updated_by=self.request.user)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured achievements"""
        achievements = self.get_queryset().filter(is_featured=True)[:6]
        
        serializer = TeamAchievementSerializer(achievements, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent achievements"""
        achievements = self.get_queryset()[:10]
        
        serializer = TeamAchievementSerializer(achievements, many=True, context={'request': request})
        return Response(serializer.data)
