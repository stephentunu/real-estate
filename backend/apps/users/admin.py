from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        ('address_line_1', 'address_line_2'),
        ('city', 'state', 'postal_code'),
        'country',
        ('company_name', 'license_number'),
        'years_experience',
        ('website', 'linkedin_url', 'twitter_url'),
        ('preferred_language', 'timezone'),
    )


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Custom User admin with enhanced functionality
    """
    inlines = (UserProfileInline,)
    
    list_display = (
        'email', 'get_full_name', 'role', 'is_active', 
        'email_verified', 'date_joined', 'last_login'
    )
    list_filter = (
        'role', 'is_active', 'is_staff', 'is_superuser',
        'email_verified', 'date_joined'
    )
    search_fields = ('email', 'first_name', 'last_name', 'username')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {
            'fields': ('username', 'email', 'password')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'avatar', 'bio')
        }),
        ('Role & Status', {
            'fields': ('role', 'is_active', 'email_verified', 'email_verified_at')
        }),
        ('Permissions', {
            'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions'),
            'classes': ('collapse',)
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'last_login', 'date_joined')
    
    actions = ['verify_email', 'unverify_email', 'activate_users', 'deactivate_users']
    
    def verify_email(self, request, queryset):
        """
        Mark selected users' emails as verified
        """
        from django.utils import timezone
        updated = queryset.update(email_verified=True, email_verified_at=timezone.now())
        self.message_user(request, f'{updated} users marked as email verified.')
    verify_email.short_description = "Mark selected users as email verified"
    
    def unverify_email(self, request, queryset):
        """
        Mark selected users' emails as unverified
        """
        updated = queryset.update(email_verified=False, email_verified_at=None)
        self.message_user(request, f'{updated} users marked as email unverified.')
    unverify_email.short_description = "Mark selected users as email unverified"
    
    def activate_users(self, request, queryset):
        """
        Activate selected users
        """
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} users activated.')
    activate_users.short_description = "Activate selected users"
    
    def deactivate_users(self, request, queryset):
        """
        Deactivate selected users
        """
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} users deactivated.')
    deactivate_users.short_description = "Deactivate selected users"


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Standalone UserProfile admin
    """
    list_display = (
        'user', 'get_full_address', 'company_name', 
        'years_experience', 'preferred_language'
    )
    list_filter = ('country', 'state', 'city', 'preferred_language', 'timezone')
    search_fields = (
        'user__email', 'user__first_name', 'user__last_name',
        'company_name', 'city', 'state'
    )
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Address', {
            'fields': (
                ('address_line_1', 'address_line_2'),
                ('city', 'state', 'postal_code'),
                'country'
            )
        }),
        ('Professional Info', {
            'fields': (
                ('company_name', 'license_number'),
                'years_experience'
            )
        }),
        ('Social Links', {
            'fields': ('website', 'linkedin_url', 'twitter_url'),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('preferred_language', 'timezone')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at')
    
    def get_full_address(self, obj):
        return obj.get_full_address()
    get_full_address.short_description = 'Address'
