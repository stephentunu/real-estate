from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import TeamMember, TeamDepartment, TeamAchievement


@admin.register(TeamDepartment)
class TeamDepartmentAdmin(admin.ModelAdmin):
    """
    Admin configuration for TeamDepartment model
    """
    
    list_display = [
        'name', 'description_short', 'member_count', 
        'visibility_level'
    ]
    list_filter = ['visibility_level', 'is_deleted']
    search_fields = ['name', 'description']
    readonly_fields = []
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description')
        }),
        ('Visibility', {
            'fields': ('visibility_level', 'visibility_groups', 'visibility_users')
        }),
        ('Metadata', {
            'fields': (),
            'classes': ('collapse',)
        })
    )
    
    def description_short(self, obj):
        """Return truncated description"""
        if obj.description:
            return obj.description[:50] + '...' if len(obj.description) > 50 else obj.description
        return '-'
    description_short.short_description = 'Description'
    
    def member_count(self, obj):
        """Return count of active members in department"""
        count = obj.members.filter(is_active=True, is_deleted=False).count()
        if count > 0:
            url = reverse('admin:team_teammember_changelist') + f'?department__id__exact={obj.id}'
            return format_html('<a href="{}">{} members</a>', url, count)
        return '0 members'
    member_count.short_description = 'Active Members'
    

    
    actions = ['make_public', 'make_private']
    
    def make_public(self, request, queryset):
        """Make selected departments public"""
        updated = queryset.update(visibility_level='public')
        self.message_user(request, f'{updated} departments marked as public.')
    make_public.short_description = 'Mark selected departments as public'
    
    def make_private(self, request, queryset):
        """Make selected departments private"""
        updated = queryset.update(visibility_level='private')
        self.message_user(request, f'{updated} departments marked as private.')
    make_private.short_description = 'Mark selected departments as private'


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    """
    Admin configuration for TeamMember model
    """
    
    list_display = [
        'full_name', 'position_display', 'department', 'email', 
        'is_active', 'is_featured', 'hire_date', 'display_order'
    ]
    list_filter = [
        'department', 'position', 'is_active', 'is_featured', 
        'visibility_level', 'is_deleted', 'hire_date', 'created_at'
    ]
    search_fields = ['first_name', 'last_name', 'email', 'phone', 'bio', 'custom_position']
    readonly_fields = [
        'created_at', 'updated_at', 
        'full_name_display', 'profile_image_preview'
    ]
    
    fieldsets = (
        ('Personal Information', {
            'fields': (
                'first_name', 'last_name', 'full_name_display',
                'email', 'phone', 'profile_image', 'profile_image_preview'
            )
        }),
        ('Professional Information', {
            'fields': (
                'department', 'position', 'custom_position', 
                'hire_date', 'bio', 'display_order'
            )
        }),
        ('Social Links', {
            'fields': ('linkedin_url', 'twitter_url', 'github_url'),
            'classes': ('collapse',)
        }),
        ('Status', {
            'fields': ('is_active', 'is_featured', 'visibility_level')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def full_name_display(self, obj):
        """Display full name as read-only field"""
        return obj.full_name
    full_name_display.short_description = 'Full Name'
    
    def profile_image_preview(self, obj):
        """Display profile image preview"""
        if obj.profile_image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px; border-radius: 50%;" />',
                obj.profile_image.url
            )
        return 'No image'
    profile_image_preview.short_description = 'Profile Image Preview'
    
    def position_display(self, obj):
        """Display position with custom position if available"""
        if obj.custom_position:
            return f"{obj.get_position_display()} ({obj.custom_position})"
        return obj.get_position_display()
    position_display.short_description = 'Position'
    

    
    actions = ['make_active', 'make_inactive', 'make_featured', 'remove_featured']
    
    def make_active(self, request, queryset):
        """Make selected members active"""
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} members marked as active.')
    make_active.short_description = 'Mark selected members as active'
    
    def make_inactive(self, request, queryset):
        """Make selected members inactive"""
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} members marked as inactive.')
    make_inactive.short_description = 'Mark selected members as inactive'
    
    def make_featured(self, request, queryset):
        """Make selected members featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} members marked as featured.')
    make_featured.short_description = 'Mark selected members as featured'
    
    def remove_featured(self, request, queryset):
        """Remove featured status from selected members"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} members removed from featured.')
    remove_featured.short_description = 'Remove featured status from selected members'


@admin.register(TeamAchievement)
class TeamAchievementAdmin(admin.ModelAdmin):
    """
    Admin configuration for TeamAchievement model
    """
    
    list_display = [
        'title', 'member_name', 'date_achieved', 
        'is_featured', 'visibility_level', 'created_at'
    ]
    list_filter = [
        'is_featured', 'visibility_level', 'is_deleted', 
        'date_achieved', 'created_at', 'team_members__department'
    ]
    search_fields = ['title', 'description', 'team_members__first_name', 'team_members__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Achievement Information', {
            'fields': ('title', 'description', 'date_achieved', 'team_members')
        }),
        ('Status', {
            'fields': ('is_featured', 'visibility_level')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def member_name(self, obj):
        """Return formatted member names with links to member admin"""
        members = obj.team_members.all()[:3]  # Show first 3 members
        if members:
            links = []
            for member in members:
                url = reverse('admin:team_teammember_change', args=[member.pk])
                links.append(format_html('<a href="{}">{}</a>', url, member.full_name))
            result = ', '.join(links)
            if obj.team_members.count() > 3:
                result += f' (+{obj.team_members.count() - 3} more)'
            return mark_safe(result)
        return '-'
    member_name.short_description = 'Team Members'
    

    
    actions = ['make_featured', 'remove_featured', 'make_public', 'make_private']
    
    def make_featured(self, request, queryset):
        """Mark selected achievements as featured"""
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} achievements marked as featured.')
    make_featured.short_description = 'Mark selected achievements as featured'
    
    def remove_featured(self, request, queryset):
        """Remove featured status from selected achievements"""
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} achievements no longer featured.')
    remove_featured.short_description = 'Remove featured status from selected achievements'
    
    def make_public(self, request, queryset):
        """Make selected achievements public"""
        updated = queryset.update(visibility_level='public')
        self.message_user(request, f'{updated} achievements marked as public.')
    make_public.short_description = 'Mark selected achievements as public'
    
    def make_private(self, request, queryset):
        """Make selected achievements private"""
        updated = queryset.update(visibility_level='private')
        self.message_user(request, f'{updated} achievements marked as private.')
    make_private.short_description = 'Mark selected achievements as private'
